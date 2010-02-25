# -*- coding: utf-8 -*-
import FSConnector
import os, stat, time
from fs.Exceptions import InvalidPath, PermissionDenied
from FifoPool import Fifos
from utils.parsers import *
import stackless

import subprocess

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "yabifs"

# the location of the directory we will serve out. This can be overridden in the constuctor if wanted
DIRECTORY = "/"

DEBUG = True

DEBUG_READ_FIFO = True

from twisted.internet import protocol
from twisted.internet import reactor

from globus.BaseShell import BaseShellProcessProtocol

class SudoShellProcessProtocol(BaseShellProcessProtocol):
    pass

class SudoShell(object):
    sudo = "/usr/bin/sudo"
    
    def __init__(self):
        pass

    def _make_env(self, environ=None):
        """Return a custom environment for the specified cert file"""
        return environ.copy() if environ!=None else os.environ.copy()

    def _make_path(self):
        return "/tmp"

    def execute(self, protocol, systemuser, command):
        """execute a command using a process protocol and run it under sudo with the passed in system user"""

        subenv = self._make_env()
        pp = protocol()
        fullcommand = [self.sudo, "-u", systemuser] + command
        
        if DEBUG:
            print "env:",subenv
            print "system user:",systemuser
            print "exec:",command
            print "full:",fullcommand
            
        reactor.spawnProcess(   pp,
                                fullcommand[0],
                                fullcommand,
                                env=subenv,
                                path=self._make_path()
                            )
        return pp
        
    def ls(self, user, directory, args="-alFR"):
        return self.execute(SudoShellProcessProtocol, user, command=["ls",args,directory])
      
    def mkdir(self, user, directory, args="-p"):
        return self.execute(SudoShellProcessProtocol, user, command=["mkdir",args,directory])
      
    def rm(self, user, directory, args=None):
        return self.execute(SudoShellProcessProtocol, user, command=["rm",args,directory]) if args else self.execute(SudoShellProcessProtocol, user,command=["rm",directory]) 
        
    def cp(self, proto, user, src, dst, args=None):
        return self.execute(proto, user, command=["cp",args,src,dst]) if args else self.execute(proto,user,command=["cp",args,src,dst])
        


class FSWriteProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.err = ""
        self.out = ""
        self.exitcode = None
        self.started=False
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        self.transport.closeStdin()
        self.started=True
        
    def outReceived(self, data):
        self.out += data
        #print "OUT:",data
        
    def errReceived(self, data):
        self.err += data
        #print "ERR:",data
            
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        #print "OCL"
        pass
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        #print "EXIT:",self.exitcode
        
    def isDone(self):
        return self.exitcode != None
    
    def isStarted(self):
        return self.started

class LocalFilesystem(FSConnector.FSConnector):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="Globus File System"
    copy = '/bin/cp'
    
    def __init__(self, directory=DIRECTORY):
        FSConnector.FSConnector.__init__(self)
        self.directory = directory
    
    def _get_filename(self, path):
        """Using this classes 'path', return the real FS path that this refers to"""
        while len(path) and path[0]=='/':
            path = path[1:]
            
        return os.path.join(self.directory,path)
    
    def mkdir(self, host, username, path, creds, yabiusername=None ):
        assert yabiusername or creds, "You must pass in a credential or a yabiusername so I can go get a credential. Neither was passed in."
        
        # TODO: fix the insecure aassumption that the user has credentials for this!
        pp = SudoShell().mkdir(username, path)
        
        while not pp.isDone():
            stackless.schedule()
            
        err, mkdir_data = pp.err, pp.out
        
        if pp.exitcode != 0:
            # an error occured
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
            
        if DEBUG:
            print "mkdir_data=",mkdir_data
            print "err", err
        
        return mkdir_data
     
    def rm(self, host, username, path, yabiusername=None, recurse=False, creds=None):
        assert yabiusername or creds, "You must pass in a credential or a yabiusername so I can go get a credential. Neither was passed in."
        
        # TODO: fix the insecure aassumption that the user has credentials for this!
        pp = SudoShell().rm(username, path, args="-r" if recurse else None)
        
        while not pp.isDone():
            stackless.schedule()
            
        err, rm_data = pp.err, pp.out
        
        if pp.exitcode != 0:
            # an error occured
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
            
        if DEBUG:
            print "rm_data=",rm_data
            print "err", err
        
        return rm_data
     
    def ls(self, host, username, path, yabiusername=None, recurse=False, culldots=True, creds={}):
        assert yabiusername or creds, "You must pass in a credential or a yabiusername so I can go get a credential. Neither was passed in."
        
        # TODO: fix the insecure aassumption that the user has credentials for this!
        pp = SudoShell().ls(username, path, args="-alFR" if recurse else "-alF")
        
        while not pp.isDone():
            stackless.schedule()
            
        err, out = pp.err, pp.out
        
        if pp.exitcode != 0:
            # an error occured
            if "Permission denied" in err:
                raise PermissionDenied(err)
            else:
                raise InvalidPath(err)
            
        ls_data = parse_ls(out, culldots=culldots)
            
        if DEBUG:
            print "ls_data=",ls_data
            print "out", out
            print "err", err
        
        # are we non recursive
        if not recurse:
            # "None" path header is actually our path in this case
            ls_data[path] = ls_data[None]
            del ls_data[None]
        
        return ls_data
        
        return ls_data

    def _make_env(self):
        """Return a custom environment for the specified cert file"""
        subenv = os.environ.copy()
        return subenv
    
    def _make_path(self):
        return "/bin"

    def GetWriteFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a write fifo to a remote path as a certain user.
        """
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        
        dst = os.path.join(self._get_filename(path),filename)
        
        # change the permissions on the destination
        chmod = ["sudo","-u",username,"chmod","o+w",dst]
        subprocess.check_call(chmod)
                
        # the copy to remote command
        procproto = FSWriteProtocol()
        
        #SudoShell().cp(procproto,username,fifo,dst)
        reactor.spawnProcess(   procproto,
                                self.copy,
                                [ self.copy, fifo, dst ],
                                env=self._make_env(),
                                path=self._make_path()
                            )
        
        # link our protocol processor to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, procproto )
        
        return procproto, fifo
            
    def GetReadFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        """
        # make our source fifo to get our data from
        if not fifo:
            fifo = Fifos.Get()
        
        src = os.path.join(self._get_filename(path),filename)
        
        # change the permissions on the source
        chmod = ["sudo","-u",username,"chmod","o+r",src]
        subprocess.check_call(chmod)
        
        # debug info about the source file
        if DEBUG_READ_FIFO:
            print "Info about the source file:"
            print "path:",src
            
            statinfo = os.stat(src)
            
            print "stat:",statinfo
            print "st_size:",statinfo.st_size
        
        # the copy to remote command
        procproto = FSWriteProtocol()
        
        #SudoShell().cp(procproto,username,src,fifo)
        reactor.spawnProcess(   procproto,
                                self.copy,
                                [ self.copy, src, fifo ],
                                env=self._make_env(),
                                path=self._make_path()
                            )
        
        # link our protocol processor to this fifo, so if we die, the fifo will be cleared up
        Fifos.WeakLink( fifo, procproto )
        
        return procproto, fifo
            
    
        