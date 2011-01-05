# -*- coding: utf-8 -*-
"""Implement scp connections"""

import os
import tempfile

from FifoPool import Fifos

from BaseShell import BaseShell, BaseShellProcessProtocol

class SCPProcessProtocol(BaseShellProcessProtocol):
    def __init__(self, password):
        BaseShellProcessProtocol.__init__(self)
        self.started = False
        self.password = password
        
    def connectionMade(self):
        #print "Connection made"
        self.transport.write(str(self.password))
        self.transport.write("\n")
        self.transport.closeStdin()
        self.started = True
                
    def isStarted(self):
        return self.started
        
class SCPError(Exception):
    pass

class SSHCopy(BaseShell):
    scp = os.path.join( os.path.dirname(os.path.realpath(__file__)), "ssh-copy-2.py" )
    python = "/usr/bin/python"
    
    def WriteToRemote(self, certfile, remoteurl, password="",fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
            
        remotehost,remotepath = remoteurl.split(':',1)
            
        command = [   self.python, self.scp,
                "-i",certfile,              # keyfile
                "-P","22",                  # port
                fifo,                       # localfile
                remoteurl
            ]
        print "C:",command
            
        return BaseShell.execute(self,SCPProcessProtocol(password),
            command
        ), fifo
        
    def ReadFromRemote(self,certfile,remoteurl,password="",fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
            
        return BaseShell.execute(self,SCPProcessProtocol(password),
            [   self.python, self.scp,
                "-i",certfile,
                "-P","22",
                remoteurl,
                fifo
            ]
        ), fifo