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

