from itertools import repeat
from itertools import starmap
from pickle import dump
from pickle import load
from typing import Iterator

from . import StorageCache
from ....utils import File


class PickleStorageCache(StorageCache):
    EXTENSION = "pickle"

    def _dump_file_list(self):
        with open(self._cache_path, "wb") as cache:
            dump(tuple(self), cache)

    def _load_file_list(self) -> Iterator[File]:
        with open(self._cache_path, "rb") as cache:
            return load(cache)


class PickleStorageCacheStreaming(StorageCache):
    def _dump_file_list(self):
        with open(self._cache_path, "wb") as cache:
            any(dump(tuple(file), cache) for file in self)

    def _load_file_list(self) -> Iterator[File]:
        with open(self._cache_path, "rb") as cache:
            try:
                yield from starmap(File, map(load, repeat(cache)))
            except EOFError:
                pass
