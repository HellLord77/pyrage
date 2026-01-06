from collections.abc import Iterable
from tarfile import TarFile
from typing import BinaryIO

from ..utils import File
from ..utils import Readable
from . import Storage


class TarStorage(Storage):
    def __init__(self, file: str | BinaryIO):
        self._tar = TarFile(file) if isinstance(file, str) else TarFile(fileobj=file)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for info in self._tar.getmembers():
            if not info.isdir():
                yield File(info.name, size=info.size, mtime=info.mtime)

    def _get_file(self, file: File) -> Readable:
        return self._tar.extractfile(file.path)

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
