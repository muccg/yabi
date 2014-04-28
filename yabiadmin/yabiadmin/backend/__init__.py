# Import all backend class in this module so they get registered

from .basebackend import BaseBackend

# file system backends
from .fsbackend import FSBackend
from .selectfilebackend import SelectFileBackend
from .filebackend import FileBackend
from .sftpbackend import SFTPBackend
from .s3backend import S3Backend
from .swiftbackend import SwiftBackend

# execution backends
from .execbackend import ExecBackend
from .selectfileexecbackend import SelectFileExecBackend
from .localexecbackend import LocalExecBackend
from .sshbackend import SSHBackend
from .sshsgeexecbackend import SSHSGEExecBackend
from .sshtorquebackend import SSHTorqueExecBackend
from .sshpbsprobackend import SSHPBSProExecBackend
