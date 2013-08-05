import logging
from yabiadmin.backend.sshbackend import SSHBackend
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.backend.sgeparsers import SGEParser,SGEQSubResult, SGEQStatResult, SGEQAcctResult
import textwrap
logger = logging.getLogger(__name__)

from yabiadmin.backend.exceptions import RetryException

class SubmissionError(Exception):
    pass

class SSHSGEExecBackend(SSHBackend):
    QSUB_TEMPLATE = "\n".join(["#!/bin/sh",
                    'script_temp_file_name="{0}"',
                    "cat<<EOS>$script_temp_file_name",
                    "{1}",
                    "EOS",
                    "qsub $script_temp_file_name"])

    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "qstat -j {0}"])

    QACCT_TEMPLATE = "\n".join([
                     "#!/bin/sh",
                     "qacct -j {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHSGEExecBackend, self).__init__(*args, **kwargs)
        self.parser = SGEParser()


    def submit_task(self):
        logger.debug("SSHSGEExecBackend.submit_task ...")
        qsub_result = self._run_qsub()

        if qsub_result.status == qsub_result.JOB_SUBMITTED:
            self.task.remote_id = qsub_result.remote_id
            self.task.save()
            logger.debug("Yabi Task %s submitted to SGE OK. remote id = %s" % (self.task.pk, self.task.remote_id))
        else:
            raise Exception("Error submitting remote job for yabi task %s %s" % (self.task.pk, qsub_result.status))

    def _run_qsub(self):
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())
        submission_script_name = self._generate_remote_script_name()
        logger.debug("creating qsub script %s" % submission_script_name)
        submission_script_body = self.get_submission_script(exec_parts.hostname, working_parts.path)
        qsub_script_body = SSHSGEExecBackend.QSUB_TEMPLATE.format(submission_script_name, submission_script_body)
        logger.debug("qsub script:\n%s" % qsub_script_body)
        stdout, stderr = self._exec_script(qsub_script_body)
        qsub_result = self.parser.parse_qsub(stdout, stderr)
        return qsub_result

    def _get_qsub_script_body(self,submission_script_name, submission_script_body):
        return SSHSGEExecBackend.QSUB_TEMPLATE.format(submission_script_name, submission_script_body)


    def _run_qstat(self):
        qstat_command = self._get_polling_script()
        stdout, stderr = self._exec_script(qstat_command)
        qstat_result = self.parser.parse_qstat(self.task.remote_id, stdout, stderr)
        return qstat_result


    def _run_qacct(self):
        script = SSHSGEExecBackend.QACCT_TEMPLATE.format(self.task.remote_id)
        stdout, stderr = self._exec_script(script)
        return self.parser.parse_qacct(self.task.remote_id, stdout, stderr)


    def _get_polling_script(self):
        return SSHSGEExecBackend.QSTAT_TEMPLATE.format(self.task.remote_id)

    def poll_task_status(self):
        qstat_result = self._run_qstat()

        if qstat_result.status == SGEQStatResult.JOB_RUNNING:
            logger.debug("remote job %s for yabi task %s is stilling running" % (self.task.remote_id, self.task))
            # cause retry of polling task ( not sure if this is the best
            raise RetryException("remote job %s still running" % self.task.remote_id)

        elif qstat_result.status == SGEQStatResult.JOB_NOT_FOUND:
            logger.debug("qstat for remote job %s did not produce results - trying qacct ..." % self.task.remote_id)

            qacct_result = self._run_qacct()
            if qacct_result.status == SGEQAcctResult.JOB_SUCCEEDED:
                logger.debug("yabi task %s succeeded" % self.task.pk)

            elif qacct_result.status == SGEQAcctResult.JOB_FAILED:
                logger.debug("remote job for yabi task %s failed" % self.task.pk)
                # how to cause a job resubmission?
                raise Exception("Yabi task %s failed remotely" % self.task.pk)

            elif qacct_result.status == SGEQAcctResult.JOB_NOT_FOUND:
                logger.debug("remote job for yabi task %s not found by qacct?!" % self.task.pk)
                # what to do here?
                raise Exception("Cannot find remote job for yabi task %s" % self.task.pk)



