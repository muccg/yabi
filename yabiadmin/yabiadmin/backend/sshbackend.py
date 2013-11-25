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
from yabiadmin.yabiengine.urihelper import url_join, uriparse
from yabiadmin.backend.backend import fs_credential
from yabiadmin.backend.schedulerexecbackend import SchedulerExecBackend
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.fsbackend import FSBackend
from yabiadmin.backend.utils import sshclient
from yabiadmin.backend.sshparsers import SSHParser
import uuid
import socket
import traceback
import paramiko
import tempfile
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
        return self.PS_COMMAND_TEMPLATE.format( self.task.remote_id)
        
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


