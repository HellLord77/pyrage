from posixpath import join
from posixpath import relpath

from dropbox import Dropbox
from dropbox.files import FileMetadata

from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable
from pyrage.utils import ReadableResponse


class DropboxStorage(Storage):
    def __init__(self, token: str, cwd: str = "/"):
        self._dropbox = Dropbox(token)
        self._cwd = cwd
        super().__init__()

    def _update_file_list(self):
        for entry in self._dropbox.files_list_folder(
            self._cwd * (self._cwd != "/"), True
        ).entries:
            if isinstance(entry, FileMetadata):
                self._add_file_list(
                    File(relpath(entry.path_display, self._cwd), size=entry.size)
                )

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._dropbox.files_download(join(self._cwd, file.path))[1]
        )

    def _set_file(self, file: File, readable: Readable):
        self._dropbox.files_upload(readable.read(), join(self._cwd, file.path))

    def _del_file(self, file: File):
        self._dropbox.files_delete_v2(join(self._cwd, file.path))
