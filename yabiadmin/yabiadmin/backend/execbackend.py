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
from yabiadmin.backend.backend import exec_credential
from yabiadmin.backend.basebackend import BaseBackend
import logging
from yabiadmin.backend.utils import submission_script
logger = logging.getLogger(__name__)


class ExecBackend(BaseBackend):

    @staticmethod
    def factory(task):
        assert(task)
        assert(task.execscheme)

        if task.execscheme == 'ssh':
            from yabiadmin.backend.sshbackend import SSHBackend
            backend = SSHBackend()

        elif task.execscheme == 'localex':
            from yabiadmin.backend.localexecbackend import LocalExecBackend
            backend = LocalExecBackend()

        elif task.execscheme == 'selectfile' or task.execscheme == 'null':
            from yabiadmin.backend.selectfileexecbackend import SelectFileExecBackend
            backend = SelectFileExecBackend()

        elif task.execscheme == 'ssh+sge':
            from yabiadmin.backend.sshsgeexecbackend import SSHSGEExecBackend
            backend = SSHSGEExecBackend()

        elif task.execscheme == 'ssh+torque':
            from yabiadmin.backend.sshtorquebackend import SSHTorqueExecBackend
            backend = SSHTorqueExecBackend()

        elif task.execsheme == "ssh+pbspro":
            from yabiadmin.backend.sshpbsprobackend import SSHPBSProExecBackend
            backend = SSHPBSProExecBackend()

        else:
            raise Exception('No valid scheme is defined for task {0}'.format(task.id))

        backend.yabiusername = task.job.workflow.user.name
        backend.task = task
        backend.cred = exec_credential(backend.yabiusername, task.job.exec_backend)
        return backend

    def get_submission_script(self, host, working):
        """Get the submission script for this backend."""
        if self.cred.submission.strip() != '':
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
            stdout='STDOUT.txt',
            stderr='STDERR.txt',
            tasknum=self.task.task_num,
            tasktotal=self.task.job.task_total)

    def submit_task(self):
        raise NotImplementedError("")

    def poll_task_status(self):
        raise NotImplementedError("")
