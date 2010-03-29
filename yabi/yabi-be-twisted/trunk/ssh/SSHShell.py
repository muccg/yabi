# -*- coding: utf-8 -*-
import os
from twisted.internet import protocol
from twisted.internet import reactor

from BaseShell import BaseShell, BaseShellProcessProtocol
from SSHRun import SSHExecProcessProtocol 


DEBUG = True

class SSHShell(BaseShell):
    ssh_exec = os.path.join( os.path.dirname(os.path.realpath(__file__)), "ssh-exec.py" )
    python = "/usr/bin/python"
    
    def _make_path(self):
        return "/usr/bin"    

    def execute(self, certfile, host, command, username, password):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""
        print "!"
        subenv = self._make_env()
        print "2"
        
        command = [ self.python, self.ssh_exec,
            "-i", certfile,
            "-P", port,
            "-w", working,
            "-x", remote_command,
            "%s@%s"%(username,host)
            ]
        
        if DEBUG:
            print "SSHShell Running:",command
            
        return BaseShell.execute(self,SSHExecProcessProtocol(password),command)
      
    def ls(self, certfile, host, directory,username, password, args="-alFR"):
        return self.execute(certfile,host,command=["ls",args,directory],username=username, password=password)
      
    def mkdir(self, certfile, host, directory,username, password, args="-p"):
        return self.execute(certfile,host,command=["mkdir",args,directory],username=username, password=password)
      
    def rm(self, certfile, host, directory,username, password, args=None):
        return self.execute(certfile,host,command=["rm",args,directory],username=username, password=password) if args else self.execute(certfile,host,command=["rm",directory],username=username, password=password) 
