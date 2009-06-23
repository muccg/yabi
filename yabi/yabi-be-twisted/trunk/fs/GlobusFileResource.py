
from twisted.web2 import resource, http_headers, responsecode, http, server, stream
from twisted.internet import defer, reactor
from os.path import sep
import os, json, sys
from submit_helpers import parsePOSTData, parsePUTData, parsePOSTDataRemoteWriter
from twisted.web2.auth.interfaces import IAuthenticatedRequest, IHTTPUser

import globus

GET_DIR_LIST = True                     # whether when you call GET on a directory, if it returns the same as LIST on that path. False throws an error on a directory.
PIPE_RETRY_TIME = 1.0                   # how often in seconds to check for an initialised pipe has failed or started flowing
BUFFER_SIZE = 8192                      # the read() buffer size. Must be less than the socket buffer size
from globus.FifoStream import FifoStream

from twisted.web import client
import json

import subprocess

from BaseFileResource import BaseFileResource

def parse_ls_generate_items(lines):
    for line in lines:
        parts=line.split(None,8)
        if len(parts)==1:
            # header
            assert parts[0][-1]==":"
            yield (parts[0][:-1],)
        elif len(parts)==2:
            assert parts[0]=="total"
        elif len(parts)==9:
            #body
            filename, filesize, date = (parts[8], int(parts[4]), "%s %s %s"%tuple(parts[5:8]))
            if filename[-1] in "*@|":
                # filename ends in a "*@|"
                yield (filename[:-1], filesize, date)
            else:
                yield (filename, filesize, date)
        else:
            pass                #ignore line

def parse_ls_directories(data):
    """Parse the output from ls -al function into yabi directory listings"""
    filelisting = None
    dirlisting = None
    presentdir = None
    for line in parse_ls_generate_items(data.split("\n")):
        if len(line)==1:
            if presentdir:
                assert filelisting!=None
                assert dirlisting!=None
                # break off this directory.
                yield presentdir,filelisting,dirlisting
            presentdir=line[0]
            filelisting=[]                  # space to store listing
            dirlisting=[]
        else:
            assert len(line)==3
            if filelisting==None and dirlisting==None:
                # we are probably a non recursive listing. Set us up for a single dir
                assert presentdir==None
                filelisting, dirlisting = [], []

            if line[0][-1]=="/":
                dirlisting.append((line[0][:-1],line[1],line[2]))                #line[0][:-1] removes the trailing /
            else:
                filelisting.append(line)
    
    # send the last one
    if None not in [filelisting,dirlisting]:
        yield presentdir, filelisting, dirlisting
            
def parse_ls(data):
    output = {}
    for name,filelisting,dirlisting in parse_ls_directories(data):
        output[name] = {
            "files":filelisting,
            "directories":dirlisting
        }
    return output



