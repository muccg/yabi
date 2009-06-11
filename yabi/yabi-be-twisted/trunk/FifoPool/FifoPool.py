import os
import tempfile
import weakref


class FifoPool(object):
    """FifoPool is a pool of fifo objects. This allows us to quickly ascertain how many transfers are going on.
    This is where fifo's are created and allocated, and also where they are cleaned up."""
    
    def __init__(self, storage=None):
        if storage:
            assert os.path.exists(storage) and os.path.isdir(storage), "Storage directory %s does not exist"%storage
            self.storage = storage
        else:
            self._make_cert_storage()
        
        self._fifos={}
        
    def _make_cert_storage(self):
        """makes a directory for storing the certificates in"""
        self.storage = tempfile.mkdtemp()
        print "FifoPool created in",self.storage
    
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
            
