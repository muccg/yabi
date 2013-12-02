from yabiadmin.backend.qbaseexecbackend import QBaseExecBackend
from yabiadmin.backend.sgeparsers import SGEParser, SGEQAcctResult
from yabiadmin.backend.exceptions import JobNotFoundException
import logging
logger = logging.getLogger(__name__)


class SSHSGEExecBackend(QBaseExecBackend):
    SCHEDULER_NAME = "sge"
    QSUB_COMMAND_LINE = "<QSUB_COMMAND> -N {3} -cwd $script_temp_file_name"

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
        exit_code, stdout, stderr = self.executer.exec_script(script)
        return self.parser.parse_qacct(self.task.remote_id, exit_code, stdout, stderr)

    def _job_not_found_response(self, qstat_result):
        logger.debug("qstat for yabi task %s remote job %s did not produce results - trying qacct ..." % (self._yabi_task_name(), self.task.remote_id))
        qacct_result = self._run_qacct()
        if qacct_result.status == SGEQAcctResult.JOB_COMPLETED:
            logger.debug("yabi task %s remote id %s succeeded" % (self._yabi_task_name(), self.task.remote_id))
        else:
            # Not found in qacct either ..
            raise JobNotFoundException("Remote job %s for Yabi task %s not found by qstat and qacct" % (self.task.remote_id, self._yabi_task_name()))

