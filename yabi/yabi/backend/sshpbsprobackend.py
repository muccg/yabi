from yabi.backend.baseexecbackend import BaseExecBackend
from yabi.backend.pbsproparsers import PBSProParser


class SSHPBSProExecBackend(BaseExecBackend):
    SCHEDULER_NAME = "PBS Pro"
    STAT_TEMPLATE = "\n".join(["#!/bin/sh",
                               "<STAT_COMMAND> -x {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHPBSProExecBackend, self).__init__(*args, **kwargs)
        self.parser = PBSProParser()

    def _job_not_found_response(self, stat_result):
        raise Exception("Remote job %s for Yabi task %s not found by qstat" % (self.task.remote_id, self._yabi_task_name()))
