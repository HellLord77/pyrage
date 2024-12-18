from functools import lru_cache

from .transformer import FileTransformer
from .transformer.noop import NoopFileTransformer
from .transformer.pathprefix import PathPrefixFileTransformer
from .utils import StorageTransformer
from ..utils import TStorage


@lru_cache
def transformer(
    storage: type[TStorage],
    file_transformer: type[FileTransformer] = NoopFileTransformer,
) -> type[TStorage]:
    # noinspection PyTypeChecker
    return type(
        f"{storage.__name__}_{file_transformer.__name__}",
        (StorageTransformer, storage),
        {"_t_file_transformer": file_transformer},
    )
