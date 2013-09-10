from yabiadmin.backend.schedulerexecbackend import SchedulerExecBackend
from yabiadmin.backend.sgeparsers import SGEParser, SGEQAcctResult
import logging
logger = logging.getLogger(__name__)


class SSHSGEExecBackend(SchedulerExecBackend):
    SCHEDULER_NAME = "sge"
    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "qstat -j {0}"])

    QACCT_TEMPLATE = "\n".join([
                     "#!/bin/sh",
                     "<QACCT_COMMAND> -j {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHSGEExecBackend, self).__init__(*args, **kwargs)
        self.parser = SGEParser()

    def _run_qacct(self):
        script = SSHSGEExecBackend.QACCT_TEMPLATE.format(self.task.remote_id).replace("<QACCT_COMMAND>",self.get_scheduler_command_path("qacct"))
        stdout, stderr = self._exec_script(script)
        return self.parser.parse_qacct(self.task.remote_id, stdout, stderr)

    def _job_not_found_response(self, qstat_result):
        logger.debug("qstat for yabi task %s remote job %s did not produce results - trying qacct ..." % (self._yabi_task_name(), self.task.remote_id))
        qacct_result = self._run_qacct()
        if qacct_result.status == SGEQAcctResult.JOB_COMPLETED:
            logger.debug("yabi task %s remote id %s succeeded" % (self._yabi_task_name(), self.task.remote_id))
        else:
            # Not found in qacct either ..
            raise Exception("Remote job %s for Yabi task %s not found by qstat" % (self.task.remote_id, self._yabi_task_name()))



