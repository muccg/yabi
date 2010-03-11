# -*- coding: utf-8 -*-
import os
from twisted.internet import protocol
from twisted.internet import reactor

from BaseShell import BaseShell, BaseShellProcessProtocol

DEBUG = True

class SSHShellProcessProtocol(BaseShellProcessProtocol):
    pass

class SSHShell(BaseShell):
    ssh = '/usr/bin/ssh'
    
    def _make_path(self):
        return "/usr/bin"    

    def execute(self, certfile, host, command):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""
        if DEBUG:
            print "SSHShell running:",[ 
                self.ssh,
                '-i',certfile,
                host 
            ] + list(command)
        return BaseShell.execute(self,SSHShellProcessProtocol,
            [ 
                self.ssh,
                '-i',certfile,
                host 
            ] + list(command)
        )
    def ls(self, certfile, host, directory, args="-alFR"):
        return self.execute(certfile,host,command=["ls",args,directory])
      
    def mkdir(self, certfile, host, directory, args="-p"):
        return self.execute(certfile,host,command=["mkdir",args,directory])
      
    def rm(self, certfile, host, directory, args=None):
        return self.execute(certfile,host,command=["rm",args,directory]) if args else self.execute(certfile,host,command=["rm",directory]) 
