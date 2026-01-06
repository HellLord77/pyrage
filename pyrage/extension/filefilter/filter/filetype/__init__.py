from mimetypes import MimeTypes
from os.path import dirname
from os.path import join

from .....utils import File
from .. import FileFilter


class FileTypeFileFilter(FileFilter):
    MIME_TYPES = MimeTypes((join(dirname(__file__), "mime.types"),))

    def __init__(self, invert: bool = False, file_type: str = ""):
        self._file_type = file_type
        super().__init__(invert)

    def __call__(self, file: File) -> bool:
        return self.MIME_TYPES.guess_file_type(file.path)[0].startswith(self._file_type)
