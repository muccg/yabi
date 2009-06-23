
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json, sys
from submit_helpers import parsePOSTData, parsePUTData, parsePOSTDataRemoteWriter
from twisted.web2.auth.interfaces import IAuthenticatedRequest, IHTTPUser

import globus

GET_DIR_LIST = True                     # whether when you call GET on a directory, if it returns the same as LIST on that path. False throws an error on a directory.
PIPE_RETRY_TIME = 1.0                   # how often in seconds to check for an initialised pipe has failed or started flowing
from globus.FifoStream import FifoStream

from twisted.web import client
import json

import subprocess

class BaseFileResource(resource.PostableResource):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="Base File Resource"
    addSlash = False
    
    def __init__(self,request=None,path=None):
        self.request, self.path = request,path
                
    def GetReadFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo is passed in, then use that as the fifo rather than creating one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        assert False, "GetReadFifo() needs to be overridden in the base class"
            
    def GetWriteFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        assert False, "GetWriteFifo() needs to be overridden in the base class"
        
    def NonFatalRetryGenerator(self):
        """This returns a generator that generates the retry delays for a non fatal error. Here you can tailor the retry
        timeouts for this particular backend. To make it retry forever, make an infinite generator. When the generator 
        finally exits, the error is raised. The default is an exponential backoff
        """
        NUM_RETRIES = 5                     # number of retries
        delay = 5.0                         # first delay
        for i in range(NUM_RETRIES):
            yield delay
            delay*=2.                       # double each time
            
    # In order to identify a non fatal copy failure, we search for each of these phrases in stdout/stderr of the copy classes.
    # comparison is case insensitive
    NonFatalKeywords = [ "connection refused", "connection reset by peer" ]                 # "broken pipe"?
    
    def render(self, request):
        # if path is none, we are at out pre '/' base resource (eg. GET /fs/file )
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "%s Version: %s\n"%(self.NAME,self.VERSION))
        
        if len(self.path) and not len(self.path[-1]):
            # path ends in a '/'. Do a directory listing
            return self.http_LIST(request)
        
        # our result will take a while. trigger this deferred when you are ready for the client
        client_channel = defer.Deferred()
        
        # get our read fifo. when its ready, the callback will be just to stream this out the connection
        def callback( process, fifo ):
            #print "render ready callback",process,fifo
        
            # just a quick check to see if the process has died. In the example of /bin/cp, the output fifo will NEVER be opened,
            # because the process is already dead. If the process is already dead, we're cactus, and we should report this death.
            if process.poll():
                # error code! Lets die
                client_channel.callback( http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream="Could not copy file: \n%s\n\n%s\n"%(sep.join(self.path),process.stdout.read())) )
                return
            
            # also a possibility is that the process will die VERY SOON. because it hasn't opened to write to the fifo, the open to read will block forever
            # and we will block, the process will die, we will never notice it, and that is that! SO as such, we need to open the file with
            # O_NONBLOCK...
             
            # read out the stream
            fh = os.fdopen( os.open( fifo, os.O_RDONLY | os.O_NONBLOCK) )
            print "fh",fh
            
            # OLD DEPRECATED no_intr call
            #fh = subprocess.no_intr(open,fifo,"rb")
            
            # we are gonna try and read the first character. This will open the stream and the remote process will die, if the remote file has an error.
            # doing this enables us to capture failure and return the right response code
            # we need to keep reading this buffer until one of two things happens
            # 1. we get a character, the stream is flowing, we return ok and begin the stream
            # 2. process.returncode gets a result. If its 0, there was a file and it was empty. If its non 0, an error occured.
            
            # our fifo stream object
            fifostream=FifoStream(fh)
            #print "fifo",fifostream
            
            def begin_transfer_stream(deferred, stream):
                #print "b_t_s",fh
                
                try:
                    first_char=fh.read(1)
                except IOError, e:
                    if e.errno==11:
                        # resource temporarily unavailable. write process has not begun!
                        reactor.callLater(PIPE_RETRY_TIME,begin_transfer_stream, deferred, stream)
                        return deferred
                    else:
                        raise
                    
                if len(first_char):
                    # stream flowing! lets connect and return
                    stream.prepush(first_char)                      # push this data back into the head of the stream
                    deferred.callback( http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=stream) )
                else:
                    # stream not flowing. Do we have a result code
                    process.poll()
                    #print "return code",process.returncode
                    if process.returncode==None:
                        # still running.
                        reactor.callLater(PIPE_RETRY_TIME,begin_transfer_stream, deferred, stream)
                        return deferred
                    else:
                        # theres a return code
                        if process.returncode==0:
                            # success. empty stream!
                            deferred.callback( http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=stream) )
                        else:
                            # error. capture it
                            errortext = process.stdout.read()
                            #print "ERROR:",errortext
                            
                            if "No such file or directory" in errortext:
                                deferred.callback( http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, stream="Remote file not found: %s\n"%(sep.join(self.path))) )
                            else:
                                deferred.callback( http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream="Could not copy remote file:"+str(errortext)) )
            
            reactor.callLater(0.1, begin_transfer_stream, client_channel, fifostream)
        
        # begin the readfifo openning process
        self.GetReadFifo( sep.join(self.path), callback )
        
        return client_channel
        
        
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Globus FS Connector Version: %s\n"%self.VERSION)
        
        # for our final result
        client_channel = defer.Deferred()
        
        # the list of processes, so we can check our result codes
        process_list=[]
        
        # we need a "writer" object, that will be instantiated and written to, for each file object uploaded.
        def RemoteFileWriter(filename):
            """Handles uploading of multiple files. This sets up the fifo and deferreds, and returns the open fifo handle"""
            path = self.path[:]
            if not path[-1]:               # path ends with '/'
                path[-1] = filename
                
            d = defer.Deferred()
            def cb( proc, fifo ):
                #def _call():
                    #print "CALLBACK",proc,fifo
                    ##print proc.stdout.read()
                    ##d.callback( open(fifo, "wb") )
                    #try:
                        #print "NEW OPEN"
                        #print os.path.exists(fifo)
                        #d.callback( os.fdopen(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK), "w") )
                    #except OSError, ose:
                        #if ose.errno==22 or ose.errno==11:
                            ## cant open write nonblock to fifo!
                            #raise
                            #print "OLD SCHOOL OPEN"
                            #d.callback( open(fifo, "wb") )
                        #else:
                            #raise
                    #print "DONE"
                    ##
                #reactor.callLater(3.0,_call)
                def _call():
                    print "cb",proc,fifo
                    #d.callback(open(fifo, "wb") )
                    d.callback( os.fdopen(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK), "w") )
                reactor.callLater(1.0,_call)
            
            print "Calling GetWriteFifo",sep.join(path), cb
            self.GetWriteFifo( sep.join(path), cb )
            
            print "RETURNING:",d
            
            return d
        
        defferedchain = parsePOSTDataRemoteWriter(request,
        self.maxMem, self.maxFields, self.maxSize, writer=RemoteFileWriter
        )
        
        def PostUploadCheck(result):
            """Check that the upload worked. Check return codes from processes."""
            # we have to wait until we get result codes from these processes.
            def checkresults(result):
                print "_cr"
                results = [proc.poll() for proc,fifo in process_list]
                if None in results:
                    reactor.callLater(PIPE_RETRY_TIME, checkresults, result)
                else:
                    # tasks finished
                    if any([X!=0 for X in results]):
                        #error. lets see if we can work out what went wrong
                        errormessage="File Upload%s Failed:\n\n"%('s' if len(results)>1 else '')
                        
                        rcode = responsecode.INTERNAL_SERVER_ERROR
                        for num, (proc, fifo) in enumerate(process_list):
                            message = proc.stdout.read()
                            
                            msg=''
                            if "Permission denied" in message:
                                msg="Permission Denied"
                                rcode = responsecode.UNAUTHORIZED
                            
                            errormessage+="upload %d: %s\n"%(num,msg)
                            errormessage+=message
                            errormessage+="\n\n\n"
                        
                        print "File upload to %s failed... %s"%(remote_url,errormessage)
                        client_channel.callback(http.Response( rcode, {'content-type': http_headers.MimeType('text', 'plain')}, errormessage) )
                    else:
                        #success
                        client_channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Files uploaded OK\n") )
            
            reactor.callLater(PIPE_RETRY_TIME, checkresults, result)
            
        
        # save worked.
        defferedchain.addCallback(PostUploadCheck)
        
        # save failed
        defferedchain.addErrback(lambda res: client_channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "File Upload Failed: %s\n"%res) ))
    
        return client_channel

    def http_LIST(self,request):
        assert False, "http_LIST needs to be overridden in subclass"

    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return BaseFileResource(request,segments), []
 