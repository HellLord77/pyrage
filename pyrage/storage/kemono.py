from datetime import datetime
from typing import Iterable

from requests import Session

from . import Storage
from ..config import KEMONO_EXTEND_GENERATE
from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse


class KemonoStorage(Storage):
    SERVER = "https://kemono.su"

    def __init__(self, service: str, creator_id: str):
        self._service = service
        self._creator_id = creator_id
        self._session = Session()
        super().__init__()

    def _file(self, path: str, ctime: float) -> File:
        if KEMONO_EXTEND_GENERATE:
            response = self._session.head(f"{self.SERVER}{path}", allow_redirects=True)
            response.raise_for_status()
            size = int(response.headers["Content-Length"])
            mtime = datetime.strptime(
                response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z"
            ).timestamp()
        else:
            size = None
            mtime = None
        return File(path[1:], size=size, mtime=mtime, ctime=ctime)

    def _generate_file_list(self) -> Iterable[File]:
        offset = 0
        limit = 0
        count = 1
        while offset + limit < count:
            response = self._session.get(
                f"{self.SERVER}/api/v1/{self._service}/user/{self._creator_id}/posts-legacy",
                params={"o": offset},
            )
            response.raise_for_status()
            json = response.json()
            for result in json["results"]:
                ctime = datetime.fromisoformat(result["published"]).timestamp()
                file = result["file"]
                if file:
                    yield self._file(file["path"], ctime)
                for attachment in result["attachments"]:
                    yield self._file(attachment["path"], ctime)
            count = json["props"]["count"]
            limit = json["props"]["limit"]
            offset += limit

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(f"{self.SERVER}/{file.path}", stream=True)
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError


class CoomerStorage(KemonoStorage):
    SERVER = "https://coomer.su"
