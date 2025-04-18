from typing import Iterable
from typing import Iterator

from flatbuffers import Builder

from .gen import File as File_
from .gen.File import End as EndFile
from .gen.File import Start as StartFile
from .gen.Files import AddFiles
from .gen.Files import End as EndFiles
from .gen.Files import Files
from .gen.Files import Start as StartFiles
from .gen.Files import StartFilesVector
from .. import FileListCache
from .....utils import File


def _get_file(builder: Builder, file: File) -> int:
    file_ = file._asdict()
    file_["path"] = builder.CreateString(file.path)
    if file.crc32 is not None:
        file_["crc32"] = builder.CreateString(file.crc32)
    if file.md5 is not None:
        file_["md5"] = builder.CreateString(file.md5)
    if file.sha1 is not None:
        file_["sha1"] = builder.CreateString(file.sha1)
    if file.sha256 is not None:
        file_["sha256"] = builder.CreateString(file.sha256)
    StartFile(builder)
    adders = vars(File_)
    for field, value in file_.items():
        if value is not None:
            adders[f"Add{field.capitalize()}"](builder, value)
    return EndFile(builder)


class FlatFileListCache(FileListCache):
    EXTENSION = "bin"

    def _dump(self, files: Iterable[File]):
        builder = Builder()
        files_ = tuple(_get_file(builder, file) for file in files)
        StartFilesVector(builder, len(files_))
        any(map(builder.PrependUOffsetTRelative, files_))
        files__ = builder.EndVector()
        StartFiles(builder)
        AddFiles(builder, files__)
        builder.Finish(EndFiles(builder))
        with open(self.path, "wb") as cache:
            cache.write(builder.Output())

    def _load(self) -> Iterator[File]:
        with open(self.path, "rb") as cache:
            files = Files.GetRootAs(cache.read())
        for index in range(files.FilesLength()):
            file = files.Files(index)
            yield File(
                file.Path().decode(),
                size=None if (size := file.Size()) is None else size,
                mtime=None if (mtime := file.Mtime()) is None else mtime,
                ctime=None if (ctime := file.Ctime()) is None else ctime,
                atime=None if (atime := file.Atime()) is None else atime,
                crc32=None if (crc32 := file.Crc32()) is None else crc32.decode(),
                md5=None if (md5 := file.Md5()) is None else md5.decode(),
                sha1=None if (sha1 := file.Sha1()) is None else sha1.decode(),
                sha256=None if (sha256 := file.Sha256()) is None else sha256.decode(),
            )
