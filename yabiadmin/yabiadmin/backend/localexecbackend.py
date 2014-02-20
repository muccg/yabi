### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics
# (http://ccg.murdoch.edu.au/).
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS,"
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS.
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
### END COPYRIGHT ###
import os
import stat
import shlex
import shutil
import logging
import uuid
import time
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.backend.execbackend import ExecBackend
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.yabiengine.enginemodels import EngineTask
from yabiadmin.backend.utils import blocking_execute

logger = logging.getLogger(__name__)

WAIT_TO_TERMINATE_SECS = 3


class LocalExecBackend(ExecBackend):

    def submit_task(self):
        """
        For local exec submitting a task executes the task and blocks
        the current process. It is not intended for large scale real world usage.
        """
        self.create_local_remnants_dir()

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
        script_name = '/tmp/yabi_lexec_%s.sh' % uuid.uuid4()
        with open(script_name, 'w') as f:
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
        task = EngineTask.objects.get(pk=self.task.pk)
        return task.is_workflow_aborting


def is_process_running(pid):
    from yabiadmin.backend.utils import execute

    args = ["ps", "-o", "pid=", "-p", pid]
    process = execute(args)
    stdout, stderr = process.communicate(None)

    return (pid in stdout)


def kill_process(pid, with_SIGKILL=False):
    logger.info("Killing process (SIGKILL=%s) %s", with_SIGKILL, pid)
    from yabiadmin.backend.utils import execute

    args = ["kill"]
    if with_SIGKILL:
        args.append("-KILL")
    args.append(pid)
    process = execute(args)
    stdout, stderr = process.communicate(None)
    status = process.returncode

    if status != 0:
        logger.error("Couldn't kill process %s. STDERR:\n%s", pid, stderr)
