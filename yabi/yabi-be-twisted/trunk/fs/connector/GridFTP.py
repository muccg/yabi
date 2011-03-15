# -*- coding: utf-8 -*-
import FSConnector
from utils.protocol import globus
import stackless
from utils.parsers import *
from Exceptions import PermissionDenied, InvalidPath
from FifoPool import Fifos
from twisted.internet import protocol
from twisted.internet import reactor
import os

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "gridftp"

DEBUG = False

class GridFTP(FSConnector.FSConnector, globus.Auth.GlobusAuth):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="Globus File System"
    copymode = "gsiftp"
    
    def __init__(self):
        FSConnector.FSConnector.__init__(self)
        globus.Auth.GlobusAuth.__init__(self)
        
        # we need to store a number of certificateproxies
        self.CreateAuthProxy()
    
    def lock(self,*args,**kwargs):
        return
        
    def unlock(self, tag):
        return
        
    def _make_remote_url(self, server, remotepath, path=""):
        """return the full url for out path"""
        return "%s://%s%s"%(self.copymode,server,remotepath) + path
    
    def mkdir(self, host, username, path, port=None, yabiusername=None, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername,SCHEMA,username,host,path)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = globus.Shell.mkdir(usercert,host,path)
        
        while not pp.isDone():
            stackless.schedule()
            
        err, mkdir_data = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
        
        if DEBUG:
            print "mkdir_data=",mkdir_data
            print "err", err
        
        return mkdir_data
        
    def rm(self, host, username, path, port=None, yabiusername=None, recurse=False, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername, SCHEMA,username,host,path)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = globus.Shell.rm(usercert,host,path,args="-r" if recurse else "")
        
        while not pp.isDone():
            stackless.schedule()
            
        err, rm_data = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
        
        if DEBUG:
            print "rm_data=",rm_data
            print "err", err
        
        return rm_data
    
    def ls(self, host, username, path, port=None, yabiusername=None, recurse=False, culldots=True, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "GridFTP::ls(",host,username,path,yabiusername,recurse,culldots,creds,")"
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername, SCHEMA,username,host,path)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = globus.Shell.ls(usercert,host,path, args="-lFR" if recurse else "-lF" )
        
        while not pp.isDone():
            stackless.schedule()
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
        
        ls_data = parse_ls(out, culldots=culldots)
        
        if DEBUG:
            print "ls_data=",ls_data
            print "out", out
            print "err", err
        
        # are we non recursive?
        if not recurse:
            # "None" path header is actually our path
            ls_data[path]=ls_data[None]
            del ls_data[None]
                        
        return ls_data

    def ln(self, host, username, target, link, port=None, yabiusername=None, recurse=False, culldots=True, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "GridFTP::ln(",host,username,target,link,yabiusername,recurse,culldots,creds,")"
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername, SCHEMA,username,host,target)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = globus.Shell.ln(usercert,host,target,link)
        
        while not pp.isDone():
            stackless.schedule()
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
       
        if DEBUG:
            print "ln_out", out
            print "ln_err", err
        
        return out

    def cp(self, host, username, src, dst, port=None, yabiusername=None, recurse=False, culldots=True, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "GridFTP::cp(",host,username,src,dst,yabiusername,recurse,culldots,creds,")"
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername, SCHEMA,username,host,src)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = globus.Shell.ln(usercert,host,src,dst)
        
        while not pp.isDone():
            stackless.schedule()
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
       
        if DEBUG:
            print "cp_out", out
            print "cp_err", err
        
        return out
        
    def GetWriteFifo(self, host=None, username=None, path=None, port=None, filename=None, fifo=None, yabiusername=None, creds={}, priority=0):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "GridFTP::GetWriteFifo( host:"+host,",username:",username,",path:",path,",filename:",filename,",fifo:",fifo,",yabiusername:",yabiusername,",creds:",creds,")"
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        dst = os.path.join(self._make_remote_url(host,path),filename)
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername, SCHEMA,username,host, path)
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        pp, fifo = globus.Copy.WriteToRemote(usercert,dst,fifo=fifo)
        
        return pp, fifo
    
    def GetReadFifo(self, host=None, username=None, path=None, port=None, filename=None, fifo=None, yabiusername=None, creds={}, priority=0):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        dst = os.path.join(self._make_remote_url(host,path),filename)
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(yabiusername,SCHEMA,username,host, path)
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        pp, fifo = globus.Copy.ReadFromRemote(usercert,dst,fifo=fifo)
        
        return pp, fifo
       
