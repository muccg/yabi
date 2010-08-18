# -*- coding: utf-8 -*-
import FSConnector
import globus
import stackless
from utils.parsers import *
from fs.Exceptions import PermissionDenied, InvalidPath
from FifoPool import Fifos
from twisted.internet import protocol
from twisted.internet import reactor
import os
import s3

s3auth = s3.S3Auth.S3Auth()

#sshauth = ssh.SSHAuth.SSHAuth()
ACCESSKEYID = 'AKIAJPCC7ZU6WWMU425A'
SECRETKEYID = 's2DOLKdev8GFXHKnqUnB2zl8pDpvnITo1R+FJCby'
BUCKET = 'yabi'

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = []

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "s3"

DEBUG = True

# helper utilities for s3
from s3 import S3

class S3Error(Exception):
    pass

def mkdir(bucket, path):
    assert path[-1]=='/', "Path needs to end in a slash"
    
    obj = S3.S3Object( data='', metadata={  's3-console-folder': 'true',
                                            's3-console-metadata-version': '2010-03-09' } )
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.put(bucket,path,obj,headers={"Content-Length":"0"})
    
    if response.http_response.status!=200:
        raise S3Error("Could not create directory '%s' in bucket '%s': %s"%(path, bucket, response.message))

def rm(bucket, path):
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.delete(bucket,path)
    if response.http_response.status != 200:
        raise S3Error("Could not delete key '%s' in bucket '%s': %s"%(path, bucket, response.message))

def ls(bucket, path):
    SEP = '/'
    
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.list_bucket(bucket)
    
    if response.http_response.status != 200:
        raise S3Error("Could not list bucket '%s': %s"%(bucket,response.message))
   
    #print "==>",dir(response.entries[0])
    #print response.entries[0].size
    entries = [(X.key.split(SEP),X.size) for X in response.entries]
    
    # we now filter the list down to just what we would see in this directory
    while path.endswith('/'):
        path = path[:-1]
    our_filter = path.split(SEP)
    
    paths = entries
    if len(path):
        print "F:",our_filter
        for part in our_filter:
            print ":",paths
            paths = [ X[1:] for X in paths if X[0]==part ]
    
    # what are folders and what are entries. If there is any extra path parts, its a folder
    files = [X[0] for X in paths if len(X)==1]
    if paths==[[]] or paths==[]:
        raise S3Error("Path not a directory")
            
    folders = list(set([X[0] for X in paths if X[0] not in files]))
    
    return_data = [A for A in files if A],[B for B in folders if B]
    print "RETURNING",return_data
    return return_data



class S3Filesystem(FSConnector.FSConnector, object):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="S3 Filesystem"
    #copymode = "ssh"
    
    def __init__(self):
        FSConnector.FSConnector.__init__(self)
        #ssh.KeyStore.KeyStore.__init__(self)
        
    def mkdir(self, host, username, path, yabiusername=None, creds={}):
        mkdir(BUCKET, path)
        return "OK"
        
    def rm(self, host, username, path, yabiusername=None, recurse=False, creds={}):
        rm(BUCKET, path)
        return
    
    def ls(self, host, username, path, yabiusername=None, recurse=False, culldots=True, creds={}):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if DEBUG:
            print "S3Filesystem::ls(",host,username,path,yabiusername,recurse,culldots,creds,")"
        
        # If we don't have creds, get them
        if not creds:
            #assert False, "presently we NEED creds"
            creds = s3auth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        files,folders = ls(BUCKET, path)
              
        print "S3 issue",{
            path : {
                'files':files,
                'directories':folders
            }
        }
              
        return {
            path : {
                'files':[(filename, 0, "unknown" ) for filename in files],
                'directories':[(filename, 0, "unknown" ) for filename in folders]
            }
        }
        
    def GetWriteFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a write fifo from a remote path as a certain user.
        
        pass in here the username, path
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "S3Filesystem::GetWriteFifo( host:"+host,",username:",username,",path:",path,",filename:",filename,",fifo:",fifo,",yabiusername:",yabiusername,",creds:",creds,")"
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        dst = "%s@%s:%s"%(username,host,os.path.join(path,filename))
        
        # make sure we are authed
        if not creds:
            assert False, "creds not supported in S3"
            #creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        #usercert = self.save_identity(creds['key'])
        
        pp, fifo = ssh.Copy.WriteToRemote(usercert,dst,password=creds['password'],fifo=fifo)
        
        return pp, fifo
    
    def GetReadFifo(self, host=None, username=None, path=None, filename=None, fifo=None, yabiusername=None, creds={}):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        print "S3::GetReadFifo(",host,username,path,filename,fifo,yabiusername,creds,")"
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        dst = "%s@%s:%s"%(username,host,os.path.join(path,filename))
        
        # make sure we are authed
        if not creds:
            #print "get creds"
            assert False, "creds not supported in S3"
            #creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        #usercert = self.save_identity(creds['key'])
        
        #print "read from remote"
        pp, fifo = ssh.Copy.ReadFromRemote(usercert,dst,password=creds['password'],fifo=fifo)
        #print "read from remote returned"
        
        return pp, fifo
       