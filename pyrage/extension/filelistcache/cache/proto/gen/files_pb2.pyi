from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class Files(_message.Message):
    __slots__ = ("files",)

    class File(_message.Message):
        __slots__ = (
            "size",
            "mtime",
            "atime",
            "ctime",
            "crc32",
            "md5",
            "sha1",
            "sha256",
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
            size: _Optional[int] = ...,
            mtime: _Optional[float] = ...,
            atime: _Optional[float] = ...,
            ctime: _Optional[float] = ...,
            crc32: _Optional[str] = ...,
            md5: _Optional[str] = ...,
            sha1: _Optional[str] = ...,
            sha256: _Optional[str] = ...,
        ) -> None: ...

    class FilesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Files.File
        def __init__(
            self,
            key: _Optional[str] = ...,
            value: _Optional[_Union[Files.File, _Mapping]] = ...,
        ) -> None: ...

    FILES_FIELD_NUMBER: _ClassVar[int]
    files: _containers.MessageMap[str, Files.File]
    def __init__(self, files: _Optional[_Mapping[str, Files.File]] = ...) -> None: ...
