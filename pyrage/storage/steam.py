from pathlib import Path
from pathlib import PureWindowsPath
from typing import Iterable
from typing import Optional

from steam.client import SteamClient
from steam.client.cdn import CDNClient

from . import Storage
from ..utils import File
from ..utils import Readable


class SteamStorage(Storage):
    def __init__(self, app_id: int, username: Optional[str] = None, password: Optional[str] = None, ):
        self._app_id = app_id
        client = SteamClient()
        if username is None:
            client.anonymous_login()
        else:
            client.login(username, password)
        self._client = CDNClient(client)
        self._client.load_licenses()
        if app_id not in self._client.licensed_app_ids:
            raise NotImplementedError
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for file in self._client.iter_files(self._app_id):
            if file.is_file:
                yield File(Path(file.filename).as_posix(), size=file.size, sha1=file.sha_content.hex())

    def _get_file(self, file: File) -> Readable:
        return next(self._client.iter_files(self._app_id), PureWindowsPath(file.path))

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
