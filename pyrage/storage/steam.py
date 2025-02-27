from functools import cache
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Iterable
from typing import Optional

from steam.client import SteamClient
from steam.client.cdn import CDNClient

from . import Storage
from ..config import STEAM_CACHE_MANIFESTS
from ..utils import File
from ..utils import Readable


class SteamStorage(Storage):
    def __init__(
        self,
        app_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        steam = SteamClient()
        if username is None:
            steam.anonymous_login()
        else:
            steam.login(username, password)
        self._cdn = CDNClient(steam)
        self._cdn.load_licenses()
        if not self._cdn.has_license_for_depot(app_id):
            raise NotImplementedError
        self._app_id = app_id
        if STEAM_CACHE_MANIFESTS:
            self._cdn.get_manifests = cache(self._cdn.get_manifests)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for file in self._cdn.iter_files(self._app_id):
            if file.is_file:
                yield File(
                    Path(file.filename).as_posix(),
                    size=file.size,
                    sha1=file.sha_content.hex(),
                )

    def _get_file(self, file: File) -> Readable:
        return next(self._cdn.iter_files(self._app_id, PureWindowsPath(file.path)))

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
