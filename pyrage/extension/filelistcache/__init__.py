from functools import lru_cache

from ..utils import TStorage
from .cache import FileListCache
from .cache.csv import CSVFileListCache as CSVFileListCache
from .cache.json import JSONFileListCache as JSONFileListCache
from .cache.pickle import PickleFileListCache as PickleFileListCache
from .cache.sqlite import SqliteFileListCache as SqliteFileListCache
from .utils import StorageCache


@lru_cache
def cache(storage: type[TStorage], file_list_cache: type[FileListCache] = JSONFileListCache) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_list_cache.__name__}",
        (StorageCache, storage),
        {"_t_file_list_cache": file_list_cache},
    )
