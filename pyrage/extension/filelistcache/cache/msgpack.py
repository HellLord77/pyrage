from itertools import starmap
from typing import Iterator

from msgpack import Packer, Unpacker, pack, unpack

from ....utils import File, consume
from . import FileListCache


class MsgPackFileListCache(FileListCache):
    EXTENSION = "msgpack"

    def _dump(self, files: Iterator[File]):
        with open(self.path, "wb") as cache:
            pack(tuple(files), cache)

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            return starmap(File, (unpack(cache)))


class StreamingMsgPackFileListCache(MsgPackFileListCache):
    def _dump(self, files: Iterator[File]):
        packer = Packer()
        with open(self.path, "wb") as cache:
            consume(cache.write(packer.pack(file)) for file in files)

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            yield from starmap(File, Unpacker(cache))
