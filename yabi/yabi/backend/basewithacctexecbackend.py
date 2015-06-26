from yabi.backend.baseexecbackend import BaseExecBackend
from yabi.backend.exceptions import JobNotFoundException
import logging
logger = logging.getLogger(__name__)


class BaseWithAcctExecBackend(BaseExecBackend):

    def _run_acct(self):
        script = self.ACCT_TEMPLATE.format(self.task.remote_id).replace("<ACCT_COMMAND>", self.get_scheduler_command_path(self.ACCT_COMMAND_NAME))
        exit_code, stdout, stderr = self.executer.exec_script(script)
        return self.parser.parse_acct(self.task.remote_id, exit_code, stdout, stderr)

    def _job_not_found_response(self, stat_result):
        logger.debug("%s for yabi task %s remote job %s did not produce results - trying %s ..." % (self.STAT_COMMAND_NAME, self._yabi_task_name(), self.task.remote_id, self.ACCT_COMMAND_NAME))
        acct_result = self._run_acct()
        if acct_result.status == acct_result.JOB_COMPLETED:
            logger.debug("yabi task %s remote id %s succeeded" % (self._yabi_task_name(), self.task.remote_id))
        else:
            # Not found in acct either ..
            raise JobNotFoundException("Remote job %s for Yabi task %s not found by %s and %s" % (self.task.remote_id, self._yabi_task_name(), self.STAT_COMMAND_NAME, self.ACCT_COMMAND_NAME))
