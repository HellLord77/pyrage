from functools import lru_cache

from .filter import FileFilter
from .filter.extension import ExtensionFileFilter
from .filter.filetype import FileTypeFileFilter
from .filter.pathprefix import PathPrefixFileFilter
from .utils import StorageFilter
from ..utils import TStorage


# noinspection PyShadowingBuiltins
@lru_cache
def filter(storage: type[TStorage], file_filter: type[FileFilter]) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_filter.__name__}",
        (StorageFilter, storage),
        {"_t_file_filter": file_filter},
    )
