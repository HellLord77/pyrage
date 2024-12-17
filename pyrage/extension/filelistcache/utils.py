from abc import ABCMeta
from typing import Iterable
from typing import Optional

from .cache import FileListCache
from ...storage import Storage
from ...utils import File


class StorageCache(Storage, metaclass=ABCMeta):
    _t_file_list_cache: type[FileListCache]

    def __init__(self, *args, cache_path: Optional[str] = None, **kwargs):
        self._file_list_cache = self._t_file_list_cache(cache_path)
        super().__init__(*args, **kwargs)

    def _generate_file_list(self) -> Iterable[File]:
        return self._file_list_cache.generate(super()._generate_file_list(), self)
