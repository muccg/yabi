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
"""Implement scp connections"""

import os
import sys
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
    python = sys.executable
    
    def WriteToRemote(self, certfile, remoteurl, port=None, password="",fifo=None):
        subenv = self._make_env()
        
        port = port or 22
        
        if not fifo:
            fifo = Fifos.Get()
            
        remotehost,remotepath = remoteurl.split(':',1)
            
        command = [   self.python, self.scp,
                "-i",certfile,              # keyfile
                "-P",str(port),                  # port
                fifo,                       # localfile
                remoteurl
            ]
            
        return BaseShell.execute(self,SCPProcessProtocol(password),
            command
        ), fifo
        
    def ReadFromRemote(self,certfile,remoteurl,port=None,password="",fifo=None):
        subenv = self._make_env()
        
        port = port or 22
        
        if not fifo:
            fifo = Fifos.Get()
            
        return BaseShell.execute(self,SCPProcessProtocol(password),
            [   self.python, self.scp,
                "-i",certfile,
                "-P",str(port),
                remoteurl,
                fifo
            ]
        ), fifo