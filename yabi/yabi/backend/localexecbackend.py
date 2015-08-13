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
import io
import os
import stat
import shlex
import shutil
import logging
import uuid
import time
from yabi.yabiengine.urihelper import uriparse
from yabi.backend.execbackend import ExecBackend
from yabi.backend.exceptions import RetryException
from yabi.backend.utils import blocking_execute

logger = logging.getLogger(__name__)

WAIT_TO_TERMINATE_SECS = 3

EXEC_SCRIPT_PREFIX = 'yabi_lexec_'
DEFAULT_TEMP_DIRECTORY = '/tmp'


class LocalExecBackend(ExecBackend):
    backend_desc = "Local execution"
    backend_auth = {}

    def __init__(self, *args, **kwargs):
        ExecBackend.__init__(self, *args, **kwargs)
        self.backend = None

    @property
    def temp_directory(self):
        temp_dir = DEFAULT_TEMP_DIRECTORY
        if self.backend and self.backend.temporary_directory:
            temp_dir = self.backend.temporary_directory
        return temp_dir

    def submit_task(self):
        """
        For local exec submitting a task executes the task and blocks
        the current process. It is not intended for large scale real world usage.
        """
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())

        script = self.get_submission_script(exec_parts.hostname, working_parts.path)
        logger.debug('script {0}'.format(script))
        script_name = self.create_script(script)

        if os.path.exists(working_parts.path):
            shutil.rmtree(working_parts.path)

        os.makedirs(working_parts.path)

        try:
            stdout = open(os.path.join(working_parts.path, 'STDOUT.txt'), 'w')
            stderr = open(os.path.join(working_parts.path, 'STDERR.txt'), 'w')

            logger.debug('Running in {0}'.format(working_parts.path))
            args = shlex.split(self.task.command.encode('utf-8'))

            def set_remote_id(pid):
                self.task.remote_id = pid
                self.task.save()

            args = [script_name]
            status = blocking_execute(args=args, stderr=stderr, stdout=stdout, cwd=working_parts.path, report_pid_callback=set_remote_id)

            if status != 0:
                if self.is_aborting():
                    return None
                logger.error('Non zero exit status [{0}]'.format(status))
                raise RetryException('Local Exec of command "{0}" retuned non-zero code {1}'.format(" ".join(args), status))

        except Exception as exc:
            raise RetryException(exc)
        finally:
            try:
                stdout.close()
                stderr.close()
            except Exception as exc:
                logger.error(exc)

            try:
                os.unlink(script_name)
            except:
                logger.exception("Couldn't delete script file %s", script_name)

        return status

    def create_script(self, script_contents):
        script_name = os.path.join(self.temp_directory,
                                   '%s%s.sh' % (EXEC_SCRIPT_PREFIX, uuid.uuid4()))
        with io.open(script_name, 'w', encoding="utf-8") as f:
            f.write(script_contents)
        st = os.stat(script_name)
        os.chmod(script_name, st.st_mode | stat.S_IEXEC)
        return script_name

    def poll_task_status(self):
        pass

    def abort_task(self):
        pid = self.task.remote_id
        if not is_process_running(pid):
            logger.info("Couldn't kill process of task %s. Process with id %s isn't running", self.task.pk, pid)
            return

        kill_process(pid)
        time.sleep(WAIT_TO_TERMINATE_SECS)
        if not is_process_running(pid):
            return

        logger.info("Process %s (task %s) not terminated on SIGTERM. Sending SIGKILL", pid, self.task.pk)
        kill_process(pid, with_SIGKILL=True)

    def is_aborting(self):
        from ..yabiengine.enginemodels import EngineTask
        task = EngineTask.objects.get(pk=self.task.pk)
        return task.is_workflow_aborting


def is_process_running(pid):
    from yabi.backend.utils import execute

    args = ["ps", "-o", "pid=", "-p", pid]
    process = execute(args)
    stdout, stderr = process.communicate(None)

    return (pid in stdout)


def kill_process(pid, with_SIGKILL=False):
    logger.info("Killing process (SIGKILL=%s) %s", with_SIGKILL, pid)
    from yabi.backend.utils import execute

    args = ["kill"]
    if with_SIGKILL:
        args.append("-KILL")
    args.append(pid)
    process = execute(args)
    stdout, stderr = process.communicate(None)
    status = process.returncode

    if status != 0:
        logger.error("Couldn't kill process %s. STDERR:\n%s", pid, stderr)
