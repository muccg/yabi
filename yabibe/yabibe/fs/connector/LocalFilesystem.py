# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
import FSConnector
import stackless
from utils.parsers import *
from Exceptions import PermissionDenied, InvalidPath, IsADirectory
from FifoPool import Fifos
from twisted.internet import protocol
from twisted.internet import reactor
import os
import json
from utils.parsers import parse_ls

from conf import config

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "localfs"

MAX_FS_OPERATIONS = 32                          # how long the lockqueue should be

# paths to localfs helper commands
LS_PATH = '/bin/ls'
MKDIR_PATH = '/bin/mkdir'
RM_PATH = '/bin/rm'
LN_PATH = '/bin/ln'
CP_PATH = '/bin/cp'

LS_TIME_STYLE = r"+%b %d  %Y"

DEBUG = True
 
from decorators import retry, call_count
from LockQueue import LockQueue
from utils.stacklesstools import sleep

def convert_filename_to_encoded_for_echo(filename):
    """This function takes a filename, and encodes the whole thing to a back ticked eval command.
    This enables us to completely encode a full filename across ssh without any nasty side effects from special characters"""
    CHARS_TO_REPLACE = '\\' + "'" + '"' + "$@!~|<>#;*[]{}?%^&()= "
    for char in CHARS_TO_REPLACE:
        filename=filename.replace(char,"\\x%x"%(ord(char)))
    return filename

class LocalShellProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, stdin=None):
        self.stdin=stdin
        self.err = ""
        self.out = ""
        self.exitcode = None
        self.started = False
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        if self.stdin:
            self.transport.write(self.stdin)
        self.transport.closeStdin()
        
        self.started = True
        
    def outReceived(self, data):
        self.out += data
        if DEBUG:
            print "OUT:",data
        
    def errReceived(self, data):
        self.err += data
        if DEBUG:
            print "ERR:",data
    
    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        if DEBUG:
            print "Out lost"
        self.unifyLineEndings()
        
    def inConenctionLost(self):
        if DEBUG:
            print "In lost"
        self.unifyLineEndings()
        
    def errConnectionLost(self):
        if DEBUG:
            print "Err lost"
        self.unifyLineEndings()
        
    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        if DEBUG:
            print "proc ended",self.exitcode
        self.unifyLineEndings()
        
    def unifyLineEndings(self):
        # try to unify the line endings to \n
        self.out = self.out.replace("\r\n","\n")
        self.err = self.err.replace("\r\n","\n")
        
    def isDone(self):
        return self.exitcode != None
        
    def isFailed(self):
        return self.isDone() and self.exitcode != 0
        
    def isStarted(self):
        return self.started

