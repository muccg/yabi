from yabiadmin.backend.basewithacctexecbackend import BaseWithAcctExecBackend
from yabiadmin.backend.sgeparsers import SGEParser


class SSHSGEExecBackend(BaseWithAcctExecBackend):
    SCHEDULER_NAME = "sge"

    ACCT_COMMAND_NAME = "qacct"

    SUB_COMMAND_LINE = "<SUB_COMMAND> -N {3} -cwd $script_temp_file_name"

    STAT_TEMPLATE = "\n".join(["#!/bin/sh", "<STAT_COMMAND> -j {0}"])

    ACCT_TEMPLATE = "\n".join([
                    "#!/bin/sh",
                    "<ACCT_COMMAND> -j {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHSGEExecBackend, self).__init__(*args, **kwargs)
        self.parser = SGEParser()
