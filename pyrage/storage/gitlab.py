from typing import Iterable, Optional

from gitlab import Gitlab
from gitlab.utils import EncodedId

from ..utils import File, Readable, ReadableResponse
from . import Storage


class GitlabStorage(Storage):
    def __init__(
        self,
        owner: int | str,
        repo: str = "",
        ref: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self._repo = Gitlab(url).projects.get(
            owner if isinstance(owner, int) else f"{owner}/{repo}"
        )
        if ref is None:
            ref = self._repo.default_branch
        self._ref = ref
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for element in self._repo.repository_tree(
            ref=self._ref, recursive=True, iterator=True, get_all=True
        ):
            if "blob" == element["type"]:
                yield File(element["path"])

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._repo.manager.gitlab.http_get(
                f"{self._repo.files.path}/{EncodedId(file.path)}/raw",
                {"ref": self._ref},
                True,
            )
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
