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

from __future__ import unicode_literals
import logging
from yabi.backend.schedulerexecbackend import SchedulerExecBackend
logger = logging.getLogger(__name__)


class BaseExecBackend(SchedulerExecBackend):
    """
    A _abstract_ backend which allows job submission via qsub
    """
    SUB_COMMAND_NAME = "qsub"
    STAT_COMMAND_NAME = "qstat"
    CANCEL_COMMAND_NAME = "qdel"

    SUB_TEMPLATE = "\n".join([
        "#!/bin/sh",
        'script_temp_file_name="{0}"',
        "cat<<\"EOS\">$script_temp_file_name",
        "{1}",
        "EOS",
        "cd '{2}'",
        "%s",  # SUB_COMMAND_LINE will be inserted here
        "rm $script_temp_file_name"])
    SUB_COMMAND_LINE = "<SUB_COMMAND> -N {3} $script_temp_file_name"
    STAT_TEMPLATE = "\n".join(["#!/bin/sh", "<STAT_COMMAND> -f -1 {0}"])
    CANCEL_TEMPLATE = "\n".join(['#!/bin/sh', '<CANCEL_COMMAND> "{0}"'])

    def get_scheduler_command_path(self, scheduler_command):
        from django.conf import settings
        if hasattr(settings, "SCHEDULER_COMMAND_PATHS"):
            if self.SCHEDULER_NAME in settings.SCHEDULER_COMMAND_PATHS:
                return settings.SCHEDULER_COMMAND_PATHS[self.SCHEDULER_NAME].get(scheduler_command, scheduler_command)
        return scheduler_command

    def _get_sub_template(self):
        return self.SUB_TEMPLATE % self.SUB_COMMAND_LINE

    def _get_submission_wrapper_script(self):
        return self._get_sub_template().format(
            self.submission_script_name, self.submission_script_body,
            self.working_dir,
            self._yabi_task_name()).replace("<SUB_COMMAND>", self.get_scheduler_command_path(self.SUB_COMMAND_NAME))

    def _get_polling_script(self):
        return self.STAT_TEMPLATE.format(self.task.remote_id).replace("<STAT_COMMAND>", self.get_scheduler_command_path(self.STAT_COMMAND_NAME))

    def _get_abort_script(self):
        return self.CANCEL_TEMPLATE.format(self.task.remote_id).replace("<CANCEL_COMMAND>", self.get_scheduler_command_path(self.CANCEL_COMMAND_NAME))
