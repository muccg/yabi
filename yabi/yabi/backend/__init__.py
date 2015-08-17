# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Re-import all backend classes and register their schemes

from .basebackend import BaseBackend  # NOQA

# file system backends
from .fsbackend import FSBackend  # NOQA
from .selectfilebackend import SelectFileBackend
from .filebackend import FileBackend
from .sftpbackend import SFTPBackend
from .s3backend import S3Backend
from .swiftbackend import SwiftBackend

# execution backends
from .execbackend import ExecBackend  # NOQA
from .selectfileexecbackend import SelectFileExecBackend
from .localexecbackend import LocalExecBackend
from .sshbackend import SSHBackend
from .sshsgeexecbackend import SSHSGEExecBackend
from .sshugeexecbackend import SSHUGEExecBackend
from .sshtorquebackend import SSHTorqueExecBackend
from .sshpbsprobackend import SSHPBSProExecBackend
from .sshslurmbackend import SSHSlurmBackend

# Register backend schemes
SelectFileExecBackend.register("selectfile", "null")
LocalExecBackend.register("localex")
SSHBackend.register("ssh")
SSHSGEExecBackend.register("ssh+sge")
SSHUGEExecBackend.register("ssh+uge")
SSHTorqueExecBackend.register("ssh+torque")
SSHPBSProExecBackend.register("ssh+pbspro")
SSHSlurmBackend.register("ssh+slurm")
SelectFileBackend.register("selectfile", "null")
FileBackend.register("file", "localfs")
SFTPBackend.register("sftp", "scp")
S3Backend.register("s3")
SwiftBackend.register("swift")
