from abc import ABCMeta
from collections.abc import Iterable

from ...storage import Storage
from ...utils import File
from .cache import FileListCache


class StorageCache(Storage, metaclass=ABCMeta):
    _t_file_list_cache: type[FileListCache]

    def __init__(self, *args, cache_path: str | None = None, **kwargs):
        self._file_list_cache = self._t_file_list_cache(cache_path)
        super().__init__(*args, **kwargs)

    def _generate_file_list(self) -> Iterable[File]:
        return self._file_list_cache.generate(super()._generate_file_list(), self)
