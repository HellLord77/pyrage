from typing import Iterable
from typing import Optional

from internetarchive import File
from internetarchive import get_item
from internetarchive import upload

from . import Storage
from ..utils import File as File_
from ..utils import Readable
from ..utils import ReadableResponse


class InternetArchiveStorage(Storage):
    def __init__(
        self,
        identifier: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self._item = get_item(
            identifier, {"s3": {"access": access_key, "secret": secret_key}}
        )
        super().__init__()

    def _generate_file_list(self) -> Iterable[File_]:
        for file in self._item.get_files():
            if file.metadata != "Metadata":
                yield File_(
                    file.name,
                    size=file.size,
                    mtime=file.mtime,
                    crc32=file.crc32,
                    md5=file.md5,
                    sha1=file.sha1,
                )

    def _get_file(self, file: File_) -> Readable:
        # noinspection PyTypeChecker
        return ReadableResponse(
            File(self._item, file.path).download(return_responses=True)
        )

    def _set_file(self, file: File_, readable: Readable):
        upload(self._item.identifier, {file.path: readable})

    def _del_file(self, file: File_):
        File(self._item, file.path).delete(True)