class GlobusFileResource(BaseFileResource):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="Globus File System"
    addSlash = False
    
    def __init__(self,request=None,path=None,remotemethod="gsiftp",remoteserver="xe-ng2.ivec.org",remotepath="/", backend=None, authproxy=None):
        """Pass in the backends to be served out by this FSResource"""
        
        BaseFileResource.__init__(self,request,path)
        
        assert remotepath, "Remote path cannot be empty, must at least be '/'"
        assert remotepath[0]=='/', "Remote path must be absolute (and begin with a '/' character)"
        if remotepath[-1]!='/':
            remotepath+='/'
        
        self.username=None
        
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
            
    def http_LIST_old(self,request):
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
           
    def http_LIST(self, request, recurse=False, path=None, username=None):
        # 1. auth our user. when they are authed, do the followng...
        path = path or self.path
        username = username or self.username
        
        def _is_authed(deferred):
            # fire up the ls process.
            usercert = self.authproxy.ProxyFile(username)
            directory = os.path.join(self.remotepath,"/".join(path[1:]))           # path[0] is the username
            proc = globus.Shell.ls(usercert,self.remoteserver,directory, args="-alFR" if recurse else "-alF" )
            
            data_result = []
            
            # now we just read the output until process is finished
            def _ls_read():
                print "_ls_read"
                
                data = proc.stdout.read(BUFFER_SIZE)
                
                if len(data):
                    print "read",len(data),"bytes"
                    
                    data_result.append(data)
                    
                # if the process has not ended...
                if proc.poll()==None:
                    # reschedule us
                    reactor.callLater(0.0 if len(data) else 0.2,_ls_read)                   # back off if we got no data
                else:
                    print "PROC ENDED",proc.poll
                    data_result.append(proc.stdout.read())
                
                    #print "RESULT",data_result
                    
                    # decode the ls data
                    ls_data = parse_ls("".join(data_result))
                    
                    # are we non recursive?
                    if not recurse:
                        # "None" path header is actually our path
                        ls_data[directory]=ls_data[None]
                        del ls_data[None]
                        
                    print "".join(data_result)
                        
                    # now we need to munge the path locations to be url descendents, not remote fs descendants
                    remote_mount_parts = self.remotepath.split("/")
                    assert remote_mount_parts[0]=="" and remote_mount_parts[-1]==""
                    remote_mount_parts=remote_mount_parts[1:-1]
                    #print remote_mount_parts
                    request_parts = path
                    
                    if request_parts[0]=="":
                        request_parts=request_parts[1:]
                    if request_parts[-1]=="":
                        request_parts=request_parts[:-1]
                     
                    #print request_parts
                    def munge_filename(remotepath):
                        remote_parts = remotepath.split("/")
                        assert remote_parts[0]==""
                        # make sure we end in '' (recursive listings dont have trailing /)
                        if len(remote_parts[-1]):
                            remote_parts=remote_parts[1:]
                        else:
                           remote_parts=remote_parts[1:-1]
                        #print remote_parts
                        
                        # remove mount prefix
                        removedprefix, remote_parts = remote_parts[:len(remote_mount_parts)],remote_parts[len(remote_mount_parts):]
                        #print removedprefix, remote_parts
                        assert removedprefix == remote_mount_parts
                        
                        # prepend with the first parts of request_parts
                        assert path[-1]=="", "path does not end in '/'"
                        username_part,path_parts_sans_username = path[:1],path[1:-1]
                        if not len(path_parts_sans_username):
                            # asking relatively for "/" under be/username/
                            prefix_parts = request_parts
                        else:
                            prefix_parts, culled = request_parts[:-len(path_parts_sans_username)],request_parts[-len(path_parts_sans_username):]
                            print culled, path_parts_sans_username
                            assert culled==path_parts_sans_username
                        
                        #print prefix_parts
                        
                        final_path = [''] + prefix_parts + remote_parts + ['']
                        
                        return "/".join(final_path)
                        
                        
                    processed_data = {}
                    try:
                        for key in ls_data:
                            munged_filename = munge_filename(key)
                            processed_data[munged_filename] = ls_data[key]
                    except AssertionError, ae:
                        deferred.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, str(ae)))
                    
                    deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, json.dumps(processed_data)))
                    
            reactor.callLater(0,_ls_read)
            
            
        # 1. auth our user
        deferred = defer.Deferred()
        if not self.authproxy.IsProxyValid(username):
            # we have to auth the user. we need to get the credentials json object from the admin mango app
            self.AuthProxyUser(username,self.backend, _is_authed,deferred)
        else:
            # our user is valid
            _is_authed(deferred)
        return deferred
           
    def http_MKDIR(self, request, path=None, username=None):
        """mkdir command. Uses self.path. If path is passed in (not None), then it overrides the request.path, and we go make this path instead.
        remember path must be a list.
        """
        
        path = path or self.path
        username = username or self.username
            
        
        # 1. auth our user. when they are authed, do the followng...
        def _is_authed(deferred):
            # fire up the ls process.
            usercert = self.authproxy.ProxyFile(username)
            directory = os.path.join(self.remotepath,"/".join(path[1:]))           # path[0] is the username
            proc = globus.Shell.mkdir(usercert,self.remoteserver,directory)
            
            data_result = []
            
            # now we just read the output until process is finished
            def _mkdir_read():
                print "_mkdir_read"
                
                data = proc.stdout.read(BUFFER_SIZE)
                
                if len(data):
                    print "read",len(data),"bytes"
                    
                    data_result.append(data)
                    
                # if the process has not ended...
                if proc.poll()==None:
                    # reschedule us
                    reactor.callLater(0.0 if len(data) else 0.2,_mkdir_read)                   # back off if we got no data
                else:
                    returncode = proc.poll()
                    data_result.append(proc.stdout.read())              # read the last bit of data
                
                    print "RC:",returncode
                
                    if returncode:
                        # failure
                        mkdir_data = "".join(data_result)
                        deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, mkdir_data))
                    else:
                        deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Directory created successfuly\n"))
                    
            reactor.callLater(0,_mkdir_read)
            
            
        # 1. auth our user
        deferred = defer.Deferred()
        if not self.authproxy.IsProxyValid(username):
            # we have to auth the user. we need to get the credentials json object from the admin mango app
            self.AuthProxyUser(username,self.backend, _is_authed,deferred)
        else:
            # our user is valid
            _is_authed(deferred)
        return deferred

    def http_DELETE(self, request, recurse=True, path=None, username=None):
        """If path is passed in, remove this remote path instead of self.path (like MKDIR)"""
        path = path or self.path
        username = username or self.username
        
        # 1. auth our user. when they are authed, do the followng...
        def _is_authed(deferred):
            # fire up the ls process.
            usercert = self.authproxy.ProxyFile(username)
            directory = os.path.join(self.remotepath,"/".join(path[1:]))           # path[0] is the username
            proc = globus.Shell.rm(usercert,self.remoteserver,directory, args="-r" if recurse else "")
            
            data_result = []
            
            # now we just read the output until process is finished
            def _rm_read():
                print "_rm_read"
                
                data = proc.stdout.read(BUFFER_SIZE)
                
                if len(data):
                    print "read",len(data),"bytes"
                    
                    data_result.append(data)
                    
                # if the process has not ended...
                if proc.poll()==None:
                    # reschedule us
                    reactor.callLater(0.0 if len(data) else 0.2,_rm_read)                   # back off if we got no data
                else:
                    returncode = proc.poll()
                    data_result.append(proc.stdout.read())              # read the last bit of data
                
                    if returncode:
                        # failure
                        mkdir_data = "".join(data_result)
                        deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, mkdir_data))
                    else:
                        deferred.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, "Delete successful\n"))
                    
            reactor.callLater(0,_rm_read)
            
            
        # 1. auth our user
        deferred = defer.Deferred()
        if not self.authproxy.IsProxyValid(username):
            # we have to auth the user. we need to get the credentials json object from the admin mango app
            self.AuthProxyUser(username,self.backend, _is_authed,deferred)
        else:
            # our user is valid
            _is_authed(deferred)
        return deferred
           
    # TODO: move the following into a mixin
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
 