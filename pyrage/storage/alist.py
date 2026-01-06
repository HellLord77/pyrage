from collections.abc import Iterable

from alist import AlistClient
from alist import AlistFileSystem

from ..utils import File
from ..utils import Readable
from . import Storage


class AListStorage(Storage):
    def __init__(
        self,
        base_url: str,
        username: str = "",
        password: str = "",
        otp_code: int | str = "",
    ):
        client = AlistClient(base_url, username, password, otp_code)
        self._fs = AlistFileSystem(client)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        root = self._fs.getcwd()
        for dir_ in self._fs.rglob():
            if dir_.hash_info is not None:
                raise NotImplementedError
            if not dir_.is_dir():
                yield File(dir_.relative_to(root), **File.get_stat(dir_.stat()))

    def _get_file(self, file: File) -> Readable:
        return self._fs.open(file.path, "rb")

    def _set_file(self, file: File, readable: Readable):
        self._fs.upload(readable, file.path)

    def _del_file(self, file: File):
        self._fs.unlink(file.path)
