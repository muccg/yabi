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

import os
from yabi.backend.schedulerexecbackend import SchedulerExecBackend
from yabi.backend.sshparsers import SSHParser
import logging
import time
logger = logging.getLogger(__name__)


WAIT_TO_TERMINATE_SECS = 3


class SSHBackend(SchedulerExecBackend):
    SCHEDULER_NAME = "SSH"

    RUN_COMMAND_TEMPLATE = """
#!/bin/sh
script_temp_file_name="{0}"
cat<<"EOS">$script_temp_file_name
{1}
EOS
chmod u+x $script_temp_file_name
nohup $script_temp_file_name > '{2}' 2> '{3}' < /dev/null &
echo "$!"
"""

    PS_COMMAND_TEMPLATE = """
#!/bin/sh
ps -o pid= -p {0}
"""

    KILL_COMMAND_TEMPLATE = """
#!/bin/sh
kill {1} -- -$( ps opgid= {0} | tr -d ' ')
"""

    backend_desc = "SSH remote execution"

    def __init__(self, *args, **kwargs):
        super(SSHBackend, self).__init__(*args, **kwargs)
        self.parser = SSHParser()

    # TODO this looks very similar to LocalExecBackend#abort_task()
    # Maybe, refactor later.
    def abort_task(self):
        pid = self.task.remote_id
        if not self.is_process_running():
            logger.info("Couldn't kill process of task %s. Process with id %s isn't running", self.task.pk, pid)
            return

        self.kill_process(pid)
        time.sleep(WAIT_TO_TERMINATE_SECS)
        if not self.is_process_running():
            return

        logger.info("Process %s (task %s) not terminated on SIGTERM. Sending SIGKILL", pid, self.task.pk)
        self.kill_process(pid, with_SIGKILL=True)

    def _get_submission_wrapper_script(self):
        stdout_file = os.path.join(self.working_dir, "STDOUT.txt")
        stderr_file = os.path.join(self.working_dir, "STDERR.txt")

        return self.RUN_COMMAND_TEMPLATE.format(
            self.submission_script_name, self.submission_script_body,
            stdout_file, stderr_file)

    def _get_polling_script(self):
        return self.PS_COMMAND_TEMPLATE.format(self.task.remote_id)

    def is_process_running(self):
        result = self._poll_job_status()
        return result.status == result.JOB_RUNNING

    def kill_process(self, pid, with_SIGKILL=False):
        kill_script = self._get_kill_script(with_SIGKILL)
        exit_code, stdout, stderr = self.executer.exec_script(kill_script)
        if exit_code > 0 or stderr:
            logger.error("Couldn't kill process %s. Exit code: %s. STDERR:\n%s", pid, exit_code, stderr)

    def _get_kill_script(self, with_SIGKILL):
        signal = "-KILL" if with_SIGKILL else ""
        return self.KILL_COMMAND_TEMPLATE.format(self.task.remote_id, signal)
