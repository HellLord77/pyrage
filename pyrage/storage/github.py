from collections.abc import Iterable

from github import Github
from github.Consts import DEFAULT_BASE_URL
from requests import Session

from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse
from . import Storage


class GithubStorage(Storage):
    FMT_RAW_URL = "{}/{}/{}/{}"

    base_url = DEFAULT_BASE_URL
    raw_host = "https://raw.githubusercontent.com"

    def __init__(self, owner: int | str, repo: str = "", sha: str | None = None):
        self._repo = Github(base_url=self.base_url).get_repo(owner if isinstance(owner, int) else f"{owner}/{repo}")
        if sha is None:
            sha = self._repo.default_branch
        self._sha = sha
        self._session = Session()  # TODO use sdk
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:  # TODO pagination
        for element in self._repo.get_git_tree(self._sha, True).tree:
            if element.type == "blob":
                yield File(element.path, size=element.size)

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(
                self.FMT_RAW_URL.format(self.raw_host, self._repo.full_name, self._sha, file.path),
                stream=True,
            ),
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError


class GiteaGithubStorage(GithubStorage):
    FMT_RAW_URL = "{}/{}/raw/branch/{}/{}"

    def __init__(self, url: str, owner: int | str, repo: str = "", sha: str | None = None):
        self.base_url = url + "/api/v1"
        self.raw_host = url
        super().__init__(owner, repo, sha)
