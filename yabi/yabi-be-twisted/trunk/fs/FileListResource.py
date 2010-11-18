# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref
import sys, os
import stackless
import json

from Exceptions import PermissionDenied, InvalidPath, BlockingException
from globus.Auth import NoCredentials, AuthException
from globus.CertificateProxy import ProxyInitError

from utils.parsers import parse_url

from utils.submit_helpers import parsePOSTData

DEBUG = False

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
        
    def old_http_POST(self, request):
        # break our request path into parts
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "request must be GET\n")

    def handle_list(self, request):
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
        
        # compile any credentials together to pass to backend
        creds={}
        for varname in ['key','password','username','cert']:
            if varname in request.args:
                creds[varname] = request.args[varname][0]
                del request.args[varname]
        
        yabiusername = request.args['yabiusername'][0] if "yabiusername" in request.args else None
        
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "URI",uri
            print "ADDRESS",address
        
        # get the backend
        fsresource = self.fsresource()
        if bendname not in fsresource.Backends():
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "Backend '%s' not found\n"%bendname)
            
        bend = fsresource.GetBackend(bendname)
        
        # our client channel
        client_channel = defer.Deferred()
        
        def do_list():
            if DEBUG:
                print "dolist() hostname=",hostname,"path=",path,"username=",username,"recurse=",recurse
            try:
                lister=bend.ls(hostname,path=path, username=username,recurse=recurse, yabiusername=yabiusername, creds=creds)
                client_channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=json.dumps(lister)))
            except BlockingException, be:
                client_channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, stream=str(be)))
            except (PermissionDenied,NoCredentials,InvalidPath,ProxyInitError), exception:
                #print "IP"
                client_channel.callback(http.Response( responsecode.FORBIDDEN, {'content-type': http_headers.MimeType('text', 'plain')}, stream=str(exception)))
                #print "POST CALLBACK"
            except Exception, e:
                client_channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream=str(exception)))
            
        tasklet = stackless.tasklet(do_list)
        tasklet.setup()
        tasklet.run()
        
        return client_channel
            
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        deferred = parsePOSTData(request)
        
        def post_parsed(result):
            return self.handle_list(request)
        
        deferred.addCallback(post_parsed)
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission Failed %s\n"%res) )
        
        return deferred

    def http_GET(self, request):
        return self.handle_list(request)
