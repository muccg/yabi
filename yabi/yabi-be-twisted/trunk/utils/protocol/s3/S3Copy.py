# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
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
            
        command = [   self.python, self.s3cp,
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