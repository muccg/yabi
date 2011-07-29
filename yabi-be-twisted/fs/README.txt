Writing a Filesystem Backend
============================

You pass the backends in as parameters to FSResource constructor, eg:
    
        # our handlers
        self.child_fs = FSResource(
                file=LocalFileResource(directory="/tmp/filesystem"),
                gridftp1=GlobusFileResource(remoteserver="xe-gt4.ivec.org", remotepath="/scratch"),
                gridftp2=GlobusFileResource(remoteserver="xe-gt4.ivec.org", remotepath="/scratch/bi01"),
            )

this makes 3 backends. /fs/file, /fs/gridftp1 and /fs/gridftp2



The backend class
-----------------
It must derive from twisted.web2.resource.PostableResource

expose the following methods:
    
    __init__(self,request=None,path=None, ..extras..)
        locateChild() is called on a resource, which then *constructs a new* copy of itself. pass in the parameters to construct with here
        
    GetReadFifo(self, path, deferred, fifo=None)
        GetReadFifo creates a read fifo and process to read from the backend path 'path'. Pass in a deferred into it, and it will be called
        when the process is ready to write to the fifo for you to read. TODO: its a callback, not a deferred, right?
        Calls the callback with the parameters ( proc, fifo ), where proc is a python subprocess.Popen object handling the associated write
        process, and fifo is the local file path to the fifo. If fifo is passed in, do not create the fifo, but use the one passed. Also 
        then calls the callback with that same fifo string.
        
    GetWriteFifo(self, path, deferred, fifo=None)
        GetWriteFifo does the same thing but to write to a backend file.
        
    
    
        