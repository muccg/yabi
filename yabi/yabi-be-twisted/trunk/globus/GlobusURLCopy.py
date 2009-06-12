"""Class to encapsulate the functionality in "globus-url-copy"
"""
import subprocess
import os
import tempfile
import sys
from FifoPool import Fifos

class GlobusFTPError(Exception):
    pass

def _globus_process_error(string):
    """parse the response from globus_url_copy and return an error code and a message"""
    lines = string.split("\n")
    numlines = [line.strip() for line in lines if  len(line) and '0' <= line[0] <= '9']               # lines that begin with a number
    
    # lets take numbered line 0 as our information line
    info = numlines[0]
    
    parts = info.split()
    
    if parts[0]=="1)":
        #certificate problems
        raise GlobusFTPError, (0,"Couldn't use proxyfile to auth connection")
    
    return int(parts[0])," ".join(parts[1:])

class GlobusURLCopy(object):
    """copy to/from/between globus"""
    globus_url_copy = '/usr/local/globus/bin/globus-url-copy'
    
    def __init__(self):
        pass
    
    def _make_env(self, certfile):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        subenv['X509_USER_PROXY'] = certfile
        
        return subenv
    
    def ListRemote(self, certfile, url):
        """
        Return a list of files and directories at that url.
        
        TODO: what if this blocks?
        """
        # environment for our subprocess
        subenv = self._make_env(certfile)
        
        # the list command
        proc = subprocess.Popen(    [  self.globus_url_copy,
                                        "-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                        "-list",    url
                                    ],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    env=subenv  )
                                 
        stdout, stderr = proc.communicate()                          # run list command: TODO: NON BLOCKING
        
        result = proc.returncode
        
        if result:
            # process the error. turn into and error code and a message. then raise this as an exception
            code, message = _globus_process_error(stdout)
            raise GlobusFTPError, (code, message)
        
        # assume we worked. Parse output into file listing
        lines = stdout.split("\n")
        
        assert lines[0]==url, "returned url header does not match passed in header"
        
        return [(line2[:-1] if line2[-1]==u"\u0000" else line2) for line2 in [line.strip() for line in lines[1:] if len(line)]]
    
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
        print "WRITE:",fifo,url,remoteurl
        
        # the copy to remote command
        proc = subprocess.Popen(    [  self.globus_url_copy,
                                        #"-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                        url,                                     # source
                                        remoteurl                                # destination
                                    ],
                                    stdin=None,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    #close_fds=True,
                                    env=subenv  )
                                    
        # link our process to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, proc )
        
        return proc, fifo
    
    def ReadFromRemote(self, certfile, remoteurl, fifo=None):
        """Read from a remote url into a local fifo"""
        subenv = self._make_env(certfile)
        
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        url = Fifos.MakeURLForFifo(fifo)
        print "READ:",fifo,url,remoteurl
        
        # the copy to remote command
        proc = subprocess.Popen(    [  self.globus_url_copy,
                                        #"-nodcau",                              # see bug #3902 ( http://bugzilla.globus.org/globus/show_bug.cgi?id=3902 )
                                        remoteurl,                               # source
                                        url                                      # destination
                                    ],
                                    stdin=None,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    #close_fds=True,
                                    env=subenv  )
                                    
        Fifos.WeakLink( fifo, proc )
        
        return proc, fifo
    
    
        