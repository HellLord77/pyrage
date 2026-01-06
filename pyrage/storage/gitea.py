from collections.abc import Iterable

from gitea import Gitea
from gitea import Repository

from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse
from . import Storage


class GiteaStorage(Storage):
    def __init__(self, url: str, owner: int | str, repo: str = "", sha: str | None = None):
        gitea = Gitea(url, auth=1)
        gitea.requests.auth = None
        self._repo = Repository.request(gitea, owner, repo)
        if sha is None:
            sha = self._repo.default_branch
        self._sha = sha
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for element in self._repo.gitea.requests_get(
            f"/repos/{self._repo.get_full_name()}/git/trees/{self._sha}",
            {"recursive": 1},
        )["tree"]:
            if element["type"] == "blob":
                yield File(element["path"], size=element["size"])

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._repo.gitea.requests.get(
                f"{self._repo.gitea.url}/{self._repo.get_full_name()}/raw/branch/{self._sha}/{file.path}",
                stream=True,
            ),
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
