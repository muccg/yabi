from yabi.backend.basewithacctexecbackend import BaseWithAcctExecBackend
from yabi.backend.sgeparsers import SGEParser


class SSHSGEBasedExecBackend(BaseWithAcctExecBackend):
    ACCT_COMMAND_NAME = "qacct"

    SUB_COMMAND_LINE = "<SUB_COMMAND> -N {3} -cwd $script_temp_file_name"

    STAT_TEMPLATE = "\n".join(["#!/bin/sh", "<STAT_COMMAND> -j {0}"])

    ACCT_TEMPLATE = "\n".join([
                    "#!/bin/sh",
                    "<ACCT_COMMAND> -j {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHSGEBasedExecBackend, self).__init__(*args, **kwargs)
        self.parser = SGEParser()
