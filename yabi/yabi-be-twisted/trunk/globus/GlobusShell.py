import os
from twisted.internet import protocol
from twisted.internet import reactor
    
class GlobusShellProcessProtocol(protocol.ProcessProtocol):
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

class GlobusShell(object):
    gsissh = '/usr/local/globus/bin/gsissh'
    
    def __init__(self):
        pass

    def _make_path(self):
        return "/usr/local/globus/bin"    

    def _make_env(self, certfile):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        
        return subenv

    def execute(self, certfile, host, *command):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""

        # TODO FIXME
        #
        # Calling Popen is currently broken in Twisted. This is due to the way signal handling is done in twisted.
        # Reference:  http://twistedmatrix.com/trac/ticket/733
        # A quick google can find plenty of other references and various workarounds.
        #
        # Suggestion: Use spawnProcess within the twisted api. Specifically there is some utils code within the 
        # twisted api which makes this really easy.
        # Reference: http://twistedmatrix.com/documents/8.2.0/api/twisted.internet.utils.html
       
        subenv = self._make_env(certfile)
        pp = GlobusShellProcessProtocol()
        print "ENV",subenv
        print "COMMAND:",[ self.gsissh, host ] +list(command)
        reactor.spawnProcess(   pp,
                                self.gsissh,
                                [ self.gsissh, host ] + list(command),
                                env=subenv,
                                path=self._make_path()
                            )
        return pp

    def ls(self, certfile, host, directory, args="-alFR"):
        return self.execute(certfile,host,"ls",args,directory)

    def mkdir(self, certfile, host, directory, args="-p"):
        return self.execute(certfile,host,"mkdir",args,directory)
    
    def rm(self, certfile, host, directory, args=None):
        return self.execute(certfile,host,"rm",args,directory) if args else self.execute(certfile,host,"rm",directory)
    
