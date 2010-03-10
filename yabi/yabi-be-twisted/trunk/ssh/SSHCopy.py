# -*- coding: utf-8 -*-
"""Implement scp connections"""

import os
import tempfile

from FifoPool import Fifos

from BaseShell import BaseShell, BaseShellProcessProtocol

class SCPProcessProtocol(BaseShellProcessProtocol):
    def __init__(self):
        BaseShellProcessProtocol.__init__(self)
        self.started = False
        
    def connectionMade(self):
        self.transport.closeStdin()
        self.started = True
        
    def isStarted(self):
        return self.started
        
class SCPError(Exception):
    pass

class SSHCopy(BaseShell):
    scp = "ssh-copy"
    
    def WriteToRemote(self, certfile, remoteurl, fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
            
        remotehost,remotepath = remoteurl.split(':',1)
            
        command = [   self.scp,
                "-C",                       # compress
                "-i",certfile,              # keyfile
                "-P","22",                  # port
                "-q",                       # quiet
                fifo,                       # localfile
                remoteurl
            ]
        print "C:",command
            
        return BaseShell.execute(self,SCPProcessProtocol,
            command
        ), fifo
        #return BaseShell.execute(self,SCPProcessProtocol,
            #[   self.scp,
                #"-C",                       # compress
                #"-i",certfile,              # keyfile
                #"-P","22",                  # port
                #"-q",                       # quiet
                #fifo,                       # localfile
                #remoteurl
            #]
        #), fifo
        
    def ReadFromRemote(self,certfile,remoteurl,fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
            
        return BaseShell.execute(self,SCPProcessProtocol,
            [   self.scp,
                "-C",
                "-i",certfile,
                "-P","22",
                "-q",
                remoteurl,
                fifo
            ]
        ), fifo