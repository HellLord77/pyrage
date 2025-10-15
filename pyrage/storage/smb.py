from ntpath import relpath, sep
from pathlib import PureWindowsPath
from shutil import copyfileobj
from typing import Iterable, Optional

from smbclient import makedirs, open_file, register_session, remove, scandir

from ..utils import File, Readable
from . import Storage


class SMBStorage(Storage):
    def __init__(
        self,
        server: str,
        share: str,
        port: int = 445,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        register_session(server, username, password, port)
        self._path = PureWindowsPath(f"{sep}{sep}{server}{sep}", share)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        paths = [self._path]
        while paths:
            for dir_ in scandir(paths.pop(0)):
                if dir_.is_dir():
                    paths.append(dir_.path)
                else:
                    yield File(
                        relpath(dir_.path, self._path), **File.get_stat(dir_.stat())
                    )

    def _get_file(self, file: File) -> Readable:
        return open_file(self._path / file.path, "rb")

    def _set_file(self, file: File, readable: Readable):
        path = self._path / file.path
        makedirs(path.parent, exist_ok=True)
        with open_file(path, "wb") as file:
            copyfileobj(readable, file)

    def _del_file(self, file: File):
        remove(self._path / file.path)
