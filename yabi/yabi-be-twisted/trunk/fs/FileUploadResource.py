# -*- coding: utf-8 -*-
from twisted.web2 import resource, http_headers, responsecode, http, server, fileupload
from twisted.internet import defer, reactor

import weakref
import sys, os, errno, time
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

# ticket store, the keys are th uuids, the values are hashes. The hashes have all the info you need in them for the upload
ticket_store = {}   

# ticket store expiry. keys are timestamps. values are uuids to expire after that timestamp.
ticket_store_expiry = {}

# list of uploads commenced. key = uuid. value = bytes transfered
uploads_progress = {}

# expiry window
EXPIRE_UPLOAD_TICKET_TIME = 60.0

def purge_expired_tickets():
    now = time.time()
    for t in [X for X in ticket_store_expiry.keys() if X < now]:
        for uuid in ticket_store_expiry[t]:
            if uuid in ticket_store:
                print "PURGING",uuid
                del ticket_store[uuid]
            else:
                print "purge ticket not found:",uuid
        
        # delete this expiry info
        del ticket_store_id[t]
        
class UploadStatus(resource.Resource):
    """This is where the admin reports the ticket id that its set for a pending upload"""
    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileListResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
    def render(self, request):
        # break our request path into parts
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, json.dumps({"ticket_store":ticket_store,"ticket_store_expiry":ticket_store_expiry,"uploads_progress":uploads_progress}))   

class UploadTicket(resource.Resource):
    """This is where the admin reports the ticket id that its set for a pending upload"""
    def __init__(self,request=None, path=None, fsresource=None):
        """Pass in the backends to be served out by this FSResource"""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileListResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
    def render(self, request):
        # break our request path into parts
        if "uri" not in request.args:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "No uri provided in GET parameters\n")

        uri = request.args['uri'][0] if 'uri' in request.args else None             # None means we need to look in the mime 
        yabiusername = request.args['yabiusername'][0] if 'yabiusername' in request.args else None
        uuid = request.args['uuid'][0]
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
        
        # save this ticket in ticket_store
        ticket_store[uuid] = {
            'creds' :           creds,
            'yabiusername'  :   yabiusername,
            'uri' :             uri
                             }
        
        # save an expiry time for this uuid upload
        expirytime = time.time() + EXPIRE_UPLOAD_TICKET_TIME
        
        if expirytime not in ticket_store_expiry:
            ticket_store_expiry[ expirytime ] = []
        ticket_store_expiry[ expirytime ].append(uuid)
        
        # done. return a json encoded upload url
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, '"http://urltouploadto/upload/%s"\n'%(uuid) )

class FileUploadResource(resource.PostableResource):
    VERSION=0.1
    maxMem = 100*1024
    maxFields = 16
    maxSize = 10*1024*102
    
    def __init__(self,request=None, path=None, fsresource=None, uuid=None):
        """If a uuid is passed in, we are an upload resource for a particular upload. Otherwise we are the parent."""
        self.path = path
        
        if not fsresource:
            raise Exception, "FileListResource must be informed on construction as to which FSResource is its parent"
        
        self.fsresource = weakref.ref(fsresource)
        
        if uuid:
            print "UPLOAD incoming for UUID:",uuid
        self.uuid = uuid
        
    def render(self, request):
        # break our request path into parts
        return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "request must be POST\n")
                        
    def http_POST(self, request):
        #print "FilePutResource::http_POST(",request,")"
        if not self.uuid:
            # we should not be POSTing to this url.
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Invalid POST URI\n")
        
        if self.uuid not in ticket_store:
            return http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "Invalid POST hash\n")
        
        # fetch details from cache
        details = ticket_store[self.uuid]
        uri = details['uri']
        yabiusername = details['yabiusername']
        creds = details['creds']
        
        # ok. now we have details, purge this entry from the store
        del ticket_store[self.uuid]
        
        # add us to the presently uploading list
        uploads_progress[self.uuid] = 0
        
        # now while we are at it, purge any entries that have expired
        purge_expired_tickets()
         
        scheme, address = parse_url(uri)
        
        if not hasattr(address,"username") or address.username==None:
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
                        self.procproto, fifo = bend.GetWriteFifo(hostname,username,path,filename, yabiusername=yabiusername,creds=creds)
                        
                        # give the engine a chance to fire up the process
                        stackless.schedule()
                        
                        while not self.procproto.isStarted():
                            print "."
                            stackless.schedule()
                    
                        # once its started wait one engine cycle before opening fifo.
                        for i in range(100):
                            stackless.schedule()
                        
                        print "Pre OPEN"
                        
                        while True:
                            try:
                                print "done?",self.procproto.isDone()
                                print "failed?",self.procproto.isFailed()
                                if self.procproto.isFailed():
                                    #channel.callback(http.HTTPError(http.StatusResponse(responsecode.SERVER_ERROR,"Write FIFO process failed! %s"%(self.procproto.err))))
                                    raise IOError, "Write FIFO process failed! %s"%(self.procproto.err)
                                #self.fileopen = os.fdopen(os.open(fifo,os.O_NONBLOCK|os.O_WRONLY),"wb")
                                self.fileopen=open(fifo,'wb')
                                print "fileopen:",self.fileopen
                                break
                            except (OSError, IOError), e:
                                print "!!!"
                                if e.errno == errno.EINTR or e.errno == errno.EAGAIN:
                                    print "sched"
                                    stackless.schedule()
                                else:
                                    raise
                        
                        print "Post OPEN"
                        
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
                        
                        # save how many bytes we've written into internal store so status page can be kept
                        uploads_progress[self.uuid] = parser.bytes_written
                        
                        stackless.schedule()
                except IOError, ioe:
                    #print "IOError!!!",ioe
                    # sleep until the task finished
                    while not parser.procproto.isDone():
                        stackless.schedule()
                    del uploads_progress[self.uuid]
                    return channel.callback(http.Response( responsecode.BAD_REQUEST, {'content-type': http_headers.MimeType('text', 'plain')}, "File upload failed: %s\n"%parser.procproto.err))
                except Exception, ex:
                    import traceback
                    del uploads_progress[self.uuid]
                    channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "File upload failed: %s\n"%(traceback.format_exc())))
                    #TODO: why does the client channel stay open here? How do we close it after returning this error message? We are inside a stackless threadlet. Is that why?
                    raise

                del uploads_progress[self.uuid]
                return channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "OK\n"))
            else:
                del uploads_progress[self.uuid]
                return channel.callback(http.Response( responsecode.BAD_REQUEST, "Invalid content-type: %s/%s" % (ctype.mediaType, ctype.mediaSubtype)))
            
        
        tasklet = stackless.tasklet(upload_tasklet)
        tasklet.setup( request, client_channel )
        tasklet.run()
        
        return client_channel
        
    def locateChild(self, request, segments):
        # return our local file resource for these segments
        return FileUploadResource(request,segments,fsresource = self,uuid=segments[0]), []
        
