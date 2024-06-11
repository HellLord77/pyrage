from itertools import starmap
from typing import Iterator

from msgpack import Packer
from msgpack import Unpacker
from msgpack import pack
from msgpack import unpack

from . import StorageCache
from ....utils import File


class MsgPackStorageCache(StorageCache):
    EXTENSION = "msgpack"

    def _dump_file_list(self):
        with open(self._cache_path, "wb") as cache:
            pack(tuple(self), cache)

    def _load_file_list(self) -> Iterator[File]:
        with open(self._cache_path, "rb") as cache:
            return starmap(File, (unpack(cache)))


class MsgPackStorageCacheStreaming(MsgPackStorageCache):
    def _dump_file_list(self):
        packer = Packer()
        with open(self._cache_path, "wb") as cache:
            all(cache.write(packer.pack(file)) for file in self)

    def _load_file_list(self) -> Iterator[File]:
        with open(self._cache_path, "rb") as cache:
            yield from starmap(File, Unpacker(cache))
