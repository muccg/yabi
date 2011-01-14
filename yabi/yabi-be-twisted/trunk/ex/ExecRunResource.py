# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http
from twisted.internet import defer

import weakref
import os
import stackless

from utils.parsers import parse_url

from utils.submit_helpers import parsePOSTDataRemoteWriter

DEBUG = False

class ExecRunResource(resource.PostableResource):
    VERSION=0.1
    
    ALLOWED_OVERRIDE = [("walltime",str), ("max_memory",int), ("cpus",int), ("queue",str), ("job_type",str), ("directory",str), ("stdout",str), ("stderr",str), ('module',str)]
    
    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileListResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
    def handle_run(self,request):
        args = request.args
        
        if "yabiusername" not in args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Job submission must have a yabiusername set (so we can get credentials)!\n")
        yabiusername = args['yabiusername'][0]
        
        if "command" not in args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Job submission must have a command!\n")
        command = args['command'][0]
        
        if "uri" not in request.args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No uri provided\n")
            
        # an optional remote info url can be submitted. If it is submitted with a job, then everytime the status of this job changes,
        # this sends a POST to the url with a json key/value set with info on the backend task
        remote_info_url = args['remote_info'][0] if 'remote_info' in args else None

        if DEBUG:
            print "RUN:",command

        uri = request.args['uri'][0]
        scheme, address = parse_url(uri)
        
        if not hasattr(address,"username"):
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No username provided in uri\n")
        
        username = address.username
        path = address.path
        hostname = address.hostname
        
        basepath, filename = os.path.split(path)
        
        # get the backend
        fsresource = self.fsresource()
        if DEBUG:
            print "BACKENDS",fsresource.Backends()
        if scheme not in fsresource.Backends():
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "Backend '%s' not found\n"%scheme)
            
        bend = self.fsresource().GetBackend(scheme)
        
        kwargs={}
        
        # cast any allowed override variables into their proper format
        for key, cast in self.ALLOWED_OVERRIDE:
            if key in args:
                try:
                    val = cast(args[key][0])
                except ValueError, ve:
                    return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Cannot convert parameter '%s' to %s\n"%(key,cast))
                #print "setting",key,"to",cast(args[key][0])
                kwargs[key]=cast(args[key][0])
        
        # we are gonna try submitting the job. We will need to make a deferred to return, because this could take a while
        #client_stream = stream.ProducerStream()
        client_deferred = defer.Deferred()
        
        task = stackless.tasklet(bend.run)
        task.setup(yabiusername, command, basepath, scheme, username, hostname, remote_info_url, client_deferred, **kwargs)
        task.run()
        
        return client_deferred
        #return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream )
        
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        deferred = parsePOSTDataRemoteWriter(request)
        
        def post_parsed(result):
            return self.handle_run(request)
        
        deferred.addCallback(post_parsed)
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission Failed %s\n"%res) )
        
        return deferred

    def http_GET(self, request):
        return self.handle_run(request)
    