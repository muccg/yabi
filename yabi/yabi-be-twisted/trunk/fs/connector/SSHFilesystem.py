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

MAX_SSH_CONNECTIONS = 0                                     # zero is unlimited
    
from decorators import retry, call_count
from LockQueue import LockQueue

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
        
        #instantiate a lock queue for this backend.
        self.lockqueue = LockQueue( MAX_SSH_CONNECTIONS )
        
    def lock(self,*args,**kwargs):
        return self.lockqueue.lock(*args, **kwargs)
        
    def unlock(self, tag):
        return self.lockqueue.unlock(tag)
        
    #@lock
    @retry(5,(InvalidPath,PermissionDenied))
    @call_count
    def mkdir(self, host, username, path, yabiusername=None, creds={},priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        
        # If we don't have creds, get them
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        usercert = self.save_identity(creds['key'])                         #, tag=(yabiusername,username,host,path)
        
        # we need to munge the path for transport over ssh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = ssh.Shell.mkdir(usercert,host,path, username=creds['username'], password=creds['password'])
        
        while not pp.isDone():
            stackless.schedule()
            
        if priority:
            self.lockqueue.unlock(lock)
            
        err, mkdir_data = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in out:
                raise InvalidPath("No such file or directory\n")
            else:
                print "SSH failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
        if DEBUG:
            print "mkdir_data=",mkdir_data
            print "err", err
        
        return mkdir_data
        
    #@lock
    @retry(5,(InvalidPath,PermissionDenied))
    @call_count
    def rm(self, host, username, path, yabiusername=None, recurse=False, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        
        # If we don't have creds, get them
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        usercert = self.save_identity(creds['key'])
        
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = ssh.Shell.rm(usercert,host,path,args="-r" if recurse else "", username=creds['username'], password=creds['password'])
        
        while not pp.isDone():
            stackless.schedule()
        
        if priority:
            self.lockqueue.unlock(lock)
            
        err, rm_data = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in out:
                raise InvalidPath("No such file or directory\n")
            else:
                print "SSH failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
        if DEBUG:
            print "rm_data=",rm_data
            print "err", err
        
        return rm_data
    
    #@lock
    @retry(5,(InvalidPath,PermissionDenied))
    @call_count
    def ls(self, host, username, path, yabiusername=None, recurse=False, culldots=True, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "SSHFilesystem::ls(",host,username,path,yabiusername,recurse,culldots,creds,priority,")"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        
        # If we don't have creds, get them
        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        usercert = self.save_identity(creds['key'])
        
        # we need to munge the path for transport over gsissh (cause it sucks)
        #mungedpath = '"' + path.replace('"',r'\"') + '"'
        pp = ssh.Shell.ls(usercert,host,path, args="-lFR" if recurse else "-lF", username=creds['username'], password=creds['password'] )
        
        while not pp.isDone():
            stackless.schedule()
            
        # release our queue lock
        if priority:
            self.lockqueue.unlock(lock)
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in out:
                raise InvalidPath("No such file or directory\n")
            else:
                print "SSH failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
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
        
    #@lock
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
    
    #@lock
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
        
        # make sure we are authed
        if not creds:
            #print "get creds"
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        usercert = self.save_identity(creds['key'])
        
        #print "read from remote"
        pp, fifo = ssh.Copy.ReadFromRemote(usercert,dst,password=creds['password'],fifo=fifo)
        #print "read from remote returned"
        
        return pp, fifo
