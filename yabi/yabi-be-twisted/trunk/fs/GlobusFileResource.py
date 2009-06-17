
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

from BaseFileResource import BaseFileResource

class GlobusFileResource(BaseFileResource):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    addSlash = False
    
    def __init__(self,request=None,path=None,remotemethod="gsiftp",remoteserver="xe-ng2.ivec.org",remotepath="/", backend=None, authproxy=None):
        """Pass in the backends to be served out by this FSResource"""
        
        BaseFileResource.__init__(self,request,path)
        
        assert remotepath, "Remote path cannot be empty, must at least be '/'"
        assert remotepath[0]=='/', "Remote path must be absolute (and begin with a '/' character)"
        if remotepath[-1]!='/':
            remotepath+='/'
        
        # save the details of this connector
        self.remotemethod, self.remoteserver, self.remotepath, self.backend = remotemethod, remoteserver, remotepath, backend
        
        if path:
            # first part of path is yabi_username
            self.username = path[0]
            
            # together the whole thing is the path
            self.path=path
        else:
            self.path = None
            
        if not authproxy:
            self.authproxy = globus.CertificateProxy()
        else:
            self.authproxy = authproxy
        
    def _make_remote_url(self, path=None):
        """return the full url for out path"""
        if not path:
            path = self.path[1:]                    # remove the username prefix from the path
            
        return "%s://%s%s"%(self.remotemethod, self.remoteserver, self.remotepath) + ("/".join(path))
        
    def GetReadFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo is passed in, then use that as the fifo rather than creating one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        fifoin = fifo
        parts = path.split("/")
        username = parts[0]
        path = parts[1:]
        
        def success( callback, *args):
            """the user is now authed"""
            usercert = self.authproxy.ProxyFile(username)
            remote_url = self._make_remote_url(path)
            process, fifo = globus.Copy.ReadFromRemote(usercert,remote_url,fifo=fifoin)
            #print "process read",sys.getrefcount(process)

            # call the func with the process, fifo
            callback( process,fifo )
            
            return
        
        if not self.authproxy.IsProxyValid(username):
            self.AuthProxyUser(username, self.backend, success, deferred)
        else:
            success(deferred)
            
    def GetWriteFifo(self, path, deferred, fifo=None):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        fifoin = fifo
        parts = path.split("/")
        username = parts[0]
        path = parts[1:]
         
        def success( callback, *args):
            """the user is now authed"""
            usercert = self.authproxy.ProxyFile(username)
            remote_url = self._make_remote_url(path)
            process, fifo = globus.Copy.WriteToRemote(usercert,remote_url,fifo=fifoin)
            #print "process write",sys.getrefcount(process)
            
            # call the func with the process, fifo
            callback( process,fifo )
            
            return
        
        if not self.authproxy.IsProxyValid(username):
            self.AuthProxyUser(username, self.backend, success, deferred)
        else:
            success(deferred)
            
    def http_LIST(self,request):
        def list_success(deferred):
            usercert = self.authproxy.ProxyFile(self.username)
            
            try:
                contents = globus.Copy.ListRemote(usercert,self._make_remote_url())
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
 