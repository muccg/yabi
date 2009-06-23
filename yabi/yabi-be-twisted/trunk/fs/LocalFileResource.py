
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json, stat
from submit_helpers import parsePOSTData, parsePUTData
from FifoPool import Fifos
import subprocess, time

GET_DIR_LIST = True                     # whether when you call GET on a directory, if it returns the same as LIST on that path. False throws an error on a directory.

from BaseFileResource import BaseFileResource

class LocalFileResource(BaseFileResource):
    """This is the resource that connects us to our local filesystem"""
    VERSION=0.1
    NAME="Local File System"
    addSlash = False
    copy = '/bin/cp'
    
    def __init__(self,request=None,path=None, directory="/tmp/test", backend=None):
        """Pass in the backends to be served out by this FSResource"""
        BaseFileResource.__init__(self,request,path)
        
        if path:
            # first part of path is yabi_username
            self.username = path[0]
            
            # together the whole thing is the path
            self.path=path
        else:
            self.path=None
            
        self.backend = backend
        
        self.directory=directory
    
    def PrefixRemotePath(self, urlpath):
        """url path gridftp1/cwellington/bi01/cwellington/work-ZGTlVm25EyG7POq5
        becomes fs path /tmp/filesystem/bi01/cwellington/work-ZGTlVm25EyG7POq5
        """
        return os.path.join(self.directory, "/".join(urlpath.split("/")[2:]))
    
    def GetFilename(self, path=None):
        """Using this classes 'path', return the real FS path that this refers to"""
        return os.path.join(self.directory,sep.join(path or self.path))
    
    def GetReadFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo is passed in, then use that as the fifo rather than creating one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        
        parts = path.split("/")
        username = parts[0]
        path = parts[1:]
        
        src = self.GetFilename(path)
        #print "FS READ:",fifo,src
        
        # the copy to remote command
        proc = subprocess.Popen(    [  self.copy,
                                       src,                                     # source
                                       fifo                                      # destination
                                    ],
                                    stdin=None,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    )
                                    
        # link our process to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, proc )
        
        # callback success
        deferred( proc, fifo )
            
    def GetWriteFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        
        parts = path.split("/")
        username = parts[0]
        path = parts[1:]
            
        dst = self.GetFilename(path)
        #print "FS WRITE:",fifo,dst
        
        # the copy to remote command
        proc = subprocess.Popen(    [  self.copy,
                                       fifo,                                     # source
                                       dst                                      # destination
                                    ],
                                    stdin=None,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    )
                                    
        # link our process to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, proc )
        
        # callback success
        deferred( proc, fifo )
            
    
    ##
    ## PUT: not working yet
    ##
    def http_PUT(self, request):
        fullpath = self.GetFilename()
         
        if not len(self.path[-1]):
            # we end in a slash... this is inappropriate. We have to be the destination file name
            return http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "cannot PUT to a directory")
            
        dirname = os.path.dirname(fullpath)
            
        if not os.path.exists(dirname):
            # make directories
            os.makedirs(dirname)
            
        defferedchain = parsePUTData(request,
            self.maxMem, self.maxFields, self.maxSize, filename=fullpath
            )                   
        
        # save worked.
        defferedchain.addCallback(lambda res: http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK: %s\n"%res) )
        
        # save failed
        defferedchain.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "NOT OK: %s\n"%res) )
        
        return defferedchain
              
    def http_LIST_old(self,request):
        fullpath = self.GetFilename(self.path[1:])
        
        if not os.path.exists(fullpath) or not os.path.isdir(fullpath):
            return http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Path not a directory\n")
        
        contents = os.listdir(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, json.dumps(contents)+"\n")
    
    def http_LIST(self,request,path=None,username=None,recurse=False):
        path = path or self.path
        username = username or self.username
        
        fullpath = self.GetFilename(path[1:])
        
        if not os.path.exists(fullpath) or not os.path.isdir(fullpath):
            return http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Path not a directory\n")
        
        def walktree(top):
            '''recursively descend the directory tree rooted at top,
            calling the callback function for each regular file'''
        
            storage={'files':[],'directories':[]}
            subtrees={}
            
            timeproc = lambda timestamp: time.strftime("%b %d %H:%M",time.localtime(timestamp))
            
            #add details for '.' and '..'
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
        
        contents = walktree(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, json.dumps(contents)+"\n")
    
    def http_MKDIR(self,request,path=None,username=None):
        path = path or self.path
        username = username or self.username
        
        fullpath = self.GetFilename(path[1:])
        
        os.makedirs(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Directory successfully made.\n")
    
    def http_DELETE(self,request,path=None,username=None, recurse=False):
        path = path or self.path
        username = username or self.username
        
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
        
        fullpath = self.GetFilename(path[1:])
        
        del_tree(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Deletion successful.\n")
    
    
    
    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return LocalFileResource(request,segments, directory=self.directory, backend=self.backend), []
    
    