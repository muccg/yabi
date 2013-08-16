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
from yabiadmin.backend.execbackend import ExecBackend
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.fsbackend import FSBackend
from yabiadmin.backend.utils import sshclient
import uuid
import socket
import traceback
import paramiko
import tempfile
import logging
logger = logging.getLogger(__name__)


class SSHBackend(ExecBackend):

    def submit_task(self):
        """ 
        For ssh tasks we run the task in the foreground. For this reason
        it is not intended for large scale use. A quirk of using ssh.exec_command
        is the need to copy stderr and stdout to the working output dir of the 
        remote host.
        """
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())

        # TODO use this script instead of self.task.command
        script = self.get_submission_script(exec_parts.hostname, working_parts.path)
        logger.debug('script {0}'.format(script))

        ssh = sshclient(exec_parts.hostname, exec_parts.port, self.cred.credential)
        try:
            stdin, stdout, stderr = ssh.exec_command(self.task.command, bufsize=-1, timeout=None, get_pty=False)
            stdin.close()
        except paramiko.SSHException, sshe:
            raise RetryException(sshe, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

        # create local remnant files to store stdout and stderr
        remnant_stdout = open(os.path.join(self.local_remnants_dir(), 'STDOUT.txt'), 'w')
        remnant_stderr = open(os.path.join(self.local_remnants_dir(), 'STDERR.txt'), 'w')
        logger.debug('Created remnant {0}'.format(remnant_stdout.name))
        logger.debug('Created remnant {0}'.format(remnant_stderr.name))
        for line in stdout:
            remnant_stdout.write(line)
        for line in stderr:
            remnant_stderr.write(line)
        remnant_stdout.close()
        remnant_stderr.close()

        return 0

    def _exec_script(self, script):
        logger.debug("SSHBackend.exec_script...")
        logger.debug('script content = {0}'.format(script))
        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        ssh = sshclient(exec_parts.hostname, exec_parts.port, self.cred.credential)
        try:
            stdin, stdout, stderr = ssh.exec_command(script, bufsize=-1, timeout=None, get_pty=False)
            stdin.close()

            logger.debug("sshclient exec'd script OK")
            return stdout.readlines(), stderr.readlines()
        except paramiko.SSHException, sshe:
            raise RetryException(sshe, traceback.format_exc())
        finally:
            try:
                if ssh is not None:
                    ssh.close()
            except:
                pass

    def poll_task_status(self):
        pass

    def _generate_remote_script_name(self):
        REMOTE_TMP_DIR = '/tmp'
        return os.path.join(REMOTE_TMP_DIR, "yabi-" + str(uuid.uuid4()) + ".sh")




