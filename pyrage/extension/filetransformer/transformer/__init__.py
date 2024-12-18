from abc import ABCMeta
from abc import abstractmethod
from typing import Iterable

from ....utils import File


class FileTransformer(metaclass=ABCMeta):
    @abstractmethod
    def _apply(self, file: File) -> File:
        raise NotImplementedError

    @abstractmethod
    def _revert(self, file: File) -> File:
        raise NotImplementedError

    def map(self, files: Iterable[File]) -> Iterable[File]:
        return map(self._apply, files)

    def get(self, file: File) -> File:
        return self._revert(file)
