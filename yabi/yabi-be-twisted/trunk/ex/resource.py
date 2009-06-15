"""Our twisted filesystem server resource"""

from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
from submit_helpers import parsePOSTDataRemoteWriter
import weakref
import sys, os

class ExecResource(resource.Resource):
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
            page = "Yabi Exec Connector Resource Version: %s\n"%self.VERSION
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