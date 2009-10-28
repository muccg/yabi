import os
from twisted.internet import protocol
from twisted.internet import reactor
    
class BaseShellProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, stdin=None):
        self.stdin=stdin
        self.err = ""
        self.out = ""
        self.exitcode = None
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        if self.stdin:
            self.transport.write(self.stdin)
        self.transport.closeStdin()
        
    def outReceived(self, data):
        self.out += data
        print "OUT:",data
        
    def errReceived(self, data):
        self.err += data
        print "ERR:",data
    
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        print "Out lost"
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        print "proc ended",self.exitcode
        
    def isDone(self):
        return self.exitcode != None

class BaseShell(object):
    def __init__(self):
        pass

    def _make_path(self):
        return "/usr/local/globus/bin"    

    def _make_env(self, certfile, environ=None):
        """Return a custom environment for the specified cert file"""
        subenv = environ.copy() if environ!=None else os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        return subenv    
        return subenv

    def execute(self, protocol, certfile, command):
        """execute a command using a process protocol"""

        subenv = self._make_env(certfile)
        pp = protocol()
        reactor.spawnProcess(   pp,
                                command[0],
                                command,
                                env=subenv,
                                path=self._make_path()
                            )
        return pp
