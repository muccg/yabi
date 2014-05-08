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
from yabiadmin.yabiengine.urihelper import uriparse
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.utils import sshclient
from contextlib import contextmanager
import uuid
import traceback
import paramiko
import logging
import stat
logger = logging.getLogger(__name__)


class SSHExec(object):

    def __init__(self, uri=None, credential=None, tmp_dir=None):
        self.uri = uri
        self.credential = credential
        self._tmp_dir = tmp_dir

    @property
    def tmp_dir(self):
        return self._tmp_dir or '/tmp'

    @tmp_dir.setter
    def tmp_dir(self, value):
        self._tmp_dir = value

    @contextmanager
    def sshclient(self):
        exec_scheme, exec_parts = uriparse(self.uri)
        ssh = sshclient(exec_parts.hostname, exec_parts.port, self.credential)
        try:
            yield ssh
        finally:
            try:
                ssh.close()
            except:
                pass

    def exec_script(self, script):
        logger.debug("SSHExex.exec_script...")
        logger.debug('script content = {0}'.format(script))
        exec_scheme, exec_parts = uriparse(self.uri)
        ssh = sshclient(exec_parts.hostname, exec_parts.port, self.credential)
        sftp = None
        try:
            sftp = ssh.open_sftp()

            script_name = self.upload_script(sftp, script)
            stdin, stdout, stderr = ssh.exec_command(script_name, bufsize=-1, timeout=None, get_pty=False)
            stdin.close()
            exit_code = stdout.channel.recv_exit_status()
            logger.debug("sshclient exec'd script OK")

            self.remove_script(sftp, script_name)

            return exit_code, stdout.readlines(), stderr.readlines()
        except paramiko.SSHException as sshe:
            raise RetryException(sshe, traceback.format_exc())
        finally:
            try:
                if sftp is not None:
                    sftp.close()
                if ssh is not None:
                    ssh.close()
            except:
                pass

    def upload_script(self, sftp, script_body):
        try:
            remote_path = self.generate_remote_script_name()
            create_remote_file(sftp, remote_path, script_body)
            make_user_executable(sftp, remote_path)
            return remote_path
        except:
            logger.exception("Error while trying to upload script")
            raise

    def remove_script(self, sftp, script_name):
        try:
            sftp.remove(script_name)
        except:
            # Don't fail, just log the error
            logger.exception("Error while trying to delete script '%s'", script_name)

    def generate_remote_script_name(self):
        name = os.path.join(self.tmp_dir, "yabi-" + str(uuid.uuid4()) + ".sh")
        return name


def create_remote_file(sftp, remote_path, body):
    remote_file = sftp.open(remote_path, mode='w')
    remote_file.write(body)


def make_user_executable(sftp, path):
    st = sftp.stat(path)
    sftp.chmod(path, st.st_mode | stat.S_IEXEC)


