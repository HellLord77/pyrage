from functools import lru_cache

from .filter import FileListFilter
from .filter.noop import NoopFileListFilter
from .utils import StorageFilter
from ..utils import TStorage


# noinspection PyShadowingBuiltins
@lru_cache
def filter(
    storage: type[TStorage],
    file_list_filter: type[FileListFilter] = NoopFileListFilter,
) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_list_filter.__name__}",
        (StorageFilter, storage),
        {"_t_file_list_filter": file_list_filter},
    )
