from .storage.local import LocalStorage
from .storage.tar import TarStorage
from .storage.zip import ZipStorage

from .storage.ddl import DDLStorage
from .storage.dropbox import DropboxStorage
from .storage.ftp import FTPStorage
from .storage.git import GitStorage
from .storage.gitea import GiteaStorage
from .storage.github import GithubStorage
from .storage.gitlab import GitlabStorage
from .storage.internetarchive import InternetArchiveStorage
from .storage.mongo import MongoStorage
from .storage.s3 import MinIOS3Storage as MinIOStorage
from .storage.s3 import S3Storage
from .storage.sftp import SFTPStorage
from .storage.smb import SMBStorage
from .storage.webdav import WebDAVStorage

from .utils import File
from .utils import Readable
from .utils import Writable
