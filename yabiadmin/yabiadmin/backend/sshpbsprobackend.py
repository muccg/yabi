import logging
from yabiadmin.backend.sshbackend import SSHBackend
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.backend.pbsproparsers import *
from yabiadmin.backend.exceptions import RetryException

logger = logging.getLogger(__name__)


class SSHPBSProExecBackend(SSHBackend):
    QSUB_TEMPLATE = "\n".join(["#!/bin/sh",
                    'script_temp_file_name="{0}"',
                    "cat<<EOS>$script_temp_file_name",
                    "{1}",
                    "EOS",
                    "qsub $script_temp_file_name"])

    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "qstat -x {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHPBSProExecBackend, self).__init__(*args, **kwargs)
        self.parser = PBSProParser()


    def submit_task(self):
        logger.debug("SSHPBSProExecBackend.submit_task ...")
        qsub_result = self._run_qsub()

        if qsub_result.status == qsub_result.JOB_SUBMITTED:
            self.task.remote_id = qsub_result.remote_id
            self.task.save()
            logger.debug("Yabi Task %s submitted to PBSPro OK. remote id = %s" % (self.task.pk, self.task.remote_id))
        else:
            raise Exception("Error submitting remote job to PBSPro for yabi task %s %s" % (self.task.pk, qsub_result.status))

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

    def poll_task_status(self):
        pass
