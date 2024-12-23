from functools import lru_cache

from .cache import FileListCache
from .cache.csv import CSVFileListCache
from .cache.ini import INIFileListCache
from .cache.json import JSONFileListCache
from .cache.pickle import StreamingPickleFileListCache as PickleFileListCache
from .cache.sqlite import SqliteFileListCache
from .utils import StorageCache
from ..utils import TStorage


@lru_cache
def cache(
    storage: type[TStorage], file_list_cache: type[FileListCache] = JSONFileListCache
) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_list_cache.__name__}",
        (StorageCache, storage),
        {"_t_file_list_cache": file_list_cache},
    )
