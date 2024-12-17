from typing import Iterable
from typing import Optional

from qbittorrentapi import Client

from . import Storage
from ..utils import File
from ..utils import Readable


class QBittorrentStorage(Storage):
    def __init__(
        self,
        host: str,
        port: int = 8080,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self._client = Client(host, port, username, password)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for torrent in self._client.torrents_info():
            for file in torrent.files:
                yield File(file.name, size=file.size)

    def _get_file(self, file: File) -> Readable:
        raise NotImplementedError

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
