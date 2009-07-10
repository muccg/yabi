from AsyncWrapper import AExec as Popen
from subprocess import PIPE,  STDOUT
import os
#from pythonhdr import PyFile_AsFile
#import ctypes

#libc=ctypes.cdll.LoadLibrary("libc.so.6")
#print libc


## python versions of setvbuf
#def set_file_unbuffered(file):
    #fp = PyFile_AsFile(file)
    
    #libc.setvbuf(fp,None,1,0)
    


class GlobusShell(object):
    gsissh = '/usr/local/globus/bin/gsissh'
    
    def __init__(self):
        pass

    def _make_env(self, certfile):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        
        return subenv

    def execute(self, certfile, host, *command):
        """Run inside gsissh, this command line. Command parts are passed in as a list of parameters, not a string."""

        # TODO FIXME
        #
        # Calling Popen is currently broken in Twisted. This is due to the way signal handling is done in twisted.
        # Reference:  http://twistedmatrix.com/trac/ticket/733
        # A quick google can find plenty of other references and various workarounds.
        #
        # Suggestion: Use spawnProcess within the twisted api. Specifically there is some utils code within the 
        # twisted api which makes this really easy.
        # Reference: http://twistedmatrix.com/documents/8.2.0/api/twisted.internet.utils.html


        subenv = self._make_env(certfile)
        proc = Popen( [  self.gsissh,
                                    host ] +
                                  list(command),
                                  shell=False,
                                  stdin=None,
                                  stdout=PIPE,
                                  stderr=STDOUT,
                                  env=subenv,
                                  bufsize=1024
                                )
        return proc

    def ls(self, certfile, host, directory, args="-alFR"):
        return self.execute(certfile,host,"ls",args,directory)

    def mkdir(self, certfile, host, directory, args="-p"):
        return self.execute(certfile,host,"mkdir",args,directory)
    
    def rm(self, certfile, host, directory, args=None):
        return self.execute(certfile,host,"rm",args,directory) if args else self.execute(certfile,host,"rm",directory)
    
