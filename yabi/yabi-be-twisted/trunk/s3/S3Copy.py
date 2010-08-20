# -*- coding: utf-8 -*-
"""Implement s3 copies"""

import os
import tempfile

from FifoPool import Fifos

from BaseShell import BaseShell, BaseShellProcessProtocol

class S3CopyProcessProtocol(BaseShellProcessProtocol):
    def __init__(self, cert, password):
        BaseShellProcessProtocol.__init__(self)
        self.started = False
        self.cert = cert
        self.password = password
        
    def connectionMade(self):
        #print "Connection made"
        self.transport.write(str(self.cert))
        self.transport.write("\n")
        self.transport.write(str(self.password))
        self.transport.write("\n")
        self.transport.closeStdin()
        self.started = True
                
    def isStarted(self):
        return self.started
        
class S3Error(Exception):
    pass

class S3Copy(BaseShell):
    s3cp = os.path.join( os.path.dirname(os.path.realpath(__file__)), "s3-copy.py" )
    python = "/usr/bin/python"
    
    def WriteToRemote(self, cert, remoteurl, password="",fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
            
        remotehost,remotepath = remoteurl.split(':',1)
            
        command = [   self.python, self.scp,
                fifo,                       # localfile
                remoteurl
            ]
            
        return BaseShell.execute(self,S3CopyProcessProtocol(cert,password),
            command
        ), fifo
        
    def ReadFromRemote(self,cert,remoteurl,password="",fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
            
        return BaseShell.execute(self,S3CopyProcessProtocol(cert,password),
            [   self.python, self.s3cp,
                remoteurl,
                fifo
            ]
        ), fifo