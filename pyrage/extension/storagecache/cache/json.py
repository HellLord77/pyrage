from itertools import starmap
from json import dump
from json import load
from typing import Iterator

from . import StorageCache
from ....utils import File


class JSONStorageCache(StorageCache):
    EXTENSION = "json"

    def _dump_file_list(self):
        with open(self._cache_path, "w") as cache:
            dump(tuple(self), cache, separators=(",", ":"))

    def _load_file_list(self) -> Iterator[File]:
        with open(self._cache_path, "r") as cache:
            return starmap(File, load(cache))


class JSONStorageCachePretty(JSONStorageCache):
    def _dump_file_list(self):
        with open(self._cache_path, "w") as cache:
            dump(tuple(self), cache, indent=2)
