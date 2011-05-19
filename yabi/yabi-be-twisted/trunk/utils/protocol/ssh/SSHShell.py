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
import os
from twisted.internet import protocol
from twisted.internet import reactor

from BaseShell import BaseShell, BaseShellProcessProtocol
from SSHRun import SSHExecProcessProtocol 


DEBUG = False

def convert_filename_to_encoded_for_echo(filename):
    """This function takes a filename, and encodes the whole thing to a back ticked eval command.
    This enables us to completely encode a full filename across ssh without any nasty side effects from special characters"""
    CHARS_TO_REPLACE = '\\' + "'" + '"' + "$@!~|<>#;*[]{}?%^&()= "
    for char in CHARS_TO_REPLACE:
        filename=filename.replace(char,"\\x%x"%(ord(char)))
    return filename

class SSHShell(BaseShell):
    ssh_exec = os.path.join( os.path.dirname(os.path.realpath(__file__)), "ssh-exec.py" )
    python = "/usr/bin/python"
    
    def _make_path(self):
        return "/usr/bin"    

    def _make_echo(self,filename):
        """Turn a filename into the remote eval line"""
        result = '"`echo -e \'%s\'`"'%(convert_filename_to_encoded_for_echo(filename))
        return result

    def execute(self, certfile, host, command, username, password, port=None):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""
        port = port or 22
        
        subenv = self._make_env()
        
        command = [ self.python, self.ssh_exec,
            "-i", certfile,
            "-P", str(port),
            "-x", " ".join(command),
            "%s@%s"%(username,host)
            ]
        
        if DEBUG:
            print "SSHShell Running:",command
            
        return BaseShell.execute(self,SSHExecProcessProtocol(password),command)
      
    def ls(self, certfile, host, directory,username, password, args="-lFR", port=None):
        return self.execute(certfile,host,command=["ls",args,self._make_echo(directory)],username=username, password=password, port=port)
      
    def mkdir(self, certfile, host, directory,username, password, args="-p", port=None):
        return self.execute(certfile,host,command=["mkdir",args,self._make_echo(directory)],username=username, password=password, port=port)
      
    def rm(self, certfile, host, directory,username, password, args=None, port=None):
        return self.execute(certfile,host,command=["rm",args,self._make_echo(directory)],username=username, password=password, port=port) if args else self.execute(certfile,host,command=["rm",self._make_echo(directory)],username=username, password=password, port=port) 

    def ln(self, certfile, host, target, link, username, password, args="-s", port=None):
        return self.execute(certfile,host,command=["ln",args,self._make_echo(target),self._make_echo(link)],username=username, password=password, port=port) if args else self.execute(certfile,host,command=["ln",self._make_echo(target),self._make_echo(link)],username=username, password=password, port=port)
        
    def cp(self, certfile, host, src, dst, username, password, args=None, port=None):
        # if the coipy is recursive, and the src ends in a slash, then we should add a wildcard '*' to the src to make it copy the contents of the directory
        if args is not None and "r" in args and src.endswith("/"):
            return self.execute(certfile,host,command=["cp",args,self._make_echo(src)+"*",self._make_echo(dst)],username=username, password=password, port=port) if args else self.execute(certfile,host,command=["cp",self._make_echo(src),self._make_echo(dst)],username=username, password=password, port=port)
        else:
            return self.execute(certfile,host,command=["cp",args,self._make_echo(src),self._make_echo(dst)],username=username, password=password, port=port) if args else self.execute(certfile,host,command=["cp",self._make_echo(src),self._make_echo(dst)],username=username, password=password, port=port)
        
