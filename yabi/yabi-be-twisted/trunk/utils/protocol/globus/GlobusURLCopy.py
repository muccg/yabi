# -*- coding: utf-8 -*-
"""Class to encapsulate the functionality in "globus-url-copy"
"""
import os
import tempfile
import sys
from FifoPool import Fifos

from twisted.internet import protocol
from twisted.internet import reactor

from BaseShell import BaseShell, BaseShellProcessProtocol

class GlobusURLCopyProcessProtocol(BaseShellProcessProtocol):
    def __init__(self):
        BaseShellProcessProtocol.__init__(self)
        self.started = False
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        self.started = True
    
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

class GlobusURLCopy(BaseShell):
    """copy to/from/between globus"""
    globus_url_copy = '/usr/local/globus/bin/globus-url-copy'
    
    def WriteToRemote(self, certfile, remoteurl, fifo=None):
        """starts a copy to remote process and returns you the following (proc, file, url) where:
        proc:   the Popen subprocess python object. Its a child process object.
        file:   the filename of the fifo object to open and write data into
        """
        subenv = self._make_env(certfile)
        
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
            
        url = Fifos.MakeURLForFifo(fifo)
        
        return BaseShell.execute(self,GlobusURLCopyProcessProtocol,certfile,
            [   self.globus_url_copy,
                "-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                "-cd",                                  # create destination directories if they dont exist
                url,                                     # source
                remoteurl                                # destination
            ]
        ), fifo
    
    def ReadFromRemote(self, certfile, remoteurl, fifo=None):
        """Read from a remote url into a local fifo"""
        subenv = self._make_env(certfile)
        
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        url = Fifos.MakeURLForFifo(fifo)
        #print "READ:",fifo,url,remoteurl
        
        return BaseShell.execute(self,GlobusURLCopyProcessProtocol,certfile,
            [  self.globus_url_copy,
                                    "-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                    remoteurl,                               # source
                                    url                                      # destination
            ]
        ), fifo
        