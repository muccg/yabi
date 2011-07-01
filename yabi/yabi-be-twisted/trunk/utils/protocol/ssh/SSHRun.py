# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-
"""Implement scp connections"""

import os
import sys
import tempfile

from FifoPool import Fifos

from BaseShell import BaseShell, BaseShellProcessProtocol

class SSHExecProcessProtocolParamiko(BaseShellProcessProtocol):
    def __init__(self, stdin_data=None):
        BaseShellProcessProtocol.__init__(self)
        self.started = False
        self.stdin_data = stdin_data
        
    def connectionMade(self):
        if self.stdin_data:
            self.transport.write(self.stdin_data)
        
        self.transport.closeStdin()
        self.started = True
                
    def isStarted(self):
        return self.started
        
class SSHError(Exception):
    pass
        
class SSHRun(BaseShell):
    ssh_exec = os.path.join( os.path.dirname(os.path.realpath(__file__)), "paramiko-ssh.py" )
    python = sys.executable                     # use the same python that yabi backend is running under
    
    def run(self, certfile, remote_command="hostname", username="yabi", host="faramir.localdomain", working="/tmp", port="22", stdout="STDOUT.txt", stderr="STDERR.txt",password="",modules=[],streamin=None):
        """Spawn a process to run a remote ssh job. return the process handler"""
        subenv = self._make_env()
        
        if modules:
            remote_command = "&&".join(["module load %s"%module for module in modules]+[remote_command])
        
        print "running remote command:",remote_command
        
        command = [self.python, self.ssh_exec ]
        command += ["-i",certfile] if certfile else []
        command += ["-p",password] if password else []
        command += ["-u",username] if username else []
        command += ["-H",host] if host else []
        command.extend( [ "-x", remote_command ] )
        
            
        print "COMMAND:",command
            
        return BaseShell.execute(self,SSHExecProcessProtocolParamiko(streamin),command)
