from datetime import datetime
from typing import Iterable, Optional

from requests import Session
from requests_toolbelt import MultipartEncoder

from ..config import ROMM_FLAT_PATH
from ..utils import File, Readable, ReadableResponse
from . import Storage


class RomMStorage(Storage):
    def __init__(
        self,
        platform_id: int | str,
        host: str = "https://demo.romm.app",
        auth: Optional[tuple[str, str]] = None,
    ):
        self._host = host
        self._session = Session()
        self._session.auth = auth
        if isinstance(platform_id, str):
            response = self._session.get(f"{self._host}/api/platforms")
            response.raise_for_status()
            for plat in response.json():
                if plat["slug"] == platform_id:
                    platform_id = plat["id"]
                    break
            else:
                raise NotImplementedError
        self._platform_id = str(platform_id)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        offset = 0
        while True:
            response = self._session.get(
                f"{self._host}/api/roms",
                params={"platform_id": self._platform_id, "offset": offset},
            )
            response.raise_for_status()
            roms = response.json()
            for rom in roms["items"]:
                for file in rom["files"]:
                    path = file["file_name"]
                    if not ROMM_FLAT_PATH:
                        path = f"{rom['rom_id']}/{path}"
                    yield File(
                        path,
                        mtime=datetime.fromisoformat(file["last_modified"]).timestamp(),
                        size=file["file_size_bytes"],
                        crc32=file["crc_hash"],
                        md5=file["md5_hash"],
                        sha1=file["sha1_hash"],
                    )
            offset += len(roms["items"])
            if offset >= roms["total"]:
                break

    def _get_file(self, file: File) -> Readable:
        if ROMM_FLAT_PATH:
            raise NotImplementedError
        else:
            rom_id, file_name = file.path.split("/", 1)
            return ReadableResponse(
                self._session.get(
                    f"{self._host}/api/roms/{rom_id}/content/{file_name}", stream=True
                )
            )

    def _set_file(self, file: File, readable: Readable):
        data = MultipartEncoder({file.path: readable})
        self._session.post(
            f"{self._host}/api/roms",
            data,
            headers={
                "Content-Type": data.content_type,
                "X-Upload-Platform": self._platform_id,
                "X-Upload-Filename": file.path,
            },
        )

    def _del_file(self, file: File):
        raise NotImplementedError
