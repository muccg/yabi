# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
from utils.submit_helpers import parsePOSTDataRemoteWriter
import weakref
import sys, os

import stackless
from TaskManager.TaskTools import Sleep, Copy, List, Mkdir, GETFailure

from utils.parsers import parse_url
from utils.stacklesstools import GETFailure

from Exceptions import BlockingException

DEBUG = False

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
            
            yabiusername = request.args['yabiusername'][0] if "yabiusername" in request.args else None
        
            assert yabiusername, "You pass in a yabiusername so I can go get a credential."
            
            assert src.endswith('/'), "'src' path must end in a '/'"
            if not dst.endswith('/'):
                dst += '/'
            
            # parse the source and dest uris
            src_scheme, src_address = parse_url(src)
            dst_scheme, dst_address = parse_url(dst)
            
            src_username = src_address.username
            dst_username = dst_address.username
            src_path, src_filename = os.path.split(src_address.path)
            dst_path, dst_filename = os.path.split(dst_address.path)
            src_hostname = src_address.hostname
            dst_hostname = dst_address.hostname
            
            # backends
            sbend = self.fsresource().GetBackend(src_scheme)
            dbend = self.fsresource().GetBackend(dst_scheme)
            
            #print "RCopying from %s -> %s"%(src,dst)
            
            #our http result channel. this stays open until the copy is finished
            result_channel = defer.Deferred()
            
            #
            # our top down tasklet to run
            #
            def rcopy_runner_thread():
                try:
                    # get a recursive listing of the source
                    try:
                        fsystem = List(path=src,recurse=True,yabiusername=yabiusername)
                    except BlockingException, be:
                        result_channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, str(be)) )
                    
                    #print "Fsystem:",fsystem
                    
                    # remember the directories we make so we only make them once
                    created=[]
                    
                    for directory in sorted(fsystem.keys()):
                        # make directory
                        destpath = directory[len(src_path)+1:]              # the subpath part
                        #print "D:",dst,":",destpath,";",src_path
                        if dst+destpath not in created:
                            #print dst+destpath,"not in",created
                            try:
                                Mkdir(dst+destpath,yabiusername=yabiusername)
                            except BlockingException, be:
                                result_channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, str(be)) )    
                            except GETFailure, gf:
                                # ignore. directory probably already exists
                                pass
                            created.append(dst+destpath)
                             
                        for file,size,date in fsystem[directory]['files']:
                            if DEBUG:
                                print "COPY",file,size,date
                                print "EXTRA",">",destpath,">",directory
                            src_uri = src+destpath+file
                            dst_uri = dst+destpath+file
                            
                            if DEBUG:
                                print "Copy(",src_uri,",",dst_uri,")"
                            #print "Copy(",sbend+directory+"/"+file,",",dst+destpath+'/'+file,")"
                            Copy(src_uri,dst_uri,yabiusername=yabiusername)
                            Sleep(0.1)
                    
                    result_channel.callback(
                                                    http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Copied successfuly\n")
                                )
                except BlockingException, be:
                    result_channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, str(be)) )
                except GETFailure, gf:
                    if "503" in gf.message[1]:
                        result_channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, str(gf)) )
                    else:
                        result_channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, str(gf)) )
                except Exception, e:
                    result_channel.callback(
                                                    http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, str(e))
                                )
                    return

            copier = stackless.tasklet(rcopy_runner_thread)
            copier.setup()
            copier.run()
            
            return result_channel
            
            #return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK: %s\n"%res)
        
        deferred.addCallback(RCopyCommand)
        
        # save failed
        deferred.addErrback(lambda res: http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "NOT OK: %s\n"%str(res)) )
        
        return deferred
        
