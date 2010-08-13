# -*- coding: utf-8 -*-
import os
from twisted.internet import protocol
from twisted.internet import reactor
    
DEBUG = False
    
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
        if DEBUG:
            print "OUT:",data
        
    def errReceived(self, data):
        self.err += data
        if DEBUG:
            print "ERR:",data
    
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        if DEBUG:
            print "Out lost"
        
    def inConenctionLost(self):
        if DEBUG:
            print "In lost"
        
    def errConnectionLost(self):
        if DEBUG:
            print "Err lost"
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        if DEBUG:
            print "proc ended",self.exitcode
        
    def isDone(self):
        return self.exitcode != None
        
    def isFailed(self):
        return self.isDone() and self.exitcode != 0

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

    def execute(self, protocol, certfile, command):
        """execute a command using a process protocol"""

        subenv = self._make_env(certfile)
        pp = protocol()
        if DEBUG:
            print "env",subenv
            print "exec:",command
            
        reactor.spawnProcess(   pp,
                                command[0],
                                command,
                                env=subenv,
                                path=self._make_path()
                            )
        return pp
