from email.utils import parsedate_to_datetime
from typing import Iterable

from bs4 import BeautifulSoup
from requests import RequestException

from ..config import MYRIENT_EXTEND_GENERATE, MYRIENT_RETRY_EXTEND_GENERATE
from ..utils import DefragmentedSession, File, Readable, ReadableResponse
from . import Storage


class MyrientStorage(Storage):
    _BASE_URL = "https://myrient.erista.me/files/"

    def __init__(self, cwd: str = ""):
        self._cwd = cwd
        self._session = DefragmentedSession()
        super().__init__()

    def _file(self, path: str) -> File:
        if MYRIENT_EXTEND_GENERATE:
            while True:
                try:
                    response = self._session.head(
                        f"{self._BASE_URL}{self._cwd}{path}", allow_redirects=True
                    )
                    response.raise_for_status()
                except RequestException:
                    if not MYRIENT_RETRY_EXTEND_GENERATE:
                        raise
                else:
                    break
            return File(
                path,
                size=int(response.headers["Content-Length"]),
                mtime=parsedate_to_datetime(
                    response.headers["Last-Modified"]
                ).timestamp(),
            )
        else:
            return File(path)

    def _generate_file_list(self) -> Iterable[File]:
        paths = [""]
        while paths:
            prefix = paths.pop(0)
            response = self._session.get(f"{self._BASE_URL}{self._cwd}{prefix}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text)
            for row in soup.select("table#list tbody tr:nth-of-type(n+4)"):
                link = row.select_one("td.link a").get_text()
                path = f"{prefix}{link}"
                if link.endswith("/"):
                    paths.append(path)
                else:
                    yield self._file(path)

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(f"{self._BASE_URL}{self._cwd}{file.path}", stream=True)
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
