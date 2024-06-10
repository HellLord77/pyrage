from functools import lru_cache
from typing import TypeVar

from .cache import StorageCache
from .cache.csv import CSVStorageCache
from .cache.json import JSONStorageCache
from ...storage import Storage

T = TypeVar("T", bound=Storage)


@lru_cache
def cache(
    storage: type[T], storage_cache: type[StorageCache] = JSONStorageCache
) -> type[T]:
    # noinspection PyTypeChecker
    return type(storage.__name__ + "Cache", (storage_cache, storage), {})
