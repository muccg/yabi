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
from yabi.backend.torqueparsers import TorqueParser
from yabi.backend.exceptions import JobNotFoundException


class SSHTorqueExecBackend(BaseExecBackend):
    SCHEDULER_NAME = "torque"
    STAT_TEMPLATE = "\n".join(["#!/bin/sh",
                               "<STAT_COMMAND> -f -1 {0}"])

    def __init__(self, *args, **kwargs):
        super(SSHTorqueExecBackend, self).__init__(*args, **kwargs)
        self.parser = TorqueParser()

    def _job_not_found_response(self, qstat_result):
        raise JobNotFoundException("Remote job %s for Yabi task %s not found by qstat" % (self.task.remote_id, self._yabi_task_name()))
