import logging
import os
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
                    "qsub -N {4} -o '{2}' -e '{3}' $script_temp_file_name"])

    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "qstat -f -1 {0}"])

    def __init__(self, *args, **kwargs):
        super(SchedulerExecBackend, self).__init__(*args, **kwargs)
        self.parser = None
        self.submission_script_name = None
        self.submission_script_body = None
        self.qsub_script_body = None
        self.stdout_file = None
        self.stderr_file = None

    def _yabi_task_name(self):
        # NB. No hyphens - these got rejected by PBS Pro initially
        # NB. 15 character limit also.
        return "Y{0}".format(self.task.pk)[:15]

    def submit_task(self):
        qsub_result = self._run_qsub()
        if qsub_result.status == qsub_result.JOB_SUBMITTED:
            self._job_submitted_response(qsub_result)
        else:
            self._job_not_submitted_response(qsub_result)


    def _job_submitted_response(self, qsub_result):
        self.task.remote_id = qsub_result.remote_id
        self.task.save()
        logger.info("Yabi Task {0} submitted to {1} OK. remote id = {2}".format(self._yabi_task_name(),
                                                                                     self.SCHEDULER_NAME,
                                                                                     self.task.remote_id))

    def _job_not_submitted_response(self, qsub_result):
        raise Exception("Error submitting remote job to {0} for yabi task {1} {2}".format(self.SCHEDULER_NAME,
                                                                                          self._yabi_task_name(),
                                                                                          qsub_result.status))

    def _run_qsub(self):
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())
        self.submission_script_name = self._generate_remote_script_name()
        logger.debug("creating qsub script %s" % self.submission_script_name)
        self.submission_script_body = self.get_submission_script(exec_parts.hostname, working_parts.path)
        self.stdout_file = os.path.join(working_parts.path, "STDOUT.txt")
        self.stderr_file = os.path.join(working_parts.path, "STDERR.txt")
        self.qsub_script_body = self._get_qsub_body()
        logger.debug("qsub script:\n%s" % self.qsub_script_body)
        stdout, stderr = self._exec_script(self.qsub_script_body)
        qsub_result = self.parser.parse_qsub(stdout, stderr)
        if qsub_result.status != qsub_result.JOB_SUBMITTED:
            for line in stderr:
                logger.debug("Error submitting Yabi Task %s: %s" % (self._yabi_task_name(), line))
        return qsub_result

    def _get_qsub_body(self):
        return self.QSUB_TEMPLATE.format(
            self.submission_script_name, self.submission_script_body,
            self.stdout_file, self.stderr_file, self._yabi_task_name())

    def _get_polling_script(self):
        return self.QSTAT_TEMPLATE.format(self.task.remote_id)

    def _run_qstat(self):
        qstat_command = self._get_polling_script()
        stdout, stderr = self._exec_script(qstat_command)
        qstat_result = self.parser.parse_qstat(self.task.remote_id, stdout, stderr)
        return qstat_result

    def _job_running_response(self, qstat_result):
        logger.debug("remote job %s for yabi task %s is stilling running" % (self.task.remote_id, self._yabi_task_name()))
        retry_ex = RetryException("Yabi task %s remote job %s still running" % (self._yabi_task_name(), self.task.remote_id))
        retry_ex.backoff_strategy = RetryException.BACKOFF_STRATEGY_CONSTANT
        raise retry_ex

    def _job_not_found_response(self, qstat_result):
        # NB. for psbpro and torque this is an error, for other subclasses it isn't
        raise NotImplementedError()

    def _job_completed_response(self, qstat_result):
        logger.debug("yabi task %s remote id %s completed" % (self._yabi_task_name(), self.task.remote_id))

    def _unknown_job_status_response(self, qstat_result):
        raise Exception("Yabi task %s unknown state: %s" % (self._yabi_task_name(), qstat_result.status))

    def poll_task_status(self):
        qstat_result = self._run_qstat()
        if qstat_result.status == qstat_result.JOB_RUNNING:
            self._job_running_response(qstat_result)
        elif qstat_result.status == qstat_result.JOB_NOT_FOUND:
            logger.info("qstat for remote job %s of yabi task %s did not produce results" % (self.task.remote_id,
                                                                                             self._yabi_task_name()))
            self._job_not_found_response(qstat_result)
        elif qstat_result.status == qstat_result.JOB_COMPLETED:
            self._job_completed_response(qstat_result)
        else:
            self._unknown_job_status_response(qstat_result)