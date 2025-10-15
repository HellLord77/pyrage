from sqlite3 import connect
from typing import Iterator, Optional

from ....utils import File
from . import FileListMapping


class SqliteFileListMapping(FileListMapping):
    def __init__(self, database: Optional[str] = None):
        if database is None:
            database = ":memory:"
        self._mapping = connect(database)
        self._mapping.execute(
            """
            CREATE TABLE IF NOT EXISTS _ (
                path TEXT PRIMARY KEY NOT NULL,
                size INTEGER,
                mtime REAL,
                atime REAL,
                ctime REAL,
                crc32 VARCHAR(8),
                md5 VARCHAR(32),
                sha1 VARCHAR(40),
                sha256 VARCHAR(64)
            );
            """
        )
        super().__init__()

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
            INSERT OR REPLACE INTO _ (path, size, mtime, atime, ctime, crc32, md5, sha1, sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
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
