from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref
import sys, os
import stackless
import json

from Exceptions import PermissionDenied, InvalidPath
from globus.Auth import NoCredentials
from globus.CertificateProxy import ProxyInitError

from utils.parsers import parse_url

class FileListResource(resource.PostableResource):
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
        
    def http_POST(self, request):
        # break our request path into parts
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "request must be GET\n")

    def http_GET(self, request):
        if "uri" not in request.args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No uri provided\n")

        uri = request.args['uri'][0]
        scheme, address = parse_url(uri)
        
        if not hasattr(address,"username"):
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No username provided in uri\n")
        
        recurse = 'recurse' in request.args
        bendname = scheme
        username = address.username
        path = address.path
        hostname = address.hostname
        
        #print "URI",uri
        #print "ADDRESS",address
        
        # get the backend
        fsresource = self.fsresource()
        if bendname not in fsresource.Backends():
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "Backend '%s' not found\n"%bendname)
            
        bend = fsresource.GetBackend(bendname)
        
        # our client channel
        client_channel = defer.Deferred()
        
        def do_list():
            print "dolist() hostname=",hostname,"path=",path,"username=",username,"recurse=",recurse
            try:
                lister=bend.ls(hostname,path=path, username=username,recurse=recurse)
                client_channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=json.dumps(lister)))
            except (PermissionDenied,NoCredentials,InvalidPath,ProxyInitError), exception:
                print "IP"
                client_channel.callback(http.Response( responsecode.FORBIDDEN, {'content-type': http_headers.MimeType('text', 'plain')}, stream=str(exception)))
                print "POST CALLBACK"
            
        tasklet = stackless.tasklet(do_list)
        tasklet.setup()
        tasklet.run()
        
        return client_channel
