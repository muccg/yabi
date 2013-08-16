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
from yabiadmin.backend.execbackend import ExecBackend
from yabiadmin.backend.exceptions import RetryException
import shlex
import shutil
import logging
logger = logging.getLogger(__name__)


class LocalExecBackend(ExecBackend):

    def submit_task(self):
        """
        For local exec submitting a task executes the task and blocks
        the current process. It is not intended for large scale real world usage.
        """
        self.create_local_remnants_dir()

        exec_scheme, exec_parts = uriparse(self.task.job.exec_backend)
        working_scheme, working_parts = uriparse(self.working_output_dir_uri())

        # TODO use this script
        script = self.get_submission_script(exec_parts.hostname, working_parts.path)
        logger.debug('script {0}'.format(script))

        if os.path.exists(working_parts.path):
            shutil.rmtree(working_parts.path)

        os.makedirs(working_parts.path)

        try:
            stdout = open(os.path.join(working_parts.path, 'STDOUT.txt'), 'w')
            stderr = open(os.path.join(working_parts.path, 'STDERR.txt'), 'w')
        except Exception, exc:
            raise RetryException(exc)

        logger.debug('Running in {0}'.format(working_parts.path))
        args = shlex.split(self.task.command.encode('utf-8'))
        status = self.blocking_execute(args=args, stderr=stderr, stdout=stdout, cwd=working_parts.path)

        if status != 0:
            logger.error('Non zero exit status [{0}]'.format(status))
            raise RetryException('Local Exec of command "{0}" retuned non-zero code {1}'.format(" ".join(args), status))

        try:
            stdout.close()
            stderr.close()
        except Exception, exc:
            logger.error(exc)

        return status

    def poll_task_status(self):
        pass
