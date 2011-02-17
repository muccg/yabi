# -*- coding: utf-8 -*-
import os
from twisted.internet import protocol
from twisted.internet import reactor

from BaseShell import BaseShell, BaseShellProcessProtocol

DEBUG = False

def convert_filename_to_encoded_for_echo(filename):
    """This function takes a filename, and encodes the whole thing to a back ticked eval command.
    This enables us to completely encode a full filename across ssh without any nasty side effects from special characters"""
    CHARS_TO_REPLACE = '\\' + "'" + '"' + "$@!~|<>#;*[]{}?%^&()="
    for char in CHARS_TO_REPLACE:
        filename=filename.replace(char,"\\x%x"%(ord(char)))
    return filename

class GlobusShellProcessProtocol(BaseShellProcessProtocol):
    pass

class GlobusShell(BaseShell):
    gsissh = '/usr/local/globus/bin/gsissh'
    
    def _make_path(self):
        return "/usr/local/globus/bin"    
    
    def _make_echo(self,filename):
        """Turn a filename into the remote eval line"""
        return '"`echo -e \'%s\'`"'%(convert_filename_to_encoded_for_echo(filename))

    def execute(self, certfile, host, command):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""
        if DEBUG:
            print "GlobusShell running:",[ 
                self.gsissh, 
                host 
            ] + list(command)
        return BaseShell.execute(self,GlobusShellProcessProtocol,certfile,
            [ 
                self.gsissh, 
                host 
            ] + list(command)
        )
    def ls(self, certfile, host, directory, args="-lFR", port=None):
        return self.execute(certfile,host,command=["ls",args,self._make_echo(directory)])
      
    def mkdir(self, certfile, host, directory, args="-p", port=None):
        return self.execute(certfile,host,command=["mkdir",args,self._make_echo(directory)])
      
    def rm(self, certfile, host, directory, args=None, port=None):
        return self.execute(certfile,host,command=["rm",args,self._make_echo(directory)]) if args else self.execute(certfile,host,command=["rm",self._make_echo(directory)]) 
