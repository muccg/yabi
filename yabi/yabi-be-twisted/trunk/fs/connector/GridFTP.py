import FSConnector
import globus
import stackless
from utils.parsers import *
from fs.Exceptions import PermissionDenied, InvalidPath
from FifoPool import Fifos
from twisted.internet import protocol
from twisted.internet import reactor
import os

DEBUG = False

class GridFTP(FSConnector.FSConnector, globus.Auth):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="Globus File System"
    copymode = "gsiftp"
    
    def __init__(self):
        # we need to store a number of certificateproxies
        self.CreateAuthProxy()
    
    def _make_remote_url(self, server, remotepath, path=""):
        """return the full url for out path"""
        return "%s://%s%s"%(self.copymode,server,remotepath) + path
    
    def mkdir(self, host, username, path, **creds):
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(self.scheme,username,host)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
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
        
    def rm(self, host, username, path, recurse=False, creds):
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(self.scheme,username,host)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
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
    
    def ls(self, host, username, path, recurse=False, culldots=True, creds):
        # make sure we are authed
        if creds:
            print "handed creds:",creds
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            print "not handed creds"
            self.EnsureAuthed(self.scheme,username,host)
        
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        pp = globus.Shell.ls(usercert,host,path, args="-alFR" if recurse else "-alF" )
        
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
        
    def GetWriteFifo(self, host=None, username=None, path=None, filename=None, fifo=None, **creds):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        dst = os.path.join(self._make_remote_url(host,path),filename)
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(self.scheme,username,host)
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        pp, fifo = globus.Copy.WriteToRemote(usercert,dst,fifo=fifo)
        
        return pp, fifo
    
    def GetReadFifo(self, host=None, username=None, path=None, filename=None, fifo=None, **creds):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        dst = os.path.join(self._make_remote_url(host,path),filename)
        
        # make sure we are authed
        if creds:
            self.EnsureAuthedWithCredentials(host, **creds)
        else:
            self.EnsureAuthed(self.scheme,username,host)
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        pp, fifo = globus.Copy.ReadFromRemote(usercert,dst,fifo=fifo)
        
        return pp, fifo
       