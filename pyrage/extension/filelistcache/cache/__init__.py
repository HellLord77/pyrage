from abc import ABCMeta, abstractmethod
from os import makedirs
from os.path import dirname, exists, getsize, realpath
from typing import Iterable, Iterator, Optional

from ....utils import File


class FileListCache(metaclass=ABCMeta):
    EXTENSION: str

    def __init__(self, path: Optional[str] = None):
        if path is None:
            path = f"{type(self).__name__}.{self.EXTENSION}"
        self.path = realpath(path)

    @abstractmethod
    def _dump(self, files: Iterable[File]):
        raise NotImplementedError

    @abstractmethod
    def _load(self) -> Iterator[File]:
        raise NotImplementedError

    def generate(
        self, generator: Iterable[File], files: Iterable[File]
    ) -> Iterator[File]:
        if exists(self.path) and getsize(self.path):
            yield from self._load()
        else:
            yield from generator
            makedirs(dirname(self.path), exist_ok=True)
            self._dump(files)
