from collections.abc import Iterator
from itertools import starmap
from json import dump
from json import load

from ....utils import File
from . import FileListCache


class JSONFileListCache(FileListCache):
    EXTENSION = "json"

    def _dump(self, files: Iterator[File]):
        with open(self.path, "w") as cache:
            dump(tuple(files), cache, separators=(",", ":"))

    def _load(self) -> Iterator[File]:
        with open(self.path) as cache:
            return starmap(File, load(cache))


class PrettyJSONFileListCache(JSONFileListCache):
    def _dump(self, files: Iterator[File]):
        with open(self.path, "w") as cache:
            dump(tuple(files), cache, indent=2)


class CompatJSONFileListCache(JSONFileListCache):
    def _dump(self, files: Iterator[File]):
        with open(self.path, "w") as cache:
            dump(tuple(file._asdict() for file in files), cache, indent=2)

    def _load(self) -> Iterator[File]:
        with open(self.path) as cache:
            return (File(**file) for file in load(cache))
