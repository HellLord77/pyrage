from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class File(_message.Message):
    __slots__ = ("path", "size", "mtime", "atime", "ctime", "crc32", "md5", "sha1")
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MTIME_FIELD_NUMBER: _ClassVar[int]
    ATIME_FIELD_NUMBER: _ClassVar[int]
    CTIME_FIELD_NUMBER: _ClassVar[int]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    MD5_FIELD_NUMBER: _ClassVar[int]
    SHA1_FIELD_NUMBER: _ClassVar[int]
    path: str
    size: int
    mtime: float
    atime: float
    ctime: float
    crc32: str
    md5: str
    sha1: str
    def __init__(self, path: _Optional[str] = ..., size: _Optional[int] = ..., mtime: _Optional[float] = ..., atime: _Optional[float] = ..., ctime: _Optional[float] = ..., crc32: _Optional[str] = ..., md5: _Optional[str] = ..., sha1: _Optional[str] = ...) -> None: ...
