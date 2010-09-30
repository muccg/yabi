# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http
from twisted.internet import defer

import weakref

from utils.submit_helpers import parsePOSTDataRemoteWriter

DEBUG = False

class ExecInfoResource(resource.PostableResource):
    VERSION=0.1

    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path

        if not fsresource:
            raise Exception, "FileListResource must be informed on construction as to which FSResource is its parent"

        self.fsresource = weakref.ref(fsresource)

    def handle_info(self,request):
        args = request.args

        if "yabiusername" not in args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Job info must have a yabiusername set (so we can get credentials)!\n")
        yabiusername = args['yabiusername'][0]

        if "jobid" not in args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Job info must have a jobid!\n")
        command = args['command'][0]

        # we are gonna try submitting the job. We will need to make a deferred to return, because this could take a while
        #client_stream = stream.ProducerStream()
        client_deferred = defer.Deferred()

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
            return self.handle_info(request)

        deferred.addCallback(post_parsed)
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "Job Submission Failed %s\n"%res) )

        return deferred

    def http_GET(self, request):
        return self.handle_info(request)
