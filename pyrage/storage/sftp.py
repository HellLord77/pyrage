from posixpath import dirname
from posixpath import join
from posixpath import relpath
from posixpath import sep
from stat import S_ISDIR
from typing import Iterable
from typing import Optional

from paramiko import AutoAddPolicy
from paramiko import SFTPClient
from paramiko import SSHClient
from paramiko.config import SSH_PORT

from . import Storage
from ..config import SFTP_AUTO_ADD
from ..utils import File
from ..utils import Readable


def _makedirs(sftp: SFTPClient, path: str):
    try:
        sftp.stat(path)
    except FileNotFoundError:
        dir_, base = path.rsplit(sep, 1)
        _makedirs(sftp, dir_)
        sftp.mkdir(base)


class SFTPStorage(Storage):
    def __init__(
        self,
        hostname: str,
        port: int = SSH_PORT,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cwd: str = ".",
    ):
        client = SSHClient()
        client.load_system_host_keys()
        if SFTP_AUTO_ADD:
            client.set_missing_host_key_policy(AutoAddPolicy)
        client.connect(hostname, port, username, password)
        self._sftp = client.open_sftp()
        self._sftp.chdir(cwd)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        cwd = self._sftp.getcwd()
        paths = [cwd]
        while paths:
            prefix = paths.pop(0)
            for attr in self._sftp.listdir_attr(prefix):
                path = join(prefix, attr.filename)
                if S_ISDIR(attr.st_mode):
                    paths.append(path)
                else:
                    # noinspection PyTypeChecker
                    yield File(relpath(path, cwd), **File.stat(attr))

    def _get_file(self, file: File) -> Readable:
        return self._sftp.open(file.path, "rb")

    def _set_file(self, file: File, readable: Readable):
        _makedirs(self._sftp, dirname(file.path))
        # noinspection PyTypeChecker
        self._sftp.putfo(readable, file.path)

    def _del_file(self, file: File):
        self._sftp.remove(file.path)
