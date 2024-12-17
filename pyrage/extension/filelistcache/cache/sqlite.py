from itertools import starmap
from sqlite3 import connect
from typing import Iterator

from . import FileListCache
from ....utils import File


class SqliteFileListCache(FileListCache):
    EXTENSION = "db"

    def _dump(self, files: Iterator[File]):
        with connect(self.path) as con:
            cur = con.cursor()
            cur.execute(
                """
                DROP TABLE IF EXISTS _;
                """
            )
            cur.execute(
                """
                CREATE TABLE _ (
                    path TEXT PRIMARY KEY NOT NULL,
                    size INTEGER,
                    mtime REAL,
                    atime REAL,
                    ctime REAL,
                    crc32 VARCHAR(8),
                    md5 VARCHAR(32),
                    sha1 VARCHAR(40)
                );
                """
            )
            cur.executemany(
                """
                INSERT INTO _ (path, size, mtime, atime, ctime, crc32, md5, sha1)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                files,
            )
            cur.close()
        con.close()

    def _load(self) -> Iterator[File]:
        with connect(self.path) as con:
            yield from starmap(
                File,
                con.execute(
                    """
                    SELECT * FROM _;
                    """
                ),
            )
        con.close()
