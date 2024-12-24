from typing import Iterable, Iterator

from google.protobuf.json_format import MessageToDict

from .file_pb2 import File as File_
from .. import FileListCache
from .....utils import File


class ProtoFileListCache(FileListCache):
    EXTENSION = "bin"

    def _dump(self, files: Iterable[File]):
        with open(self.path, "wb") as cache:
            for file in files:
                string = File_(**file._asdict()).SerializeToString()
                cache.write(len(string).to_bytes(4))
                cache.write(string)

    def _load(self) -> Iterator[File]:  # FIXME type(size) = str
        with open(self.path, "rb") as cache:
            while size := cache.read(4):
                yield File(
                    **MessageToDict(File_.FromString(cache.read(int.from_bytes(size))))
                )
