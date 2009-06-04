
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from os.path import sep
import os

class LocalFileResource(resource.PostableResource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.1
    addSlash = False
    
    def __init__(self,request,path=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path=path
        
    def render(self, request):
        # if path is none, we are at out pre '/' base resource (eg. GET /fs/file )
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Local File FS Connector Version: %s"%self.VERSION)
        
        path = sep.join(self.path)
        page = "page:"+path
        
        # get the file and return it
        fullpath = os.path.join("/tmp/test",path)
        
        # see if file exits
        if not os.path.exists(fullpath):
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "File '%s' not found"%path)
        
        fh = open(fullpath)
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=stream.FileStream(fh))
    
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        return server.parsePOSTData(request,
            self.maxMem, self.maxFields, self.maxSize
            ).addCallback(lambda res: self.render(request))
            
    def http_LIST(self,request):
        filelist = ["1.txt","2.txt"]
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, str(filelist)+"\n\n")
    
    def locateChild(self, request, segments):
        # return our local file resource for these segments
        print "LFR::LC",request,segments
        return LocalFileResource(request,segments), []