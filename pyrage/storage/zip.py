from datetime import datetime
from shutil import copyfileobj
from threading import Lock
from typing import BinaryIO, Iterable, Optional
from zipfile import ZipFile

from ..utils import CRC32Hash, File, Readable
from . import Storage


class ZipStorage(Storage):
    def __init__(self, file: str | BinaryIO, pwd: Optional[bytes] = None):
        self._zip = ZipFile(file, "a")
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
        with self._lock, self._zip.open(file.path, "w") as file_:
            copyfileobj(readable, file_)

    def _del_file(self, file: File):
        raise NotImplementedError
