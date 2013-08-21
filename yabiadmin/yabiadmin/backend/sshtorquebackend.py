from yabiadmin.backend.schedulerexecbackend import SchedulerExecBackend
from yabiadmin.backend.torqueparsers import TorqueParser


class SSHTorqueExecBackend(SchedulerExecBackend):
    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "qstat -f -1 {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHTorqueExecBackend, self).__init__(*args, **kwargs)
        self.parser = TorqueParser()

    def _job_not_found_response(self, qstat_result):
        raise Exception("Remote job %s for Yabi task %s not found by qstat" % (self.task.remote_id, self._yabi_task_name()))