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


class SSHExec(object):

    def __init__(self, uri=None, credential=None):
        self.uri = uri
        self.credential = credential

    def exec_script(self, script):
        logger.debug("SSHExex.exec_script...")
        logger.debug('script content = {0}'.format(script))
        exec_scheme, exec_parts = uriparse(self.uri)
        ssh = sshclient(exec_parts.hostname, exec_parts.port, self.credential)
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

    def generate_remote_script_name(self):
        REMOTE_TMP_DIR = '/tmp'
        name = os.path.join(REMOTE_TMP_DIR, "yabi-" + str(uuid.uuid4()) + ".sh")
        return name
