from itertools import starmap
from json import dump
from json import load
from typing import Iterator

from . import FileListCache
from ....utils import File


class JSONFileListCache(FileListCache):
    EXTENSION = "json"

    def _dump(self, files: Iterator[File]):
        with open(self.path, "w") as cache:
            dump(tuple(files), cache, separators=(",", ":"))

    def _load(self) -> Iterator[File]:
        with open(self.path, "r") as cache:
            return starmap(File, load(cache))


class JSONFileListCachePretty(JSONFileListCache):
    def _dump(self, files: Iterator[File]):
        with open(self.path, "w") as cache:
            dump(tuple(files), cache, indent=2)


class JSONFileListCacheCompat(JSONFileListCache):
    def _dump(self, files: Iterator[File]):
        with open(self.path, "w") as cache:
            dump(tuple(file._asdict() for file in files), cache, indent=2)

    def _load(self) -> Iterator[File]:
        with open(self.path, "r") as cache:
            return (File(**file) for file in load(cache))
