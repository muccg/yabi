import logging
from yabiadmin.backend.sshbackend import SSHBackend
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.yabiengine.urihelper import uriparse

logger = logging.getLogger(__name__)


class SchedulerExecBackend(SSHBackend):
    """
    A _abstract_ backend which allows job submission via qsub
    """
    SCHEDULER_NAME = ""
    QSUB_TEMPLATE = "\n".join(["#!/bin/sh",
                    'script_temp_file_name="{0}"',
                    "cat<<EOS>$script_temp_file_name",
                    "{1}",
                    "EOS",
                    "qsub $script_temp_file_name"])

    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "qstat -f -1 {0}"])

    def __init__(self, *args, **kwargs):
        super(SchedulerExecBackend, self).__init__(*args, **kwargs)
        self.parser = None

    def submit_task(self):
        qsub_result = self._run_qsub()
        if qsub_result.status == qsub_result.JOB_SUBMITTED:
            self.task.remote_id = qsub_result.remote_id
            self.task.save()
            logger.debug("Yabi Task {0} submitted to {1} OK. remote id = {2}".format(self.task.pk,
                                                                                     self.SCHEDULER_NAME,
                                                                                     self.task.remote_id))
        else:
            raise Exception("Error submitting remote job to {0} for yabi task {1} {2}".format(self.SCHEDULER_NAME,
                                                                                              self.task.pk,
                                                                                              qsub_result.status))

    def _run_qsub(self):
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())
        submission_script_name = self._generate_remote_script_name()
        logger.debug("creating qsub script %s" % submission_script_name)
        submission_script_body = self.get_submission_script(exec_parts.hostname, working_parts.path)
        qsub_script_body = self.QSUB_TEMPLATE.format(submission_script_name, submission_script_body)
        logger.debug("qsub script:\n%s" % qsub_script_body)
        stdout, stderr = self._exec_script(qsub_script_body)
        qsub_result = self.parser.parse_qsub(stdout, stderr)
        return qsub_result

    def _get_polling_script(self):
        return self.QSTAT_TEMPLATE.format(self.task.remote_id)

    def _run_qstat(self):
        qstat_command = self._get_polling_script()
        stdout, stderr = self._exec_script(qstat_command)
        qstat_result = self.parser.parse_qstat(self.task.remote_id, stdout, stderr)
        return qstat_result

    def poll_task_status(self):
        qstat_result = self._run_qstat()

        if qstat_result.status == qstat_result.JOB_RUNNING:
            logger.debug("remote job %s for yabi task %s is stilling running" % (self.task.remote_id, self.task))
            # cause retry of polling task ( not sure if this is the best
            retry_ex = RetryException("remote job %s still running" % self.task.remote_id)
            retry_ex.backoff_strategy = RetryException.BACKOFF_STRATEGY_CONSTANT
            raise retry_ex

        elif qstat_result.status == qstat_result.JOB_NOT_FOUND:
            logger.debug("qstat for remote job %s did not produce results" % self.task.remote_id)
            # For Torque this is an error
            raise Exception("Remote job %s for Yabi task %s not found by qstat" % (self.task.remote_id, self.task.pk))

        elif qstat_result.status == qstat_result.JOB_SUCCEEDED:
            logger.debug("yabi task %s succeeded" % self.task.pk)

        elif qstat_result.status == qstat_result.JOB_FAILED:
            logger.debug("remote job for yabi task %s failed" % self.task.pk)
            # how to cause a job resubmission?
            raise Exception("Yabi task %s failed remotely" % self.task.pk)
        else:
            raise Exception("Yabi task %s unknown state: %s" % (self.task.pk, qstat_result.status))

