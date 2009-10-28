import FSConnector
import os, stat, time
from fs.Exceptions import InvalidPath
from FifoPool import Fifos

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "yabifs"

# the location of the directory we will serve out. This can be overridden in the constuctor if wanted
DIRECTORY = "/tmp/filesystem/"

DEBUG = True

from twisted.internet import protocol
from twisted.internet import reactor

class FSWriteProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        self.started=False
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        self.started=True
        
    def outReceived(self, data):
        self.out += data
        #print "OUT:",data
        
    def errReceived(self, data):
        self.err += data
        #print "ERR:",data
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        #print "OCL"
        pass
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        #print "EXIT:",self.exitcode
        
    def isDone(self):
        return self.exitcode != None
    
    def isStarted(self):
        return self.started


class LocalFilesystem(FSConnector.FSConnector):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="Globus File System"
    copy = '/bin/cp'
    
    def __init__(self, directory=DIRECTORY):
        FSConnector.FSConnector.__init__(self)
        self.directory = directory
    
    def _get_filename(self, path):
        """Using this classes 'path', return the real FS path that this refers to"""
        while len(path) and path[0]=='/':
            path = path[1:]
            
        return os.path.join(self.directory,path)
    
    def rm(self, host, username, path, recurse=False, creds=None):
        if recurse:
            def del_tree(root):
                for path, dirs, files in os.walk(root, False):
                    for fn in files:
                        os.unlink(os.path.join(path, fn))
                    for dn in dirs:
                        os.rmdir(os.path.join(path, dn))
                os.rmdir(root)
        else:
            def del_tree(root):
                os.unlink(root)
        
        fullpath = self._get_filename(path)
        
        del_tree(fullpath)
        return True
    
    def mkdir(self, host, username, path, creds):
        os.makedirs(self._get_filename(path))
        return True
     
    def ls(self, host, username, path, recurse=False, culldots=True, creds={}):
        fullpath = self._get_filename(path)
        if not os.path.exists(fullpath):
            raise InvalidPath("Invalid path.")
        if not os.path.isdir(fullpath):
            raise InvalidPath("Path is not a directory")
        
        #print "FULLPATH:",fullpath
        
        def walktree(top):
            '''recursively descend the directory tree rooted at top,
            calling the callback function for each regular file'''
        
            storage={'files':[],'directories':[]}
            subtrees={}
            
            timeproc = lambda timestamp: time.strftime("%b %d %H:%M",time.localtime(timestamp))
            
            #add details for '.' and '..'
            if not culldots:
                for fname in [".",".."]:
                    pathname=os.path.join(top,fname)
                    storage['directories'].append( (fname,os.stat(pathname)[stat.ST_SIZE],timeproc(os.stat(pathname)[stat.ST_MTIME])) )
            
            for f in os.listdir(top):
                pathname = os.path.join(top, f)
                mode = os.stat(pathname)[stat.ST_MODE]
                if stat.S_ISDIR(mode):
                    # It's a directory, 
                    storage['directories'].append( (f,os.stat(pathname)[stat.ST_SIZE],timeproc(os.stat(pathname)[stat.ST_MTIME])) )
                    if recurse:
                        #recurse into it
                        stackless.schedule()            # schedule the tasklet to keep other tasklets running
                        sub = walktree(pathname)
                        subtrees.update(sub)
                elif stat.S_ISREG(mode):
                    # It's a file, call the callback function
                    storage['files'].append( (f,os.stat(pathname)[stat.ST_SIZE],timeproc(os.stat(pathname)[stat.ST_MTIME])) )
                else:
                    # Unknown file type, print a message
                    #print 'Skipping %s' % pathname
                    pass
                    
            shortenedpath = "/"+username+top[len(self.directory):]              # munge the filename into its url part path
            subtrees[shortenedpath]=storage
            return subtrees
        
        return walktree(fullpath)

    def _make_env(self):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        return subenv
    
    def _make_path(self):
        return "/bin"

    def GetWriteFifo(self, host=None, username=None, path=None, filename=None, fifo=None, creds={}):
        """sets up the chain needed to setup a write fifo to a remote path as a certain user.
        """
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        
        dst = os.path.join(self._get_filename(path),filename)
        
        # the copy to remote command
        procproto = FSWriteProtocol()
        
        reactor.spawnProcess(   procproto,
                                self.copy,
                                [ self.copy, fifo, dst ],
                                env=self._make_env(),
                                path=self._make_path()
                            )
        
        # link our protocol processor to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, procproto )
        
        return procproto, fifo
            
    def GetReadFifo(self, host=None, username=None, path=None, filename=None, fifo=None, creds={}):
        """sets up the chain needed to setup a write fifo to a remote path as a certain user.
        """
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        
        dst = os.path.join(self._get_filename(path),filename)
        
        # the copy to remote command
        procproto = FSWriteProtocol()
        
        reactor.spawnProcess(   procproto,
                                self.copy,
                                [ self.copy, dst, fifo ],
                                env=self._make_env(),
                                path=self._make_path()
                            )
        
        # link our protocol processor to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, procproto )
        
        return procproto, fifo
            
    
        