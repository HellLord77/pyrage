from typing import Iterable
from typing import Iterator

from google.protobuf.json_format import MessageToDict

from .gen.files_pb2 import Files
from .. import FileListCache
from .....utils import File


class ProtoFileListCache(FileListCache):
    EXTENSION = "bin"

    def _dump(self, files: Iterable[File]):
        files_ = Files()
        for file in files:
            file_ = file._asdict()
            file__ = files_.files[file_.pop("path")]
            for field, value in file_.items():
                if value is not None:
                    setattr(file__, field, value)
        with open(self.path, "wb") as cache:
            cache.write(files_.SerializeToString())

    def _load(self) -> Iterator[File]:  # FIXME type(size) = str
        with open(self.path, "rb") as cache:
            files = Files.FromString(cache.read())
        return (
            File(path=path, **MessageToDict(file)) for path, file in files.files.items()
        )
