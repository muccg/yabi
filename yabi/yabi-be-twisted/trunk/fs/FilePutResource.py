from twisted.web2 import resource, http_headers, responsecode, http, server, fileupload
from twisted.internet import defer, reactor

import weakref
import sys, os
import stackless
import json
from MimeStreamDecoder import MimeStreamDecoder, no_intr

from Exceptions import PermissionDenied, InvalidPath
from globus.Auth import NoCredentials
from globus.CertificateProxy import ProxyInitError

from utils.stacklesstools import WaitForDeferredData
from utils.parsers import parse_url

from twisted.internet.defer import Deferred

from utils.submit_helpers import parsePOSTData

UPLOAD_BLOCK_SIZE = 1024 * 256

class FilePutResource(resource.PostableResource):
    VERSION=0.1
    maxMem = 100*1024
    maxFields = 16
    maxSize = 10*1024*102
    
    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileListResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
    def render(self, request):
        # break our request path into parts
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "request must be POST\n")
                        
    def http_POST(self, request):
        if "uri" not in request.args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No uri provided in GET parameters\n")

        uri = request.args['uri'][0]
        scheme, address = parse_url(uri)
        
        # compile any credentials together to pass to backend
        creds={}
        for varname in ['key','password','username','cert']:
            if varname in request.args:
                creds[varname] = request.args[varname][0]
                del request.args[varname]
        
        if not hasattr(address,"username"):
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No username provided in uri\n")
        
        bendname = scheme
        username = address.username
        path = address.path
        hostname = address.hostname
        
        # get the backend
        fsresource = self.fsresource()
        if bendname not in fsresource.Backends():
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "Backend '%s' not found\n"%bendname)
            
        # our client channel
        client_channel = defer.Deferred()
        
        def upload_tasklet(req, channel):
            """Tasklet to do file upload"""
            ctype = request.headers.getHeader('content-type')
            
            if (ctype.mediaType == 'application' and ctype.mediaSubtype == 'x-www-form-urlencoded'):
                reader = req.stream.read()
                
                while True:
                    #print "DATA:",WaitForDeferredData(reader)
                    stackless.schedule()
                
                raise Exception
            elif (ctype.mediaType == 'multipart' and ctype.mediaSubtype == 'form-data'):
                boundary = ctype.params.get('boundary')
                if boundary is None:
                    return channel.callback(http.HTTPError(http.StatusResponse(responsecode.BAD_REQUEST,"Boundary not specified in Content-Type.")))
                
                #print "Boundary:",boundary
                
                # our backend writer
                bend = self.fsresource().GetBackend(scheme)
                #print "BEND:",bend
                
                class MyMimeStreamDecoder(MimeStreamDecoder):
                    """Override this class and put in our own file open methods"""
                    def open_write_stream(self, filename):
                        #print "Uploading file:",filename
                        self.procproto, fifo = bend.GetWriteFifo(hostname,username,path,filename, creds=creds)
                        self.fileopen = no_intr(open,fifo,"wb")
                        
                    def close_write_stream(self):
                        """do the close, but also check the process result"""
                        MimeStreamDecoder.close_write_stream(self)
                        
                        # wait for copy fifo process to exit
                        while not self.procproto.isDone():
                            stackless.schedule()
                        
                        # if in error state, report error
                        if self.procproto.exitcode:
                            raise IOError(self.procproto.err)
                
                parser = MyMimeStreamDecoder()
                parser.set_boundary(boundary)
                
                reader = req.stream.read()
                
                try:
                    while reader is not None:
                        dat = WaitForDeferredData(reader)
                        
                        # process data snippet
                        parser.feed(dat)
                        
                        reader = req.stream.read()
                        stackless.schedule()
                except IOError, ioe:
                    #print "IOError!!!",ioe
                    # sleep until the task finished
                    while not parser.procproto.isDone():
                        stackless.schedule()
                    return channel.callback(http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "File upload failed: %s\n"%parser.procproto.err))

                return channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK\n"))
            else:
                return channel.callback(http.Response( responsecode.BAD_REQUEST, "Invalid content-type: %s/%s" % (ctype.mediaType, ctype.mediaSubtype)))
            
        
        tasklet = stackless.tasklet(upload_tasklet)
        tasklet.setup( request, client_channel )
        tasklet.run()
        
        return client_channel
