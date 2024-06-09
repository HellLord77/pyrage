from github import Github
from github.Consts import DEFAULT_BASE_URL
from requests import Session

from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable
from pyrage.utils import ReadableResponse


class GithubStorage(Storage):
    FMT_RAW_URL = "{}/{}/{}/{}"

    base_url = DEFAULT_BASE_URL
    raw_host = "https://raw.githubusercontent.com"

    def __init__(self, owner: int | str, repo: str = "", sha: str = "main"):
        self._repo = Github(base_url=self.base_url).get_repo(
            owner if isinstance(owner, int) else f"{owner}/{repo}"
        )
        self._sha = sha
        self._session = Session()
        super().__init__()

    def _update_file_list(self):  # TODO pagination
        for element in self._repo.get_git_tree(self._sha, True).tree:
            if "blob" == element.type:
                self._add_file_list(File(element.path, size=element.size))

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(
                self.FMT_RAW_URL.format(
                    self.raw_host, self._repo.full_name, self._sha, file.path
                ),
                stream=True,
            )
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError


class GiteaStorage(GithubStorage):
    FMT_RAW_URL = "{}/{}/raw/branch/{}/{}"

    def __init__(self, url: str, owner: int | str, repo: str = "", sha: str = "main"):
        self.base_url = url + "/api/v1"
        self.raw_host = url
        super().__init__(owner, repo, sha)
