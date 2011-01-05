# -*- coding: utf-8 -*-
"""Implement scp connections"""

import os
import tempfile

from FifoPool import Fifos

from BaseShell import BaseShell, BaseShellProcessProtocol

class SSHExecProcessProtocol(BaseShellProcessProtocol):
    def __init__(self, password):
        BaseShellProcessProtocol.__init__(self)
        self.started = False
        self.password = password
        
    def connectionMade(self):
        self.transport.write(str(self.password))
        self.transport.write("\n")
        self.transport.closeStdin()
        self.started = True
                
    def isStarted(self):
        return self.started
        
class SSHError(Exception):
    pass

class SSHRun(BaseShell):
    ssh_exec = os.path.join( os.path.dirname(os.path.realpath(__file__)), "ssh-exec.py" )
    python = "/usr/bin/python"
    
    def run(self, certfile, remote_command="hostname", username="yabi", host="faramir.localdomain", working="/tmp", port="22", stdout="STDOUT.txt", stderr="STDERR.txt",password="",modules=[]):
        """Spawn a process to run a remote ssh job. return the process handler"""
        subenv = self._make_env()
        
        if modules:
            remote_command = "&&".join(["module load %s"%module for module in modules]+[remote_command])
        
        command = [ self.python, self.ssh_exec,
            "-i", certfile,
            "-P", port,
            "-o", stdout,
            "-e", stderr,
            "-w", working,
            "-x", remote_command,
            "%s@%s"%(username,host)
            ]
            
        return BaseShell.execute(self,SSHExecProcessProtocol(password),command)