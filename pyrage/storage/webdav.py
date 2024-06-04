from typing import Optional
from urllib.parse import urlparse

from webdav3.client import Client
from webdav3.urn import Urn

from pyrage.config import WEBDAV_DISABLE_CHECK
from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable
from pyrage.utils import ReadableResponse


class WebDAVStorage(Storage):
    def __init__(
        self, hostname: str, login: Optional[str] = None, password: Optional[str] = None
    ):
        self._client = Client(
            {
                "webdav_hostname": hostname,
                "webdav_login": login,
                "webdav_password": password,
                "webdav_disable_check": WEBDAV_DISABLE_CHECK,
            }
        )
        self._client.verify = "https" == urlparse(hostname).scheme
        super().__init__()

    def get_file_list(self) -> dict[str, File]:
        paths = [self._client.root]
        while paths:
            for info in self._client.list(paths.pop(0), True):
                if info["isdir"]:
                    paths.append(info["path"])
                else:
                    # noinspection PyArgumentList
                    self._add_file_list(
                        File(
                            info["path"].removeprefix(self._client.root),
                            size=int(info["size"]),
                        )
                    )
        return super().get_file_list()

    def __get_file_list(self) -> dict[str, File]:
        roots = [self._client.root]
        while roots:
            root = roots.pop(0)
            for name in self._client.list(root):
                path = root + name
                if path:
                    roots.append(path)
                else:
                    # noinspection PyArgumentList
                    self._add_file_list(
                        File(
                            path.removeprefix(self._client.root),
                            size=int(self._client.info(path)["size"]),
                        )
                    )
        return super().get_file_list()

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._client.execute_request(
                action="download", path=Urn(self._client.root + file.path).quote()
            )
        )

    def _set_file(self, file: File, readable: Readable):
        self._client.upload_to(readable, self._client.root + file.path)

    def _del_file(self, file: File):
        self._client.clean(self._client.root + file.path)
