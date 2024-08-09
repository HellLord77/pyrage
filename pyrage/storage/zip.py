from datetime import datetime
from shutil import copyfileobj
from threading import Lock
from typing import Iterable
from typing import Optional
from zipfile import ZipFile

from . import Storage
from ..utils import CRC32Hash
from ..utils import File
from ..utils import Readable


class ZipStorage(Storage):
    def __init__(self, path: str, pwd: Optional[bytes] = None):
        self._zip = ZipFile(path, "a")
        self._zip.setpassword(pwd)
        self._lock = Lock()
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for info in self._zip.filelist:
            if not info.is_dir():
                yield File(
                    info.filename,
                    size=info.file_size,
                    mtime=datetime(*info.date_time).timestamp(),
                    crc32=CRC32Hash(value=info.CRC).hexdigest(),
                )

    def _get_file(self, file: File) -> Readable:
        return self._zip.open(file.path)

    def _set_file(self, file: File, readable: Readable):
        with self._lock, self._zip.open(file.path, "w") as file:
            copyfileobj(readable, file)

    def _del_file(self, file: File):
        raise NotImplementedError
