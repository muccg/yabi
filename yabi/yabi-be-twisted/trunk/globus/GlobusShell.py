import os
from twisted.internet import protocol
from twisted.internet import reactor

from BaseShell import BaseShell, BaseShellProcessProtocol

class GlobusShellProcessProtocol(BaseShellProcessProtocol):
    pass

class GlobusShell(BaseShell):
    gsissh = '/usr/local/globus/bin/gsissh'
    
    def _make_path(self):
        return "/usr/local/globus/bin"    

    def execute(self, certfile, host, command):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""
        BaseShell.execute(self,GlobusShellProcessProtocol,certfile,
            [ 
                self.gsissh, 
                host 
            ] + list(command)
        )
    def ls(self, certfile, host, directory, args="-alFR"):
        return self.execute(certfile,host,command=["ls",args,directory])
      
    def mkdir(self, certfile, host, directory, args="-p"):
        return self.execute(certfile,host,command=["mkdir",args,directory])
      
    def rm(self, certfile, host, directory, args=None):
        return self.execute(certfile,host,command=["rm",args,directory]) if args else self.execute(certfile,host,command=["rm",directory]) 
