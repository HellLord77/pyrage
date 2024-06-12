from functools import lru_cache

from .cache import StorageCache
from .cache.csv import CSVStorageCache
from .cache.ini import INIStorageCache
from .cache.json import JSONStorageCache
from .cache.pickle import PickleStorageCacheStreaming as PickleStorageCache
from .cache.sqlite import SqliteStorageCache
from ..utils import TStorage


@lru_cache
def cache(
    storage: type[TStorage], storage_cache: type[StorageCache] = JSONStorageCache
) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{storage_cache.__name__}", (storage_cache, storage), {}
    )
