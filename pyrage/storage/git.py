from os.path import join
from typing import Optional

from git import Repo
from requests import Session

from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable


class GitStorage(Storage):
    def __init__(self, path: str, rev: Optional[str] = None):
        self._repo = Repo(path)
        self._rev = rev
        self._session = Session()
        super().__init__()

    def _update_file_list(self):
        for index in self._repo.tree(self._rev).traverse():
            if "blob" == index.type:
                # noinspection PyArgumentList
                self._add_file_list(File(index.path, size=index.size))

    def _get_file(self, file: File) -> Readable:
        return open(join(self._repo.working_dir, file.path), "rb")

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
