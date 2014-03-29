import logging
from yabiadmin.backend.schedulerexecbackend import SchedulerExecBackend
logger = logging.getLogger(__name__)


class QBaseExecBackend(SchedulerExecBackend):
    """
    A _abstract_ backend which allows job submission via qsub
    """
    QSUB_TEMPLATE = "\n".join(["#!/bin/sh",
                    'script_temp_file_name="{0}"',
                    "cat<<\"EOS\">$script_temp_file_name",
                    "{1}",
                    "EOS",
                    "cd '{2}'"])
    QSUB_COMMAND_LINE = "<QSUB_COMMAND> -N {3} $script_temp_file_name"
    QSTAT_TEMPLATE = "\n".join(["#!/bin/sh", "<QSTAT_COMMAND> -f -1 {0}"])
    QDEL_TEMPLATE = "\n".join(['#!/bin/sh', '<QDEL_COMMAND> "{0}"'])

    def get_scheduler_command_path(self, scheduler_command):
        from django.conf import settings
        if hasattr(settings, "SCHEDULER_COMMAND_PATHS"):
            if self.SCHEDULER_NAME in settings.SCHEDULER_COMMAND_PATHS:
                return settings.SCHEDULER_COMMAND_PATHS[self.SCHEDULER_NAME].get(scheduler_command, scheduler_command)
        return scheduler_command

    def _get_qsub_template(self):
        return "%s\n%s" % (self.QSUB_TEMPLATE, self.QSUB_COMMAND_LINE)

    def _get_submission_wrapper_script(self):
        return self._get_qsub_template().format(
            self.submission_script_name, self.submission_script_body,
            self.working_dir,
            self._yabi_task_name()).replace("<QSUB_COMMAND>", self.get_scheduler_command_path("qsub"))

    def _get_polling_script(self):
        return self.QSTAT_TEMPLATE.format(self.task.remote_id).replace("<QSTAT_COMMAND>", self.get_scheduler_command_path("qstat"))

    def _get_abort_script(self):
        return self.QDEL_TEMPLATE.format(self.task.remote_id).replace("<QDEL_COMMAND>", self.get_scheduler_command_path("qdel"))
