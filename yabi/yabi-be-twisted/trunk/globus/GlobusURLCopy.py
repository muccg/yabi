"""Class to encapsulate the functionality in "globus-url-copy"
"""
import os
import tempfile
import sys
from FifoPool import Fifos

from twisted.internet import protocol
from twisted.internet import reactor

class GlobusURLCopyProcessProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        self.started = False
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        self.started = True
        
    def outReceived(self, data):
        self.out += data
        
    def errReceived(self, data):
        self.err += data
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None
    
    def isStarted(self):
        return self.started

class GlobusFTPError(Exception):
    pass

def _globus_process_error(string):
    """parse the response from globus_url_copy and return an error code and a message"""
    lines = string.split("\n")
    numlines = [line.strip() for line in lines if  len(line) and '0' <= line[0] <= '9']               # lines that begin with a number
    
    # lets take numbered line 0 as our information line
    print string
    info = numlines[0]
    
    parts = info.split()
    
    if parts[0]=="1)":
        #certificate problems
        raise GlobusFTPError, (0,"Couldn't use proxyfile to auth connection")
    
    return int(parts[0])," ".join(parts[1:])

class GlobusURLCopy(object):
    """copy to/from/between globus"""
    globus_url_copy = '/usr/local/globus/bin/globus-url-copy'
    
    def __init__(self):
        pass
    
    def _make_env(self, certfile):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        
        return subenv
    
    def WriteToRemote(self, certfile, remoteurl, fifo=None):
        """starts a copy to remote process and returns you the following (proc, file, url) where:
        proc:   the Popen subprocess python object. Its a child process object.
        file:   the filename of the fifo object to open and write data into
        """
        subenv = self._make_env(certfile)
        
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
            print "generated",fifo
            
        url = Fifos.MakeURLForFifo(fifo)
        
        pp = GlobusURLCopyProcessProtocol()
        
        # the copy to remote command
        print "GlobusURLCopy::WriteToRemote",certfile,remoteurl
        print subenv
        print [ self.globus_url_copy,
                                        "-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                        "-cd",                                  # create destination directories if they dont exist
                                        url,                                     # source
                                        remoteurl                                # destination
                                    ]
        
        reactor.spawnProcess(   pp,
                                self.globus_url_copy,
                                [ self.globus_url_copy,
                                        "-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                        "-cd",                                  # create destination directories if they dont exist
                                        url,                                     # source
                                        remoteurl                                # destination
                                    ],
                                env=subenv,
                                path="/bin"
                            )
        
        return pp, fifo
    
    def ReadFromRemote(self, certfile, remoteurl, fifo=None):
        """Read from a remote url into a local fifo"""
        subenv = self._make_env(certfile)
        
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        url = Fifos.MakeURLForFifo(fifo)
        #print "READ:",fifo,url,remoteurl
        
        pp = GlobusURLCopyProcessProtocol()
        
        # the copy to remote command
        reactor.spawnProcess(   pp,
                                self.globus_url_copy,
                                [  self.globus_url_copy,
                                    "-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                    remoteurl,                               # source
                                    url                                      # destination
                                ],
                                env=subenv,
                                path="/bin"
                            )
                                    
        #Fifos.WeakLink( fifo, proc )
        
        return pp, fifo
    
    
        