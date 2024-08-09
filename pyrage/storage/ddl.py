from typing import Optional, Iterable
from urllib.parse import urlparse

from requests import Session

from . import Storage
from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse


class DDLStorage(Storage):
    def __init__(
        self,
        url: str,
        name: Optional[str] = None,
        size: Optional[int] = None,
        crc32: Optional[str] = None,
        md5: Optional[str] = None,
    ):
        self._url = url
        self._name = name
        self._size = size
        self._crc32 = crc32
        self._md5 = md5
        self._session = Session()
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        if self._name is None or self._size is None:
            headers = self._session.head(self._url).headers
            if self._name is None:  # TODO headers.get("Content-Disposition")
                self._name = urlparse(self._url).path.split("/")[-1]
            if self._size is None:
                size = headers.get("Content-Length")
                if size is not None:
                    self._size = int(size)
        yield File(self._name, size=self._size, crc32=self._crc32, md5=self._md5)

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(self._session.get(self._url, stream=True))

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
