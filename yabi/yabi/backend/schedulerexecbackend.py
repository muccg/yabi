# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from yabi.backend.execbackend import ExecBackend
from yabi.backend.sshexec import SSHExec
from yabi.backend.exceptions import RetryPollingException
from yabi.yabiengine.urihelper import uriparse
from yabi.yabiengine.engine_logging import create_task_logger


logger = logging.getLogger(__name__)


class SchedulerExecBackend(ExecBackend):
    """
    A _abstract_ backend which allows job submissions
    """
    SCHEDULER_NAME = ""
    backend_auth = ExecBackend.SSH_AUTH

    def __init__(self, *args, **kwargs):
        super(SchedulerExecBackend, self).__init__(*args, **kwargs)
        self.executer = SSHExec()
        self.parser = None
        self.submission_script_name = None
        self.submission_script_body = None
        self.working_dir = None
        self._task = None
        self._cred = None
        self._backend = None
        self.task_logger = logger

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, val):
        self._task = val
        self.executer.uri = self._task.job.exec_backend
        self.task_logger = create_task_logger(logger, self._task.pk)

    @property
    def cred(self):
        return self._cred

    @cred.setter
    def cred(self, val):
        self._cred = val
        self.executer.credential = self._cred.credential

    @property
    def backend(self):
        return self._backend

    @backend.setter
    def backend(self, val):
        self._backend = val
        self.executer.tmp_dir = self._backend.temporary_directory

    def submit_task(self):
        result = self._submit_job()
        if result.status == result.JOB_SUBMITTED:
            self._job_submitted_response(result)
        else:
            self._job_not_submitted_response(result)

    def poll_task_status(self):
        result = self._poll_job_status()
        if result.status == result.JOB_RUNNING:
            self._job_running_response(result)
        elif result.status == result.JOB_NOT_FOUND:
            self.task_logger.info("polling of status for remote job %s of yabi task %s did not produce results", self.task.remote_id, self._yabi_task_name())
            self._job_not_found_response(result)
        elif result.status == result.JOB_COMPLETED:
            self._job_completed_response(result)
        else:
            self._unknown_job_status_response(result)

    def abort_task(self):
        result = self._abort_job()
        if result.status == result.JOB_FINISHED:
            self.task_logger.info("trying to abort an already finished job. Remote job %s, yabi task %s", self.task.remote_id, self._yabi_task_name())
        elif result.status == result.JOB_ABORTION_ERROR:
            self._job_abortion_error_response(result)
        elif result.status == result.JOB_ABORTED:
            self._job_aborted_response(result)
        else:
            self._unknown_job_status_response(result)

    def _get_submission_wrapper_script(self):
        raise NotImplementedError()

    def _get_polling_script(self):
        raise NotImplementedError()

    def _get_abort_script(self):
        raise NotImplementedError()

    def _submit_job(self):
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())
        self.working_dir = working_parts.path
        self.submission_script_name = self.executer.generate_remote_script_name()
        self.task.job_identifier = self.submission_script_name
        self.task.save()
        self.task_logger.info("Creating submission script %s" % self.submission_script_name)
        self.submission_script_body = self.get_submission_script(exec_parts.hostname, self.working_dir)
        wrapper_script = self._get_submission_wrapper_script()
        self.task_logger.info("Executing script:\n\n%s" % wrapper_script)
        exit_code, stdout, stderr = self.executer.exec_script(wrapper_script)
        result = self.parser.parse_sub(exit_code, stdout, stderr)
        if result.status != result.JOB_SUBMITTED:
            self.task_logger.error("Yabi Task Name = %s" % self._yabi_task_name())
            self.task_logger.error("Submission script name = %s" % self.submission_script_name)
            self.task_logger.error("Submission script body = %s" % self.submission_script_body)
            self.task_logger.error("stderr:\n")
            lines = "\n".join(stderr)
            self.task_logger.error(lines)
        return result

    def _job_submitted_response(self, result):
        self.task.remote_id = result.remote_id
        self.task.save()
        self.task_logger.info("Yabi Task {0} submitted to {1} OK. remote id = {2}".format(
            self._yabi_task_name(),
            self.SCHEDULER_NAME,
            self.task.remote_id))

    def _job_not_submitted_response(self, result):
        raise Exception("Error submitting remote job to {0} for yabi task {1} {2}".format(self.SCHEDULER_NAME,
                                                                                          self._yabi_task_name(),
                                                                                          result.status))

    def _yabi_task_name(self):
        # NB. No hyphens - these got rejected by PBS Pro initially
        # NB. 15 character limit also.
        return "Y{0}".format(self.task.pk)[:15]

    def _poll_job_status(self):
        polling_script = self._get_polling_script()
        exit_code, stdout, stderr = self.executer.exec_script(polling_script)
        result = self.parser.parse_poll(self.task.remote_id, exit_code, stdout, stderr)
        return result

    def _job_running_response(self, result):
        self.task_logger.debug("remote job %s for yabi task %s is still running" % (self.task.remote_id, self._yabi_task_name()))
        raise RetryPollingException("Yabi task %s remote job %s still running" % (self._yabi_task_name(), self.task.remote_id))

    def _job_not_found_response(self, result):
        # NB. for psbpro and torque this is an error, for other subclasses it isn't
        raise NotImplementedError()

    def _job_completed_response(self, result):
        self.task_logger.debug("yabi task %s remote id %s completed" % (self._yabi_task_name(), self.task.remote_id))

    def _unknown_job_status_response(self, result):
        raise Exception("Yabi task %s unknown state: %s" % (self._yabi_task_name(), result.status))

    def _abort_job(self):
        abort_script = self._get_abort_script()
        self.task_logger.info("Execution abort script:\n\n%s", abort_script)
        exit_code, stdout, stderr = self.executer.exec_script(abort_script)
        result = self.parser.parse_abort(self.task.remote_id, exit_code, stdout, stderr)
        return result

    def _job_abortion_error_response(self, result):
        self.task_logger.error("couldn't abort job %s for yabi task %s. STDERR was: \n%s",
                               self.task.remote_id, self._yabi_task_name(), result.error)
        raise Exception("couldn't abort job %s for yabi task %s" % (
                        self.task.remote_id, self._yabi_task_name()))

    def _job_aborted_response(self, result):
        self.task_logger.error("Aborted job %s for yabi task %s.",
                               self.task.remote_id, self._yabi_task_name())
