"""Our twisted filesystem server resource"""

from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer
from submit_helpers import parsePOSTDataRemoteWriter
import weakref

class FileCopyResource(resource.PostableResource):
    VERSION=0.1
    maxMem = 100*1024
    maxFields = 16
    maxSize = 10*1024*102
    
    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileCopyResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
    def render(self, request):
        # break our request path into parts
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "request must be POST\n")

    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        
        NOTE: parameters must be Content-Type: application/x-www-form-urlencoded
        eg. 
        """
        deferred = parsePOSTDataRemoteWriter( request,
            self.maxMem, self.maxFields, self.maxSize )
        
        # Copy command
        def CopyCommand(res):
            # source and destination
            if 'src' not in request.args or 'dst' not in request.args:
                return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "copy must specify source 'src' and destination 'dst'\n")
            
            src = request.args['src'][0]
            dst = request.args['dst'][0]
            
            print "Copying from %s -> %s"%(src,dst)
            
            # seperate out the backends
            src_be, src_path = src.split("/",1)
            dst_be, dst_path = dst.split("/",1)
            
            # get our actual backend objects
            sbend = getattr(self.fsresource(), "child_%s"%src_be)
            dbend = getattr(self.fsresource(), "child_%s"%dst_be)
            
            print "Copying from",sbend,"to",dbend
            
            #readproc, readfifo = sbend.
            
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK: %s\n"%res)
        
        deferred.addCallback(CopyCommand)
        
        # save failed
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "NOT OK: %s\n"%str(res)) )
        
        return deferred
        

class FSResource(resource.Resource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.1
    addSlash = True
    
    def __init__(self,*args,**kwargs):
        """Pass in the backends to be served out by this FSResource"""
        self.backends={}
        for name, bend in kwargs.iteritems():
            bend.backend = name                     # store the name in the backend, so the backend knows about it
            self.backends[name]=bend
            self.putChild(name,bend)
        
    def render(self, request):
        # break our request path into parts
        parts = request.path.split("/")
        assert parts[0]=="", "Expected a leading '/' on the request path"
        
        backendname = parts[2]
        
        # no name? just status
        if not backendname and len(parts)==3:
            # status page
            page = "Yabi Filesystem Connector Resource Version: %s\n"%self.VERSION
            page += "Available backends: "+", ".join(self.backends.keys())
            page += "\n\n"
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, page)
        
        # check for backend name
        if backendname not in self.backends:
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "Backend '%s' not found"%backendname)
        
        backend = self.backends[backendname]
        page = "Hello, %s!"%backend
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, page)
    
    def locateChild(self, request, segments):
        # return our local file resource for these segments
        if segments[0]=="copy":
            # wanting the file copy resource
            return FileCopyResource(request,segments,fsresource = self), []
        return resource.Resource.locateChild(self,request,segments)