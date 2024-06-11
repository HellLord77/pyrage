from functools import lru_cache

from .mapping import FileListMapping
from .mapping.sqlite import SqliteFileListMapping
from ..utils import TStorage


@lru_cache
def mapping(
    storage: type[TStorage],
    file_list_mapping: type[FileListMapping] = SqliteFileListMapping,
) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(storage.__name__ + "Mapping", (file_list_mapping, storage), {})
