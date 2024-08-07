from ntpath import relpath
from ntpath import sep
from pathlib import PureWindowsPath
from shutil import copyfileobj
from typing import Iterable
from typing import Optional

from smbclient import makedirs
from smbclient import open_file
from smbclient import register_session
from smbclient import remove
from smbclient import scandir

from . import Storage
from ..utils import File
from ..utils import Readable


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
        self._path = PureWindowsPath(sep + sep + server + sep, share)
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
        return open_file(self._path.joinpath(file.path), "rb")

    def _set_file(self, file: File, readable: Readable):
        path = self._path.joinpath(file.path)
        makedirs(path.parent, exist_ok=True)
        with open_file(path, "wb") as file:
            copyfileobj(readable, file)

    def _del_file(self, file: File):
        remove(self._path.joinpath(file.path))
