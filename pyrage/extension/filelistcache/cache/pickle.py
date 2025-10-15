from itertools import repeat, starmap
from pickle import dump, load
from typing import Iterator

from ....utils import File, consume
from . import FileListCache


class PickleFileListCache(FileListCache):
    EXTENSION = "pickle"

    def _dump(self, files: Iterator[File]):
        with open(self.path, "wb") as cache:
            dump(tuple(files), cache)

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            return load(cache)


class StreamingPickleFileListCache(PickleFileListCache):
    def _dump(self, files: Iterator[File]):
        with open(self.path, "wb") as cache:
            consume(dump(tuple(file), cache) for file in files)

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            try:
                yield from starmap(File, map(load, repeat(cache)))
            except EOFError:
                pass
