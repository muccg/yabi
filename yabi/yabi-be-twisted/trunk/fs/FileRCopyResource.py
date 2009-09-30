from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
from utils.submit_helpers import parsePOSTDataRemoteWriter
import weakref
import sys, os

import stackless
from TaskManager.TaskTools import Sleep, Copy, List, Mkdir, GetFailure

class FileRCopyResource(resource.PostableResource):
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
        #print "POST!",request
        
        deferred = parsePOSTDataRemoteWriter( request,
            self.maxMem, self.maxFields, self.maxSize )
        
        # Copy command
        def RCopyCommand(res):
            # source and destination
            if 'src' not in request.args or 'dst' not in request.args:
                return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "copy must specify source 'src' and destination 'dst'\n")
            
            src = request.args['src'][0]
            dst = request.args['dst'][0]
            
            assert src.endswith('/'), "'src' path must end in a '/'"
            if not dst.endswith('/'):
                dst += '/'
            
            # seperate out the backends
            src_be, src_path = src.split("/",1)
            dst_be, dst_path = dst.split("/",1)
            
            print "RCopying from %s -> %s"%(src,dst)
            
            #our http result channel. this stays open until the copy is finished
            result_channel = defer.Deferred()
            
            #
            # our top down tasklet to run
            #
            def rcopy_runner_thread():
                try:
                    # get a recursive listing of the source
                    fsystem = List(path=src,recurse=True)
                    
                    # remember the directories we make so we only make them once
                    created=[]
                    
                    for directory in sorted(fsystem.keys()):
                        # make directory
                        destpath = directory[len(src_path)+1:]
                        if dst+destpath not in created:
                            #print dst+destpath,"not in",created
                            try:
                                Mkdir(dst+destpath)
                            except GetFailure, gf:
                                # ignore. directory probably already exists
                                pass
                            created.append(dst+destpath)
                             
                        for file,size,date in fsystem[directory]['files']:
                            print "Copy(",src_be+directory+"/"+file,",",dst+destpath+'/'+file,")"
                            Copy(src_be+directory+"/"+file,dst+destpath+'/'+file,retry=1)
                            #Sleep(0.5)
                    
                    result_channel.callback(
                                                    http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Copied successfuly\n")
                                )
                except Exception, e:
                    result_channel.callback(
                                                    http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, str(e))
                                )
                    raise

            copier = stackless.tasklet(rcopy_runner_thread)
            copier.setup()
            copier.run()
            
            return result_channel
            
            #return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK: %s\n"%res)
        
        deferred.addCallback(RCopyCommand)
        
        # save failed
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "NOT OK: %s\n"%str(res)) )
        
        return deferred
        
