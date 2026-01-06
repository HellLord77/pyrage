from functools import lru_cache

from ..utils import TStorage
from .filter import FileFilter
from .filter.extension import ExtensionFileFilter as ExtensionFileFilter
from .filter.filetype import FileTypeFileFilter as FileTypeFileFilter
from .filter.pathprefix import PathPrefixFileFilter as PathPrefixFileFilter
from .utils import StorageFilter


# noinspection PyShadowingBuiltins
@lru_cache
def filter(storage: type[TStorage], file_filter: type[FileFilter]) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_filter.__name__}",
        (StorageFilter, storage),
        {"_t_file_filter": file_filter},
    )
