
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json
from submit_helpers import parsePOSTData, parsePUTData, parsePOSTDataRemoteWriter
from twisted.web2.auth.interfaces import IAuthenticatedRequest, IHTTPUser

import globus

GET_DIR_LIST = True                     # whether when you call GET on a directory, if it returns the same as LIST on that path. False throws an error on a directory.
PIPE_RETRY_TIME = 1.0                   # how often in seconds to check for an initialised pipe has failed or started flowing
from globus.FifoStream import FifoStream

from twisted.web import client
import json

class GlobusFileResource(resource.PostableResource):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    addSlash = False
    
    def __init__(self,request=None,path=None,remotemethod="gsiftp",remoteserver="xe-ng2.ivec.org",remotepath="/", backend=None, authproxy=None):
        """Pass in the backends to be served out by this FSResource"""
        
        assert remotepath, "Remote path cannot be empty, must at least be '/'"
        assert remotepath[0]=='/', "Remote path must be absolute (and begin with a '/' character)"
        if remotepath[-1]!='/':
            remotepath+='/'
        
        # save the details of this connector
        self.remotemethod, self.remoteserver, self.remotepath, self.backend = remotemethod, remoteserver, remotepath, backend
        
        if path:
            # first part of path is yabi_username
            self.username = path.pop(0)
            
            # rest is the path of the remote file/directory
            self.path=path
        else:
            self.path = None
            
        if not authproxy:
            self.authproxy = globus.CertificateProxy()
        else:
            self.authproxy = authproxy
        
    def _make_remote_url(self):
        """return the full url for out path"""
        assert self.path, "Must only be called on a GlobusFileResource that has been constructed with a path"
        
        return "%s://%s%s"%(self.remotemethod, self.remoteserver, self.remotepath) + ("/".join(self.path))
        
    def render(self, request):
        # if path is none, we are at out pre '/' base resource (eg. GET /fs/file )
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Globus FS Connector Version: %s\n"%self.VERSION)
        
        if len(self.path) and not len(self.path[-1]):
            # path ends in a '/'. Do a directory listing
            return self.http_LIST(request)
        
        # auth our user
        # this may take a while, so we create a deferred for the response
        deferred = defer.Deferred()
        if not self.authproxy.IsProxyValid(self.username):
            # we have to auth the user. we need to get the credentials json object from the admin mango app
            self.AuthProxyUser(self.username, self.backend, self.RemoteFile,deferred)
        else:
            self.RemoteFile(deferred)
        
        return deferred
        
    def RemoteFile(self, result):
        """Actually tries to connect the remote file via the fifo to a http response and returns it. Asumes user is authed and ready
        
        result is the deferred to write our result into
        """
        usercert = self.authproxy.ProxyFile(self.username)
        
        # get our read fifo
        remote_url = self._make_remote_url()
        process, fifo = globus.Globus.ReadFromRemote(usercert,remote_url)
        #print "PROC",process,"FIFO",fifo
         
        # read out the stream
        fh = open(fifo)
        
        # we are gonna try and read the first character. This will open the stream and the remote process will die, if the remote file has an error.
        # doing this enables us to capture failure and return the right response code
        # we need to keep reading this buffer until one of two things happens
        # 1. we get a character, the stream is flowing, we return ok and begin the stream
        # 2. process.returncode gets a result. If its 0, there was a file and it was empty. If its non 0, an error occured.
        
        # our fifo stream object
        fifostream=FifoStream(fh)
        
        def begin_transfer_stream(deferred, stream):
            first_char=fh.read(1)
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
                        print "ERROR:",errortext
                        
                        if "No such file or directory" in errortext:
                            deferred.callback( http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, stream="Remote file not found: %s\n"%(remote_url)) )
                        else:
                            deferred.callback( http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream="Could not copy remote file:"+str(errortext)) )
        
        reactor.callLater(PIPE_RETRY_TIME, begin_transfer_stream, result, fifostream)
        
        # a deferred result
        return result
        
    def http_POST(self, request):
        """
        Respond to a POST request.
        Reads and parses the incoming body data then calls L{render}.
    
        @param request: the request to process.
        @return: an object adaptable to L{iweb.IResponse}.
        """
        if self.path == None:
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Globus FS Connector Version: %s\n"%self.VERSION)
        
        # auth our user
        # this may take a while, so we create a deferred for the response
        deferred = defer.Deferred()
        if not self.authproxy.IsProxyValid(self.username):
            # we have to auth the user. we need to get the credentials json object from the admin mango app
            self.AuthProxyUser(self.username,self.backend,self.UploadFile,deferred,request)
        else:
            self.UploadFile(deferred,request)
        
        return deferred
        
    def UploadFile(self, deferred, request):
        """handle the requests upload.
        
        deferred: where to write the result into. This is the connection back to the web service client
        """
        usercert = globus.Certificates.ProxyFile(self.username)
        remote_url = self._make_remote_url()
        
        # save the subprocesses in here so we can fetch return values
        process_list = []
        
        def GlobusRemoteFileWriter(filename):
            """Handles uploading of multiple globus files. This sets up the fifo and deferreds, and returns the open fifo handle"""
            url = remote_url
            if url.endswith('/'):
                url+=filename
            #print "FN:",filename,"REMOTE:",url    
            proc, fifo = globus.Globus.WriteToRemote(usercert,url)
            process_list.append((proc,fifo))
            
            return open(fifo, "wb")
        
        
        defferedchain = parsePOSTDataRemoteWriter(request,
            self.maxMem, self.maxFields, self.maxSize, writer=GlobusRemoteFileWriter
            )
        
        def PostUploadCheck(result):
            """Check that the upload worked. Check return codes from processes."""
            # we have to wait until we get result codes from these processes.
            def checkresults(result):
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
                        deferred.callback(http.Response( rcode, {'content-type': http_headers.MimeType('text', 'plain')}, errormessage) )
                    else:
                        #success
                        deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Files uploaded OK\n") )
            
            reactor.callLater(PIPE_RETRY_TIME, checkresults, result)
            
        
        # save worked.
        defferedchain.addCallback(PostUploadCheck)
        
        # save failed
        defferedchain.addErrback(lambda res: deferred.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, "File Upload Failed: %s\n"%res) ))
        
        return defferedchain

    def http_LIST(self,request):
        def list_success(deferred):
            usercert = self.authproxy.ProxyFile(self.username)
            
            try:
                contents = globus.Globus.ListRemote(usercert,self._make_remote_url())
                deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, json.dumps(contents)+"\n"))
            except globus.GlobusURLCopy.GlobusFTPError, error:
                deferred.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, str(error[1])+"\n"))
            
            return deferred
        
        # auth our user
        # this may take a while, so we create a deferred for the response
        deferred = defer.Deferred()
        if not self.authproxy.IsProxyValid(self.username):
            # we have to auth the user. we need to get the credentials json object from the admin mango app
            self.AuthProxyUser(self.username,self.backend, list_success,deferred)
        else:
            # auth our user
            list_success(deferred)
        
        return deferred
           
    def AuthProxyUser(self, username, backend, successcallback, deferred, *args):
        """Auth a user via getting the credentials from the json yabiadmin backend. When the credentials are gathered, successcallback is called with the deferred.
        The deferred should be the result channel your result will go back down"""
        host,port = "localhost",8000
        useragent = "YabiFS/0.1"
        
        factory = client.HTTPClientFactory(
            'http://%s:%d/yabiadmin/ws/credential/%s/%s/'%(host,port,username,backend),
            agent = useragent
            )
        reactor.connectTCP(host, port, factory)
        
        # now if the page fails for some reason. deal with it
        def _doFailure(data):
            print "Failed:",factory,":",type(data),data.__class__
            print data
            
            deferred.callback( http.Response( responsecode.UNAUTHORIZED, {'content-type': http_headers.MimeType('text', 'plain')}, "User: %s does not have credentials for this backend\n"%username) )
            
        # if we get the credentials decode them and auth them
        def _doSuccess(data):
            print "Success",deferred,args,successcallback
            credentials=json.loads(data)
            print "Credentials gathered successfully for user %s"%username
            
            # auth the user
            self.authproxy.CreateUserProxy(username,credentials['cert'],credentials['key'],credentials['password'])
            
            successcallback(deferred, *args)
        
        return factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)

    def locateChild(self, request, segments):
        # return our local file resource for these segments
        #print "LFR::LC",request,segments
        return GlobusFileResource(request,segments, remotemethod=self.remotemethod, remoteserver=self.remoteserver, remotepath=self.remotepath, backend=self.backend, authproxy=self.authproxy), []
 