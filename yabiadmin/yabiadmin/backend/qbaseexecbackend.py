import logging
from yabiadmin.backend.schedulerexecbackend import SchedulerExecBackend
import django
logger = logging.getLogger(__name__)


class QBaseExecBackend(SchedulerExecBackend):
    """
    A _abstract_ backend which allows job submission via qsub
    """
    QSUB_TEMPLATE = "\n".join(["#!/bin/sh",
                    'script_temp_file_name="{0}"',
                    "cat<<EOS>$script_temp_file_name",
                    "{1}",
                    "EOS",
                    "<QSUB_COMMAND> -N {4} -o '{2}' -e '{3}' $script_temp_file_name"])

    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh",
                                "<QSTAT_COMMAND> -f -1 {0}"])


    def get_scheduler_command_path(self, scheduler_command):
        from django.conf import settings
        if hasattr(settings, "SCHEDULER_COMMAND_PATHS"):
            if settings.SCHEDULER_COMMAND_PATHS.has_key(self.SCHEDULER_NAME):
                return settings.SCHEDULER_COMMAND_PATHS[self.SCHEDULER_NAME].get(scheduler_command, scheduler_command)
        return scheduler_command


    def _get_submission_wrapper_script(self):
        return self.QSUB_TEMPLATE.format(
            self.submission_script_name, self.submission_script_body,
            self.stdout_file, self.stderr_file, self._yabi_task_name()).replace("<QSUB_COMMAND>",self.get_scheduler_command_path("qsub"))

    def _get_polling_script(self):
        return self.QSTAT_TEMPLATE.format(self.task.remote_id).replace("<QSTAT_COMMAND>", self.get_scheduler_command_path("qstat"))

