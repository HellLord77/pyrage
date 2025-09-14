from typing import Iterable
from typing import Optional

from wayback import CdxRecord
from wayback import WaybackClient

from . import Storage
from ..config import WAYBACK_EXTEND_GENERATE
from ..config import WAYBACK_FLAT_PATH
from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse
from ..utils import lsplit


class WaybackMachineStorage(Storage):
    def __init__(
        self,
        url: str,
        filter_field: str | list[str] | tuple[str, ...] = "!statuscode:[45]..",
        collapse: Optional[str] = "urlkey",
    ):
        self._url = url
        self._filter_field = filter_field
        self._collapse = collapse
        self._client = WaybackClient()
        super().__init__()

    def _file(self, record: CdxRecord) -> File:
        path = record.url.removeprefix(self._url)
        if not WAYBACK_FLAT_PATH:
            path = f"{record.timestamp.strftime('%Y%m%d%H%M%S')}/{path}"
        mtime = record.timestamp.timestamp()
        if WAYBACK_EXTEND_GENERATE:
            response = self._client.session.head(record.raw_url, allow_redirects=True)
            response.raise_for_status()
            return File(path, size=int(response.headers["Content-Length"]), mtime=mtime)
        else:
            return File(path, mtime=mtime)

    def _generate_file_list(self) -> Iterable[File]:
        return map(
            self._file,
            self._client.search(
                self._url,
                match_type="prefix",
                filter_field=self._filter_field,
                collapse=self._collapse,
            ),
        )

    def _get_file(self, file: File) -> Readable:
        if WAYBACK_FLAT_PATH:
            url = next(self._client.search(f"{self._url}{file.path}")).raw_url
        else:
            timestamp, path = lsplit(file.path)
            url = (f"https://web.archive.org/web/{timestamp}id_/{self._url}{path}",)
        return ReadableResponse(
            self._client.session.get(
                url,
                stream=True,
            )
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
