from .gen.File import File as File_
from typing import Iterable
from typing import Iterator
from .. import FileListCache
from .....utils import File

class FlatFileListCache(FileListCache):
    EXTENSION = "bin"

    def _dump(self, files: Iterable[File]):
        with open(self.path, "wb") as cache:
            raise NotImplementedError

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            raise NotImplementedError