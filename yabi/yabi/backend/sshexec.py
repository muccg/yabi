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
import os
from yabi.yabiengine.urihelper import uriparse
from yabi.backend.exceptions import RetryException
from yabi.backend.utils import sshclient
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
