import subprocess
import os
#from pythonhdr import PyFile_AsFile
#import ctypes

#libc=ctypes.cdll.LoadLibrary("libc.so.6")
#print libc


## python versions of setvbuf
#def set_file_unbuffered(file):
    #fp = PyFile_AsFile(file)
    
    #libc.setvbuf(fp,None,1,0)
    


class GlobusRun(object):
    globusrun_ws = '/usr/local/globus/bin/globusrun-ws'
    
    def __init__(self):
        pass

    def _make_env(self, certfile):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        
        return subenv

    def run(self, certfile, rslfile):
        """Spawn a process to run an xml job. return the process handler"""
        subenv = self._make_env(certfile)
        proc = subprocess.Popen(    [   self.globusrun_ws,
                                        "-submit",
                                        "-batch",
                                        "-job-description-file",
                                        rslfile,
                                        ],
                                        shell=False,
                                        stdin=None,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        env = subenv,
                                        )

        #set_file_unbuffered(proc.stdout)
        return proc
    
    def status(self, certfile, eprfile):
        subenv = self._make_env(certfile)
        proc = subprocess.Popen(    [   self.globusrun_ws,
                                        "-status",
                                        "-job-epr-file",
                                        eprfile,
                                        ],
                                        shell=False,
                                        stdin=None,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        env = subenv,
                                        )
        return proc
