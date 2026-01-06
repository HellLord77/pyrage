from functools import lru_cache

from ..utils import TStorage
from .transformer import FileTransformer
from .transformer.pathprefix import PathPrefixFileTransformer as PathPrefixFileTransformer
from .utils import StorageTransformer


@lru_cache
def transformer(storage: type[TStorage], file_transformer: type[FileTransformer]) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_transformer.__name__}",
        (StorageTransformer, storage),
        {"_t_file_transformer": file_transformer},
    )
