# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http, server, fileupload
from twisted.internet import defer, reactor

import weakref
import sys, os, errno
import stackless
import json
from MimeStreamDecoder import MimeStreamDecoder, no_intr

from Exceptions import PermissionDenied, InvalidPath, NoCredentials, ProxyInitError

from utils.stacklesstools import WaitForDeferredData
from utils.parsers import parse_url

from twisted.internet.defer import Deferred

from utils.submit_helpers import parsePOSTData
import traceback

DEFAULT_PUT_PRIORITY = 1

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
        # override default priority
        priority = int(request.args['priority'][0]) if "priority" in request.args else DEFAULT_PUT_PRIORITY
        
        #print "FilePutResource::http_POST(",request,")"
        if "uri" not in request.args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No uri provided in GET parameters\n")

        uri = request.args['uri'][0] if 'uri' in request.args else None             # None means we need to look in the mime 
        yabiusername = request.args['yabiusername'][0] if 'yabiusername' in request.args else None
        scheme, address = parse_url(uri)
        
        # compile any credentials together to pass to backend
        creds={}
        for varname in ['key','password','username','cert']:
            if varname in request.args:
                creds[varname] = request.args[varname][0]
                del request.args[varname]
        
        if not (yabiusername or creds):
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in.\n")
        
        if not hasattr(address,"username") or address.username==None:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No username provided in uri\n")
        
        bendname = scheme
        username = address.username
        path = address.path
        hostname = address.hostname
        port = address.port
        
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
                
                #while True:
                    ##print "DATA:",WaitForDeferredData(reader)
                    #stackless.schedule()
                
                raise Exception, "Unallowed mediatype in POST upload file header"
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
                        print "Uploading file:",filename
                        self.procproto, fifo = bend.GetWriteFifo(hostname,username,path,port,filename, yabiusername=yabiusername,creds=creds, priority=priority)
                        
                        def fifo_cleanup(response):
                            os.unlink(fifo)
                            return response
                        channel.addCallback(fifo_cleanup)
                        
                        # give the engine a chance to fire up the process
                        stackless.schedule()
                        
                        while not self.procproto.isStarted():
                            print "."
                            stackless.schedule()
                    
                        # once its started wait one engine cycle before opening fifo.
                        for i in range(100):
                            stackless.schedule()
                        
                        while True:
                            try:
                                if self.procproto.isFailed():
                                    #channel.callback(http.HTTPError(http.StatusResponse(responsecode.SERVER_ERROR,"Write FIFO process failed! %s"%(self.procproto.err))))
                                    raise IOError, "Write FIFO process failed! %s"%(self.procproto.err)
                                #self.fileopen = os.fdopen(os.open(fifo,os.O_NONBLOCK|os.O_WRONLY),"wb")
                                self.fileopen=open(fifo,'wb')
                                break
                            except (OSError, IOError), e:
                                print traceback.format_exc()
                                if e.errno == errno.EINTR or e.errno == errno.EAGAIN:
                                    stackless.schedule()
                                else:
                                    raise
                        
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
                #print "READER",reader
                
                try:
                    while reader is not None:
                        dat = WaitForDeferredData(reader)
                        
                        # process data snippet
                        #print "SNIPPET",dat
                        parser.feed(dat)
                        
                        reader = req.stream.read()
                        stackless.schedule()
                except IOError, ioe:
                    #print "IOError!!!",ioe
                    # sleep until the task finished
                    print traceback.format_exc()
                    while not parser.procproto.isDone():
                        stackless.schedule()
                    return channel.callback(http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "File upload failed: %s\n"%parser.procproto.err))
                except Exception, ex:
                    print traceback.format_exc()
                    channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "File upload failed: %s\n"%(traceback.format_exc())))
                    #TODO: why does the client channel stay open here? How do we close it after returning this error message? We are inside a stackless threadlet. Is that why?
                    raise

                return channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK\n"))
            else:
                return channel.callback(http.Response( responsecode.BAD_REQUEST, "Invalid content-type: %s/%s" % (ctype.mediaType, ctype.mediaSubtype)))
            
        
        tasklet = stackless.tasklet(upload_tasklet)
        tasklet.setup( request, client_channel )
        tasklet.run()
        
        return client_channel
