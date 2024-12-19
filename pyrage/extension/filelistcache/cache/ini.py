from ast import literal_eval
from configparser import ConfigParser
from itertools import islice
from typing import Iterator

from . import FileListCache
from ....utils import File


class INIFileListCache(FileListCache):
    EXTENSION = "ini"

    def _dump(self, files: Iterator[File]):
        config = ConfigParser()
        config.optionxform = str
        config["_"] = {file.path: file.encode() for file in files}
        with open(self.path, "w") as cache:
            config.write(cache, False)

    def _load(self) -> Iterator[File]:
        config = ConfigParser()
        config.optionxform = str
        with open(self.path, "r") as cache:
            config.read_file(cache)
        return (File.decode(path, file) for path, file in config["_"].items())


class PrettyINIFileListCache(INIFileListCache):
    def _dump(self, files: Iterator[File]):
        config = ConfigParser()
        config.optionxform = str
        config["_"] = {file.path: file[1:] for file in files}
        with open(self.path, "w") as cache:
            config.write(cache)


class CompatINIFileListCache(INIFileListCache):
    def _dump(self, files: Iterator[File]):
        config = ConfigParser()
        config.update(
            (file.path, dict(islice(zip(file._fields, map(repr, file)), 1, None)))
            for file in files
        )
        with open(self.path, "w") as cache:
            config.write(cache)

    def _load(self) -> Iterator[File]:
        config = ConfigParser()
        with open(self.path, "r") as cache:
            config.read_file(cache)
        return (
            File(path=path, **dict(zip(file, map(literal_eval, file.values()))))
            for path, file in config.items()
        )
