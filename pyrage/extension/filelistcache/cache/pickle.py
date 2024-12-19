from itertools import repeat
from itertools import starmap
from pickle import dump
from pickle import load
from typing import Iterator

from . import FileListCache
from ....utils import File


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
            any(dump(tuple(file), cache) for file in files)

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            try:
                yield from starmap(File, map(load, repeat(cache)))
            except EOFError:
                pass
