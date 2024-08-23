from ast import literal_eval
from configparser import ConfigParser
from itertools import islice
from typing import Iterator

from . import StorageCache
from ....utils import File


class INIStorageCache(StorageCache):
    EXTENSION = "ini"

    def _dump_file_list(self):
        config = ConfigParser()
        config.optionxform = str
        config["_"] = {file.path: file.encode() for file in self}
        with open(self._cache_path, "w") as cache:
            config.write(cache, False)

    def _load_file_list(self) -> Iterator[File]:
        config = ConfigParser()
        config.optionxform = str
        with open(self._cache_path, "r") as cache:
            config.read_file(cache)
        return (File.decode(path, file) for path, file in config["_"].items())


class INIStorageCachePretty(INIStorageCache):
    def _dump_file_list(self):
        config = ConfigParser()
        config.optionxform = str
        config["_"] = {file.path: file[1:] for file in self}
        with open(self._cache_path, "w") as cache:
            config.write(cache)


class INIStorageCacheCompat(INIStorageCache):
    def _dump_file_list(self):
        config = ConfigParser()
        config.update(
            (file.path, dict(islice(zip(file._fields, map(repr, file)), 1, None)))
            for file in self
        )
        with open(self._cache_path, "w") as cache:
            config.write(cache)

    def _load_file_list(self) -> Iterator[File]:
        config = ConfigParser()
        with open(self._cache_path, "r") as cache:
            config.read_file(cache)
        return (
            File(path=path, **dict(zip(file, map(literal_eval, file.values()))))
            for path, file in config.items()
        )
