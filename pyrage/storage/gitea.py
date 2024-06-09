from typing import Iterable

from gitea import Gitea
from gitea import Repository

from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable
from pyrage.utils import ReadableResponse


class GiteaStorage(Storage):
    def __init__(self, url: str, owner: int | str, repo: str = "", sha: str = "main"):
        gitea = Gitea(url, auth=1)
        gitea.requests.auth = None
        self._repo = Repository.request(gitea, owner, repo)
        self._sha = sha
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for element in self._repo.gitea.requests_get(
            f"/repos/{self._repo.get_full_name()}/git/trees/{self._sha}",
            {"recursive": 1},
        )["tree"]:
            if "blob" == element["type"]:
                yield File(element["path"], size=element["size"])

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._repo.gitea.requests.get(
                f"{self._repo.gitea.url}/{self._repo.get_full_name()}/raw/branch/{self._sha}/{file.path}",
                stream=True,
            )
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
