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
