from typing import Iterable, Iterator

from bson import decode, decode_file_iter, encode

from ....utils import File, consume
from . import FileListCache


class BSONFileListCache(FileListCache):
    EXTENSION = "bson"

    def _dump(self, files: Iterable[File]):
        with open(self.path, "wb") as cache:
            cache.write(encode({file.path: file[1:] for file in files}))

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            return (File(path, *file) for path, file in decode(cache.read()).items())


class CompatBSONFileListCache(BSONFileListCache):
    def _dump(self, files: Iterator[File]):
        with open(self.path, "wb") as cache:
            consume(cache.write(encode(file._asdict())) for file in files)

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            yield from (File(**file) for file in decode_file_iter(cache))
