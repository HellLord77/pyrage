from abc import ABCMeta
from abc import abstractmethod
from os import makedirs
from os.path import dirname
from os.path import exists
from os.path import realpath
from typing import Iterable
from typing import Iterator
from typing import Optional
from typing import TextIO

from ....utils import File


class StorageCache(metaclass=ABCMeta):
    EXTENSION: str

    _file_list: dict[str, File]

    def __init__(self, *args, cache_path: Optional[str] = None, **kwargs):
        if cache_path is None:
            cache_path = f"{type(self).__name__}.{self.EXTENSION}"
        self._cache_path = realpath(cache_path)
        super().__init__(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def _dump_file_list(writable: TextIO, files: Iterable[File]):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _load_file_list(readable: TextIO) -> Iterator[File]:
        raise NotImplementedError

    def _generate_file_list(self) -> Iterable[File]:
        if exists(self._cache_path):
            with open(self._cache_path, "r") as file:
                yield from self._load_file_list(file)
        else:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            yield from super()._generate_file_list()
            makedirs(dirname(self._cache_path), exist_ok=True)
            with open(self._cache_path, "w", newline="") as file:
                # noinspection PyTypeChecker
                self._dump_file_list(file, self)
