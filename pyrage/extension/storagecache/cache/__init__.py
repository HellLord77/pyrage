from abc import ABCMeta
from abc import abstractmethod
from os import makedirs
from os.path import dirname
from os.path import exists
from os.path import getsize
from os.path import realpath
from typing import Iterable
from typing import Iterator
from typing import Optional

from ....utils import File


class StorageCache(metaclass=ABCMeta):
    EXTENSION: str

    def __init__(self, *args, cache_path: Optional[str] = None, **kwargs):
        if cache_path is None:
            cache_path = f"{type(self).__name__}.{self.EXTENSION}"
        self._cache_path = realpath(cache_path)
        super().__init__(*args, **kwargs)

    def __iter__(self) -> Iterator[File]: ...

    @abstractmethod
    def _dump_file_list(self):
        raise NotImplementedError

    @abstractmethod
    def _load_file_list(self) -> Iterator[File]:
        raise NotImplementedError

    def _generate_file_list(self) -> Iterable[File]:
        if exists(self._cache_path) and getsize(self._cache_path):
            yield from self._load_file_list()
        else:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            yield from super()._generate_file_list()
            makedirs(dirname(self._cache_path), exist_ok=True)
            self._dump_file_list()


del StorageCache.__iter__
