"""Base class for FSConnector"""

class NotImplemented(Exception):
    """Exception to mark methods that haven't been overridden... yet..."""
    pass

class ExecConnector(object):
    """Base class for a filesystem connector"""
    
    def run(self, command, working, address, callback, *args, **kwargs):
        """Run a job on a backend. extra params can be passed in that are specific to a backend. They should all have defaults if ommitted
        
        command is the command to run
        working is the working directory
        address is the host on which to run the command
        
        callback is a callable that is called with the status changes for the running job
        
        """
        raise NotImplemented("The run method for this backend is not implemented")
    
        