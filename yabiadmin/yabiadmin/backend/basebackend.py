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
from yabiadmin.yabiengine.urihelper import url_join
from yabiadmin.backend.exceptions import RetryException
from yabiadmin.backend.utils import execute
import traceback
import subprocess
import logging
import os
import shutil
logger = logging.getLogger(__name__)


class BaseBackend(object):

    task = None
    cred = None
    yabiusername = None
    last_stdout = None
    last_stderr = None

    def blocking_execute(self, args, bufsize=0, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=None, env=None):
        """execute a process and wait for it to end"""
        status = None
        try:
            logger.debug(args)
            logger.debug(cwd)
            process = execute(args, bufsize=bufsize, stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, env=env)
            stdout_data, stderr_data = process.communicate(stdin)
            status = process.returncode

            if stdout == subprocess.PIPE:
                self.last_stdout = stdout_data
            if stderr == subprocess.PIPE:
                self.last_stderr = stderr_data
        except Exception, exc:
            logger.error('execute failed {0}'.format(status))
            from yabiadmin.backend.exceptions import RetryException
            raise RetryException(exc, traceback.format_exc())

        return status

    def local_remnants_dir(self, scratch='/tmp'):
        """Return path to a directory on the local file system for any task remnants"""
        return os.path.join(scratch, self.task.working_dir)

    def working_dir_uri(self):
        """working dir"""
        return url_join(self.task.job.fs_backend, self.task.working_dir)

    def working_input_dir_uri(self):
        """working/input dir"""
        return url_join(self.working_dir_uri(), 'input')

    def working_output_dir_uri(self):
        """working/output dir"""
        return url_join(self.working_dir_uri(), 'output')

    def create_local_remnants_dir(self):
        local_remnants_dir = self.local_remnants_dir()
        if os.path.exists(local_remnants_dir):
            shutil.rmtree(local_remnants_dir)
        os.makedirs(local_remnants_dir)

