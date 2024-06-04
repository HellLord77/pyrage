from ftplib import FTP
from os.path import relpath
from shutil import copyfileobj
from typing import Optional

from ftputil import FTPHost

from pyrage.config import FTP_INCLUDE_HIDDEN
from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable


class _FTPPort(FTP):
    def __init__(
        self,
        host: str,
        user: Optional[str] = None,
        passwd: Optional[str] = None,
        port: int = 0,
    ):
        super().__init__()
        self.connect(host, port)
        self.login(user, passwd)


class FTPStorage(Storage):
    def __init__(
        self,
        host: str,
        port: int = 0,
        user: Optional[str] = None,
        passwd: Optional[str] = None,
        cwd: str = ".",
    ):
        self._ftp = FTPHost(host, user, passwd, port, session_factory=_FTPPort)
        self._ftp.use_list_a_option = FTP_INCLUDE_HIDDEN
        self._ftp.chdir(cwd)
        super().__init__()

    def get_file_list(self) -> dict[str, File]:
        cwd = self._ftp.getcwd()
        paths = [cwd]
        while paths:
            prefix = paths.pop(0)
            for dir_ in self._ftp.listdir(prefix):
                path = prefix + self._ftp.sep + dir_
                if self._ftp.path.isdir(path):
                    paths.append(path)
                else:
                    stat = self._ftp.stat(path)
                    # noinspection PyArgumentList
                    self._add_file_list(
                        File(
                            relpath(path, cwd),
                            size=stat.st_size,
                            mtime=stat.st_mtime,
                            atime=stat.st_atime,
                            ctime=stat.st_ctime,
                        )
                    )
        return super().get_file_list()

    def _get_file(self, file: File) -> Readable:
        return self._ftp.open(self._ftp.getcwd() + self._ftp.sep + file.path, "rb")

    def _set_file(self, file: File, readable: Readable):
        path = self._ftp.getcwd() + self._ftp.sep + file.path
        self._ftp.makedirs(self._ftp.path.dirname(path), exist_ok=True)
        with self._ftp.open(path, "wb") as file:
            copyfileobj(readable, file)

    def _del_file(self, file: File):
        self._ftp.remove(self._ftp.getcwd() + self._ftp.sep + file.path)
