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

from yabi.backend.basewithacctexecbackend import BaseWithAcctExecBackend
from yabi.backend.slurmparsers import SlurmParser


class SSHSlurmBackend(BaseWithAcctExecBackend):
    SCHEDULER_NAME = "slurm"

    SUB_COMMAND_NAME = "sbatch"
    STAT_COMMAND_NAME = "squeue"
    ACCT_COMMAND_NAME = "sacct"
    CANCEL_COMMAND_NAME = "scancel"

    SUB_COMMAND_LINE = "<SUB_COMMAND> -J {3} $script_temp_file_name"

    STAT_TEMPLATE = "\n".join(["#!/bin/sh", "<STAT_COMMAND> -h --jobs {0}"])

    ACCT_TEMPLATE = "\n".join([
                    "#!/bin/sh",
                    "<ACCT_COMMAND> -n -o J --jobs {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHSlurmBackend, self).__init__(*args, **kwargs)
        self.parser = SlurmParser()
