from sqlite3 import connect
from typing import Iterator

from . import FileListMapping
from ....utils import File


class SqliteFileListMapping(FileListMapping):
    def __init__(self, *args, mapping_path: str = ":memory:", **kwargs):
        self._mapping = connect(mapping_path)
        self._mapping.execute(
            """
            CREATE TABLE IF NOT EXISTS _ (
                path TEXT PRIMARY KEY NOT NULL,
                size INTEGER,
                mtime REAL,
                atime REAL,
                ctime REAL,
                md5 VARCHAR(32)
            );
            """
        )
        self.clear()
        super().__init__(*args, **kwargs)
        self._file_list = self

    def __del__(self):
        super().__del__()
        self._mapping.close()

    def __contains__(self, key: str) -> bool:
        return bool(
            self._mapping.execute(
                """
                SELECT EXISTS(SELECT 1 FROM _ WHERE path = ?);
                """,
                (key,),
            ).fetchone()[0]
        )

    def __len__(self):
        return self._mapping.execute(
            """
            SELECT COUNT(*) FROM _;
            """
        ).fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        return (
            row[0]
            for row in self._mapping.execute(
                """
                SELECT path FROM _;
                """
            )
        )

    def __getitem__(self, key: str) -> File:
        value = self._mapping.execute(
            """
            SELECT * FROM _ WHERE path = ?;
            """,
            (key,),
        ).fetchone()
        if value is None:
            raise KeyError(key)
        return File(*value)

    def __setitem__(self, key: str, value: File):
        self._mapping.execute(
            """
            INSERT OR REPLACE INTO _ (path, size, mtime, atime, ctime, md5)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            value,
        )

    def __delitem__(self, key: str):
        if key not in self:
            raise KeyError(key)
        self._mapping.execute(
            """
            DELETE FROM _ WHERE path = ?;
            """,
            (key,),
        )

    def clear(self):
        self._mapping.execute(
            """
            DELETE FROM _;
            """
        )
