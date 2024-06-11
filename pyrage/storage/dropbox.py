from posixpath import join
from posixpath import relpath
from typing import Iterable

from dropbox import Dropbox
from dropbox.files import FileMetadata

from . import Storage
from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse


class DropboxStorage(Storage):
    def __init__(self, token: str, cwd: str = "/"):
        self._dropbox = Dropbox(token)
        self._cwd = cwd
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for entry in self._dropbox.files_list_folder(
            self._cwd * (self._cwd != "/"), True
        ).entries:
            if isinstance(entry, FileMetadata):
                yield File(relpath(entry.path_display, self._cwd), size=entry.size)

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._dropbox.files_download(join(self._cwd, file.path))[1]
        )

    def _set_file(self, file: File, readable: Readable):
        self._dropbox.files_upload(readable.read(), join(self._cwd, file.path))

    def _del_file(self, file: File):
        self._dropbox.files_delete_v2(join(self._cwd, file.path))
