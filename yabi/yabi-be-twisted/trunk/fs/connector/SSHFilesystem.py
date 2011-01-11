# -*- coding: utf-8 -*-
import FSConnector
import stackless
from utils.parsers import *
from Exceptions import PermissionDenied, InvalidPath
from FifoPool import Fifos
from twisted.internet import protocol
from twisted.internet import reactor
import os
from utils.protocol import ssh

from conf import config

sshauth = ssh.SSHAuth.SSHAuth()

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "scp"

DEBUG = False

MAX_SSH_CONNECTIONS = 128
SSH_CONNECTION_COUNT = 0

def pre_ssh(self):
    while SSH_CONNECTION_COUNT >= MAX_SSH_CONNECTIONS:
        print "WARNING: max SSH connection count reached"
        stackless.schedule()
        
    SSH_CONNECTION_COUNT+=1
    
def post_ssh(self):
    SSH_CONNECTION_COUNT-=1
    
def lock(f):
    def new_func(*args, **kwargs):
        pre_ssh()
        try:
            return f(*args, **kwargs)
        finally:
            post_ssh()
    return new_func

class SSHFilesystem(FSConnector.FSConnector, ssh.KeyStore.KeyStore, object):
    """This is the resource that connects to the ssh backends"""
    VERSION=0.1
    NAME="SSH Filesystem"
    copymode = "ssh"
    
    def __init__(self):
        FSConnector.FSConnector.__init__(self)
        
        # make a path to store keys in
        configdir = config.config['backend']['certificates']
        ssh.KeyStore.KeyStore.__init__(self, dir=configdir)
    
    @lock
    def mkdir(self, host, username, path, yabiusername=None, creds={}):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # If we don't have creds, get them
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        usercert = self.save_identity(creds['key'])                         #, tag=(yabiusername,username,host,path)
        
        # we need to munge the path for transport over ssh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = ssh.Shell.mkdir(usercert,host,path, username=creds['username'], password=creds['password'])
        
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
        
    @lock
    def rm(self, host, username, path, yabiusername=None, recurse=False, creds={}):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # If we don't have creds, get them
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        usercert = self.save_identity(creds['key'])
        
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = ssh.Shell.rm(usercert,host,path,args="-r" if recurse else "", username=creds['username'], password=creds['password'])
        
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
    
    @lock
    def ls(self, host, username, path, yabiusername=None, recurse=False, culldots=True, creds={}):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "SSHFilesystem::ls(",host,username,path,yabiusername,recurse,culldots,creds,")"
        
        # If we don't have creds, get them
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        usercert = self.save_identity(creds['key'])
        
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = ssh.Shell.ls(usercert,host,path, args="-lFR" if recurse else "-lF", username=creds['username'], password=creds['password'] )
        
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
                        
        os.unlink(usercert)
                        
        return ls_data
        
    @lock
    def GetWriteFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a write fifo from a remote path as a certain user.
        
        pass in here the username, path
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "SSHFilesystem::GetWriteFifo( host:"+host,",username:",username,",path:",path,",filename:",filename,",fifo:",fifo,",yabiusername:",yabiusername,",creds:",creds,")"
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        dst = "%s@%s:%s"%(username,host,os.path.join(path,filename))
        
        # make sure we are authed
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        usercert = self.save_identity(creds['key'])
        
        pp, fifo = ssh.Copy.WriteToRemote(usercert,dst,password=creds['password'],fifo=fifo)
        
        return pp, fifo
    
    @lock
    def GetReadFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "SSH::GetReadFifo(",host,username,path,filename,fifo,yabiusername,creds,")"
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        dst = "%s@%s:%s"%(username,host,os.path.join(path,filename))
        
        self.lock()
        
        # make sure we are authed
        if not creds:
            #print "get creds"
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        usercert = self.save_identity(creds['key'])
        
        #print "read from remote"
        pp, fifo = ssh.Copy.ReadFromRemote(usercert,dst,password=creds['password'],fifo=fifo)
        #print "read from remote returned"
        
        return pp, fifo
       
