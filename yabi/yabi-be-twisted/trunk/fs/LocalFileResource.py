
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json
from submit_helpers import parsePOSTData, parsePUTData
from FifoPool import Fifos
import subprocess

GET_DIR_LIST = True                     # whether when you call GET on a directory, if it returns the same as LIST on that path. False throws an error on a directory.

class LocalFileResource(resource.PostableResource):
    """This is the resource that connects us to our local filesystem"""
    VERSION=0.1
    addSlash = False
    copy = '/bin/cp'
    
    def __init__(self,request=None,path=None, directory="/tmp/test", backend=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path=path
        self.backend = backend
        
        self.directory=directory
        
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
        src = self.GetFilename(path.split('/'))
        print "FS READ:",fifo,src
        
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
        dst = self.GetFilename(path.split('/'))
        print "FS WRITE:",fifo,dst
        
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
            
    
    def render(self, request):
        # if path is none, we are at out pre '/' base resource (eg. GET /fs/file )
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Local File FS Connector Version: %s\n"%self.VERSION)
        
        fullpath = self.GetFilename()
        
        # see if file exits
        if not os.path.exists(fullpath):
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "File '%s' not found\n"%sep.join(self.path))
        
        if GET_DIR_LIST and os.path.isdir(fullpath):
            return self.http_LIST(request)
        
        fh = open(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=stream.FileStream(fh))
    
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        fullpath = self.GetFilename()
        
        if not os.path.exists(fullpath):
            # make directories
            os.makedirs(fullpath)
            
        defferedchain = parsePOSTData(request,
            self.maxMem, self.maxFields, self.maxSize, basepath=fullpath
            )                   
        
        # save worked.
        defferedchain.addCallback(lambda res: http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK: %s\n"%res) )
        
        # save failed
        defferedchain.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "NOT OK: %s\n"%res) )
        
        return defferedchain
        
        
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
              
    def http_LIST(self,request):
        fullpath = self.GetFilename()
        
        if not os.path.exists(fullpath) or not os.path.isdir(fullpath):
            return http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Path not a directory\n")
        
        contents = os.listdir(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, json.dumps(contents)+"\n")
    
    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return LocalFileResource(request,segments, directory=self.directory, backend=self.backend), []
    
    