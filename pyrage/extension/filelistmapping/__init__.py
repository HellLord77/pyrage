from functools import lru_cache

from ..utils import TStorage
from .mapping import FileListMapping
from .mapping.local import LocalFileListMapping
from .mapping.sqlite import SqliteFileListMapping
from .utils import StorageMapping


@lru_cache
def mapping(
    storage: type[TStorage],
    file_list_mapping: type[FileListMapping] = SqliteFileListMapping,
) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_list_mapping.__name__}",
        (StorageMapping, storage),
        {"_t_file_list_mapping": file_list_mapping},
    )
