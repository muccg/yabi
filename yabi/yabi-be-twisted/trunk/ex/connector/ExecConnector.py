# -*- coding: utf-8 -*-
"""Base class for FSConnector"""

class NotImplemented(Exception):
    """Exception to mark methods that haven't been overridden... yet..."""
    pass

class ExecutionError(Exception):
    pass

class ExecConnector(object):
    """Base class for a filesystem connector"""
    
    def __init__(self):
        self.childenv = {}
    
    def run(self, yabiusername, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single", module=None, **creds):
        """Run a job on a backend. extra params can be passed in that are specific to a backend. They should all have defaults if ommitted
        
        command is the command to run
        working is the working directory
        address is the host on which to run the command
        
        callback is a callable that is called with the status changes for the running job
        
        """
        raise NotImplemented("The run method for this backend is not implemented")
    
    def SetEnvironment(self, env):
        """Pass in the environment setup you want any child processes to inherit"""
        self.childenv = env.copy()
        