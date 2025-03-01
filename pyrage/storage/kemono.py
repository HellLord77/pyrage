from datetime import datetime
from os.path import splitext
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

    def _file(self, file: dict[str, str]) -> File:
        name = file["path"][7:]
        sha256 = splitext(name)[0]
        if KEMONO_EXTEND_GENERATE:
            response = self._session.get(f"{self.SERVER}/api/v1/search_hash/{sha256}")
            response.raise_for_status()
            json = response.json()
            return File(
                f"{sha256}{json["ext"]}",
                size=json["size"],
                mtime=datetime.fromisoformat(json["mtime"]).timestamp(),
                ctime=datetime.fromisoformat(json["ctime"]).timestamp(),
                sha256=sha256,
            )
        else:
            return File(name, sha256=sha256)

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
                file = result["file"]
                if file:
                    yield self._file(file)
                for attachment in result["attachments"]:
                    yield self._file(attachment)
            count = json["props"]["count"]
            limit = json["props"]["limit"]
            offset += limit

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(
                f"{self.SERVER}/{file.path[:2]}/{file.path[2:4]}/{file.path}",
                stream=True,
            )
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError


class CoomerStorage(KemonoStorage):
    SERVER = "https://coomer.su"
