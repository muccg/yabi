# Re-import all backend classes and register their schemes

# file system backends
from .selectfilebackend import SelectFileBackend
from .filebackend import FileBackend
from .sftpbackend import SFTPBackend
from .s3backend import S3Backend
from .swiftbackend import SwiftBackend

# execution backends
from .selectfileexecbackend import SelectFileExecBackend
from .localexecbackend import LocalExecBackend
from .sshbackend import SSHBackend
from .sshsgeexecbackend import SSHSGEExecBackend
from .sshtorquebackend import SSHTorqueExecBackend
from .sshpbsprobackend import SSHPBSProExecBackend

# Register backend schemes
SelectFileExecBackend.register("selectfile", "null")
LocalExecBackend.register("localex")
SSHBackend.register("ssh")
SSHSGEExecBackend.register("ssh+sge")
SSHTorqueExecBackend.register("ssh+torque")
SSHPBSProExecBackend.register("ssh+pbspro")
SelectFileBackend.register("selectfile", "null")
FileBackend.register("file", "localfs")
SFTPBackend.register("sftp", "scp")
S3Backend.register("s3")
SwiftBackend.register("swift")
