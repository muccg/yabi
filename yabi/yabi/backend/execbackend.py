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

from yabi.backend.backend import exec_credential
from yabi.backend.basebackend import BaseBackend
import logging
from yabi.backend.utils import submission_script
logger = logging.getLogger(__name__)


class ExecBackend(BaseBackend):

    @classmethod
    def factory(cls, task):
        assert(task)
        assert(task.execscheme)

        backend = cls.create_backend_for_scheme(task.execscheme)

        if not backend:
            raise Exception('No valid scheme is defined for task {0}'.format(task.id))

        backend.yabiusername = task.job.workflow.user.name
        backend.task = task
        backend.cred = exec_credential(backend.yabiusername, task.job.exec_backend)
        backend.backend = backend.cred.backend if backend.cred is not None else None
        return backend

    def get_submission_script(self, host, working):
        """Get the submission script for this backend."""
        if self.task.job.tool.submission.strip() != '':
            template = self.task.job.tool.submission
        elif self.cred.submission.strip() != '':
            template = self.cred.submission
        else:
            template = self.cred.backend.submission

        return submission_script(
            template=template,
            working=working,
            command=self.task.command,
            modules=self.task.job.module,
            cpus=self.task.job.cpus,
            memory=self.task.job.max_memory,
            walltime=self.task.job.walltime,
            yabiusername=self.yabiusername,
            username=self.cred.credential.username,
            host=host,
            queue=self.task.job.queue,
            tasknum=self.task.task_num,
            tasktotal=self.task.job.task_total,
            envvars=self.task.envvars)

    def submit_task(self):
        raise NotImplementedError("")

    def poll_task_status(self):
        raise NotImplementedError("")

    def abort_task(self):
        raise NotImplementedError("")
