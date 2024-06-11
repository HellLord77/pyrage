from os.path import join
from typing import Iterable
from typing import Optional

from git import Repo
from requests import Session

from . import Storage
from ..utils import File
from ..utils import Readable


class GitStorage(Storage):
    def __init__(self, path: str, rev: Optional[str] = None):
        self._repo = Repo(path)
        self._rev = rev
        self._session = Session()
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for index in self._repo.tree(self._rev).traverse():
            if "blob" == index.type:
                yield File(index.path, size=index.size)

    def _get_file(self, file: File) -> Readable:
        return open(join(self._repo.working_dir, file.path), "rb")

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
