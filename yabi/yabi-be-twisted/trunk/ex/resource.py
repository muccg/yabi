# -*- coding: utf-8 -*-
"""Our twisted filesystem server resource"""

from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor

import weakref
import sys, os

from ExecRunResource import ExecRunResource
from ExecResumeResource import ExecResumeResource
from ExecInfoResource import ExecInfoResource
from utils.BackendResource import BackendResource

class ExecResource(resource.Resource, BackendResource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.2
    addSlash = True
    
    def __init__(self,*args,**kwargs):
        BackendResource.__init__(self,*args,**kwargs)
        
    def LoadConnectors(self, quiet=False):
        """Load all the backend connectors into our backends"""
        import connector
        return BackendResource.LoadConnectors(self,connector,'ExecConnector','exec', quiet=quiet)
  
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
        if segments[0]=="run":
            return ExecRunResource(request,segments,fsresource = self), []
        elif segments[0]=="resume":
            return ExecResumeResource(request,segments,fsresource = self), []
        elif segments[0]=="info":
            return ExecInfoResource(request,segments,fsresource = self), []
            
        
        return resource.Resource.locateChild(self,request,segments)
        