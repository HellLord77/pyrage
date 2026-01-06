from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class Files(_message.Message):
    __slots__ = ("files",)

    class File(_message.Message):
        __slots__ = (
            "atime",
            "crc32",
            "ctime",
            "md5",
            "mtime",
            "sha1",
            "sha256",
            "size",
        )
        SIZE_FIELD_NUMBER: _ClassVar[int]
        MTIME_FIELD_NUMBER: _ClassVar[int]
        ATIME_FIELD_NUMBER: _ClassVar[int]
        CTIME_FIELD_NUMBER: _ClassVar[int]
        CRC32_FIELD_NUMBER: _ClassVar[int]
        MD5_FIELD_NUMBER: _ClassVar[int]
        SHA1_FIELD_NUMBER: _ClassVar[int]
        SHA256_FIELD_NUMBER: _ClassVar[int]
        size: int
        mtime: float
        atime: float
        ctime: float
        crc32: str
        md5: str
        sha1: str
        sha256: str
        def __init__(
            self,
            size: int | None = ...,
            mtime: float | None = ...,
            atime: float | None = ...,
            ctime: float | None = ...,
            crc32: str | None = ...,
            md5: str | None = ...,
            sha1: str | None = ...,
            sha256: str | None = ...,
        ) -> None: ...

    class FilesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Files.File
        def __init__(self, key: str | None = ..., value: Files.File | _Mapping | None = ...) -> None: ...

    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.MessageMap[str, Files.File]
    def __init__(self, files: _Mapping[str, Files.File] | None = ...) -> None: ...
