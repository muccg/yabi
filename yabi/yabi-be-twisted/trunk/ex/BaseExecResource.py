# -*- coding: utf-8 -*-

from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json, sys

from twisted.web2.auth.interfaces import IAuthenticatedRequest, IHTTPUser

from utils.protocol import globus

from twisted.web import client
import json

import subprocess

class BaseExecResource(resource.PostableResource):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    addSlash = False
    
    def __init__(self,request=None,path=None):
        self.request, self.path = request,path
                
    def GetReadFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo is passed in, then use that as the fifo rather than creating one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        assert False, "GetReadFifo() needs to be overridden in the base class"
            
    def GetWriteFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        assert False, "GetWriteFifo() needs to be overridden in the base class"
        
    def render(self, request):
        # if path is none, we are at out pre '/' base resource (eg. GET /fs/file )
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Base Exec Connector Version: %s\n"%self.VERSION)
        
        return http.Response( responsecode.NOT_ACCEPTABLE, {'content-type': http_headers.MimeType('text', 'plain')}, "Execution jobs must be submitted via POST\n")
        
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Base Exec Connector Version: %s\n"%self.VERSION)

    def http_LIST(self,request):
        assert False, "http_LIST needs to be overridden in subclass"

    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return BaseExecResource(request,segments), []
 