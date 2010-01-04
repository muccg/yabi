# -*- coding: utf-8 -*-
import os
import tempfile
import weakref

from conf import config

class FifoPool(object):
    """FifoPool is a pool of fifo objects. This allows us to quickly ascertain how many transfers are going on.
    This is where fifo's are created and allocated, and also where they are cleaned up."""
    
    def __init__(self, storage=None):
        if storage:
            assert os.path.exists(storage) and os.path.isdir(storage), "Storage directory %s does not exist"%storage
            self.storage = storage
        else:
            self._make_fifo_storage()
        
        self._fifos={}
        
    def _make_fifo_storage(self, directory=None):
        """makes a directory for storing the fifos in"""
        directory = directory or config.config['backend']['fifos']
        self.storage = tempfile.mkdtemp(prefix="yabi-fifo-", dir=directory)
        #print "FifoPool created in",self.storage
    
    def _make_fifo(self, prefix="fifo_",suffix=""):
        """make a fifo on the filesystem and return its path"""
        filename = tempfile.mktemp(suffix=suffix, prefix=prefix, dir=self.storage)                # insecure, but we dont care
        os.mkfifo(filename, 0600)
        return filename
    
    def Get(self):
        """return a new fifo path"""
        fifo = self._make_fifo()
        self._fifos[fifo]=[]
        return fifo
        
    def WeakLink(self, fifo, *procs):
        """Link the running proccesses to our fifo. Weak refs are used. When all the weakrefs for a fifo expire, the fifo is deleted. AUTOMAGICAL power of weakrefs"""
        
        # a closure to remove the fifo if the list is empty
        def remove_ref( weak ):
            self._fifos[fifo].remove(weak)
            if not self._fifos[fifo]:
                # empty. delete us
                os.unlink(fifo)
                del self._fifos[fifo]
        
        for proc in procs:
            ref = weakref.ref( proc, remove_ref )
            self._fifos[fifo].append(ref)
            
    def MakeURLForFifo(self,filename):
        return "file://"+os.path.normpath(filename)