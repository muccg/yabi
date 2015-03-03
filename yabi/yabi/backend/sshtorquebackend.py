from yabi.backend.baseexecbackend import BaseExecBackend
from yabi.backend.torqueparsers import TorqueParser
from yabi.backend.exceptions import JobNotFoundException


class SSHTorqueExecBackend(BaseExecBackend):
    SCHEDULER_NAME = "torque"
    STAT_TEMPLATE = "\n".join(["#!/bin/sh",
                               "<STAT_COMMAND> -f -1 {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHTorqueExecBackend, self).__init__(*args, **kwargs)
        self.parser = TorqueParser()

    def _job_not_found_response(self, qstat_result):
        raise JobNotFoundException("Remote job %s for Yabi task %s not found by qstat" % (self.task.remote_id, self._yabi_task_name()))