class LocalShell(object):
    def __init__(self):
        pass

    def _make_path(self):
        return "/usr/bin"    

    def _make_env(self, environ=None):
        """Return a custom environment for the specified cert file"""
        subenv = environ.copy() if environ!=None else os.environ.copy()
        return subenv    

    def _make_echo(self,filename):
        """Turn a filename into the remote eval line"""
        return filename
        result = '"`echo -e \'%s\'`"'%(convert_filename_to_encoded_for_echo(filename))
        return result
    
    def execute(self, pp, command):
        """execute a command using a process protocol"""

        subenv = self._make_env()
        if DEBUG:
            print "env",subenv
            print "exec:",command
            print  [pp,
                                command[0],
                                command,
                                subenv,
                                self._make_path()]
            
            
        reactor.spawnProcess(   pp,
                                command[0],
                                command,
                                env=subenv,
                                path=self._make_path()
                            )
        return pp

    def mkdir(self, path):
        return self.execute()
        
    def ls(self,path,recurse=False):
        return self.execute(LocalShellProcessProtocol(),[LS_PATH,"--time-style=%s"%(LS_TIME_STYLE),"-lFR" if recurse else "-lF",path])
        
    def mkdir(self, directory, args="-p"):
        return self.execute(LocalShellProcessProtocol(),[MKDIR_PATH,args,self._make_echo(directory)])
      
    def rm(self, directory, args=None):
        return self.execute(LocalShellProcessProtocol(),[RM_PATH] + ( [args] if args else [] ) + [self._make_echo(directory)] )

    def ln(self, target, link, args="-s"):
        return self.execute(LocalShellProcessProtocol(),[LN_PATH] + ( [args] if args else [] ) + [self._make_echo(target),self._make_echo(link)])
        
    def cp(self, src, dst, args=None):
        # if the coipy is recursive, and the src ends in a slash, then we should add a wildcard '*' to the src to make it copy the contents of the directory
        if args is not None and "r" in args and src.endswith("/"):
            return self.execute(LocalShellProcessProtocol(),command=[CP_PATH]+ ([args] if args else []) +[self._make_echo(src)+"*",self._make_echo(dst)])
        else:
            return self.execute(LocalShellProcessProtocol(),command=[CP_PATH]+ ([args] if args else []) +[self._make_echo(src),self._make_echo(dst)])

    def WriteToRemote(self,path,fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
        
        return self.execute(LocalShellProcessProtocol(),command=[CP_PATH,fifo,self._make_echo(path)]), fifo
        
    def ReadFromRemote(self,path,fifo=None):
        subenv = self._make_env()
        
        if not fifo:
            fifo = Fifos.Get()
                
        return self.execute(LocalShellProcessProtocol(),command=[CP_PATH,self._make_echo(path),fifo]), fifo
        

class LocalFilesystem(FSConnector.FSConnector, object):
    """This is the resource that connects to the ssh backends"""
    VERSION=0.1
    NAME="Local Backend Filesystem"
    
    def __init__(self):
        FSConnector.FSConnector.__init__(self)
        
        # make a path to store keys in
        configdir = config.config['backend']['certificates']
        
        # instantiate a lock queue for this backend. Key refers to the particular back end. None is the global queue
        self.lockqueue = LockQueue( MAX_FS_OPERATIONS )
        
    def lock(self,*args,**kwargs):
        return self.lockqueue.lock(*args, **kwargs)
        
    def unlock(self, tag):
        return self.lockqueue.unlock(tag)
        
    @retry(5,(InvalidPath,PermissionDenied))
    #@call_count
    def mkdir(self, host, username, path, port=22, yabiusername=None, creds={},priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        
        # call the mkdir function
        pp = LocalShell().mkdir(path)
        
        while not pp.isDone():
            stackless.schedule()
            
        if priority:
            self.lockqueue.unlock(lock)
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in err:
                raise InvalidPath("No such file or directory\n")
            else:
                print "local mkdir failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
        if DEBUG:
            print "mkdir_data=",out
            print "err", err

        return out
        
    @retry(5,(InvalidPath,PermissionDenied, IsADirectory))
    #@call_count
    def rm(self, host, username, path, port=22, yabiusername=None, recurse=False, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        
        pp = LocalShell().rm(path,args="-rf" if recurse else "-f")
        
        while not pp.isDone():
            stackless.schedule()
        
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in err:
                raise InvalidPath("No such file or directory\n")
            elif "Is a directory" in err:
                raise IsADirectory("Cannot delete a directory without using recursive delete: %s\n"%(err))
            else:
                print "rm failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
        if DEBUG:
            print "rm_data=",out
            print "err", err

        return out
    
    @retry(5,(InvalidPath,PermissionDenied))
    #@call_count
    def ls(self, host, username, path, port=22, yabiusername=None, recurse=False, culldots=True, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "LocalFilesystem::ls(",host,username,path,port,yabiusername,recurse,culldots,creds,priority,")"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
                
        pp = LocalShell().ls(path, recurse=recurse)
        
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
            elif "No such file" in err:
                raise InvalidPath("No such file or directory\n")
            else:
                print "LS failed with exit code %d and output: %s"%(pp.exitcode,out)
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
            
        return ls_data
        
    @retry(5,(InvalidPath,PermissionDenied))
    #@call_count
    def ln(self, host, username, target, link, port=22, yabiusername=None, creds={},priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        pp = LocalShell().ln(target, link)
        
        while not pp.isDone():
            stackless.schedule()
            
        if priority:
            self.lockqueue.unlock(lock)
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in err:
                raise InvalidPath("No such file or directory\n")
            else:
                print "ln failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
        if DEBUG:
            print "ln_data=",out
            print "ln_err", err
        
        return out
        
    @retry(5,(InvalidPath,PermissionDenied))
    #@call_count
    def cp(self, host, username, src, dst, port=22, yabiusername=None, recurse=False, creds={},priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        # acquire our queue lock
        if priority:
            lock = self.lockqueue.lock()
        
        pp = LocalShell().cp(src, dst, args="-r" if recurse else None)
        
        while not pp.isDone():
            stackless.schedule()
            
        if priority:
            self.lockqueue.unlock(lock)
            
        err, out = pp.err, pp.out
        
        if pp.exitcode!=0:
            # error occurred
            if "Permission denied" in err:
                raise PermissionDenied(err)
            elif "No such file or directory" in err:
                if not ("cp: cannot stat" in str(err) and "*': No such file or directory" in str(err) and recurse==True):
                    raise InvalidPath("No such file or directory\n")
            else:
                print "cp failed with exit code %d and output: %s"%(pp.exitcode,out)
                raise Exception(err)
        
        if DEBUG:
            print "cp_data=",out
            print "cp_err", err

        return out
        
    
        
    #@lock
    def GetWriteFifo(self, host=None, username=None, path=None, port=22, filename=None, fifo=None, yabiusername=None, creds={}, priority=0):
        """sets up the chain needed to setup a write fifo from a remote path as a certain user.
        
        pass in here the username, path
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "LocalFilesystem::GetWriteFifo( host:"+host,",username:",username,",path:",path,",filename:",filename,",fifo:",fifo,",yabiusername:",yabiusername,",creds:",creds,")"
        
        dst = os.path.join(path,filename)
        
        pp, fifo = LocalShell().WriteToRemote(dst,fifo=fifo)
        
        return pp, fifo
    
    #@lock
    def GetReadFifo(self, host=None, username=None, path=None, port=22, filename=None, fifo=None, yabiusername=None, creds={}, priority=0):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "LocalFilesystem::GetReadFifo(",host,username,path,filename,fifo,yabiusername,creds,")"
        dst = os.path.join(path,filename)
        
        pp, fifo = LocalShell().ReadFromRemote(dst,fifo=fifo)
        #print "read from remote returned"
        
        return pp, fifo
