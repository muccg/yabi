from yabiadmin.backend.basewithacctexecbackend import BaseWithAcctExecBackend
from yabiadmin.backend.slurmparsers import SlurmParser


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
