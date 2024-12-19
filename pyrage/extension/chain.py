from functools import lru_cache
from posixpath import sep

from .filefilter import PathPrefixFileFilter
from .filefilter import filter
from .filetransformer import PathPrefixFileTransformer
from .filetransformer import transformer
from .utils import TStorage


# noinspection PyShadowingBuiltins,PyArgumentList
@lru_cache
def cwd(storage: type[TStorage], dir: str) -> type[TStorage]:
    extension_kwargs = {"path_prefix": dir + sep}
    storage_cwd = transformer(
        filter(storage, PathPrefixFileFilter), PathPrefixFileTransformer
    )
    __init__ = lambda self, *args, **kwargs: super(storage_cwd, self).__init__(
        *args,
        **kwargs,
        filter_kwargs=extension_kwargs,
        transformer_kwargs=extension_kwargs,
    )
    # noinspection PyTypeChecker
    return type(f"{storage.__name__}_CWD", (storage_cwd,), {"__init__": __init__})
