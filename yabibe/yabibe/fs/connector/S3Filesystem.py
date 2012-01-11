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
from utils.protocol import globus
import gevent
from utils.parsers import *
from Exceptions import PermissionDenied, InvalidPath
from FifoPool import Fifos
from twisted.internet import protocol
from twisted.internet import reactor
import os
from utils.protocol import s3

s3auth = s3.S3Auth.S3Auth()

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = []

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "s3"

DEBUG = False

# helper utilities for s3
from utils.protocol.s3 import S3
from utils.protocol.s3 import s3utils
    
class S3Error(Exception):
    pass

def mkdir(bucket, path, ACCESSKEYID, SECRETKEYID):
    assert path[-1]=='/', "Path needs to end in a slash"
    
    obj = S3.S3Object( data='', metadata={  's3-console-folder': 'true',
                                            's3-console-metadata-version': '2010-03-09' } )
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.put(bucket,path,obj,headers={"Content-Length":"0"})
    
    if not (200 <= response.http_response.status <300):
        raise S3Error("Could not create directory '%s' in bucket '%s': %s"%(path, bucket, response.message))

def rm(bucket, path, ACCESSKEYID, SECRETKEYID):
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    #print "RM",path
    response = conn.delete(bucket,path)
    if not (200 <= response.http_response.status <300):
        raise S3Error("Could not delete key '%s' in bucket '%s': %s"%(path, bucket, response.message))

def rmrf(bucket, path, ACCESSKEYID, SECRETKEYID):
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.list_bucket(bucket)
    
    if not (200 <= response.http_response.status <300):
        raise S3Error("Could recursive delete because could not list bucket '%s': %s"%(bucket,response.message))
   
    tree = s3utils.make_tree([(OBJ.key,OBJ) for OBJ in response.entries])
    
    # find the child node
    treenode = tree.find_node(path)
    
    # delete all below
    for obj in treenode.walk():
        try:
            #print "DEL1",obj.key
            response = conn.delete(bucket,obj.key)
            if not (200 <= response.http_response.status <300):
                raise S3Error("Aborting recursive delete because could not delete key '%s' in bucket '%s': %s"%(path, bucket, response.message))
        except AttributeError:
            #print "SKIP",obj.s3folder
            if obj.s3folder:
                #print "DEL2",obj.s3folder.key
                response = conn.delete(bucket,obj.s3folder.key)
                if not (200 <= response.http_response.status <300):
                    raise S3Error("Aborting recursive delete because could not delete key '%s' in bucket '%s': %s"%(path, bucket, response.message))
    
    # delete this node now
    #print "DEL3",path
    rm(bucket, path, ACCESSKEYID, SECRETKEYID)
    

def ls(bucket, path, ACCESSKEYID, SECRETKEYID):
    # path separator
    SEP = '/'
    
    #if there are MULTIPLE seperators on the end, remove all but one
    # TODO: fix the extra / on initial root directory listings
    while len(path)>=2 and path[-2:] == (SEP*2):
        path=path[:-1]
    
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.list_bucket(bucket)
    
    if not (200 <= response.http_response.status <300):
        raise S3Error("Could not list bucket '%s': %s"%(bucket,response.message))
   
    tree = s3utils.make_tree([(OBJ.key,OBJ) for OBJ in response.entries])
    #tree.dump()
    try:
        lsdata = tree.ls(path)
    except s3utils.NodeNotFound:
        raise InvalidPath("No such file or directory\n")
    
    return lsdata

def lsrecurse(bucket, path, ACCESSKEYID, SECRETKEYID):
    # path separator
    SEP = '/'
    
    #if there are MULTIPLE seperators on the end, remove all but one
    # TODO: fix the extra / on initial root directory listings
    while len(path)>=2 and path[-2:] == (SEP*2):
        path=path[:-1]
    
    conn = S3.AWSAuthConnection(ACCESSKEYID, SECRETKEYID)
    response = conn.list_bucket(bucket)
    
    if not (200 <= response.http_response.status <300):
        raise S3Error("Could not list bucket '%s': %s"%(bucket,response.message))
   
    tree = s3utils.make_tree([(OBJ.key,OBJ) for OBJ in response.entries])
    directory = tree.find_node(path)
    
    def get_ls_data(lpath,ldirectory):
        files, folders = ldirectory.ls()
        out = { lpath:{'files':files,'directories':folders } }
        for folder in [X[0] for X in folders]:
            out.update(get_ls_data(lpath+folder+"/",ldirectory.find_node(folder)))
        return out
            
    return get_ls_data(path,directory)
    
class S3Filesystem(FSConnector.FSConnector, object):
    """This is the resource that connects to the globus gridftp backends"""
    VERSION=0.1
    NAME="S3 Filesystem"
    #copymode = "ssh"
    
    def __init__(self):
        FSConnector.FSConnector.__init__(self)
        #ssh.KeyStore.KeyStore.__init__(self)
        
    def _decode_bucket(self, host, username, path, yabiusername=None, creds={}):
        """return the bucket and actual credentials for a request"""
        bucket = host.split(".")[0]
        
        # remove prefixed '/'s from path
        while len(path) and path[0]=='/':
            path = path[1:]
       
        # If we don't have creds, get them
        if not creds:
            #assert False, "presently we NEED creds"
            creds = s3auth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
        
        # return everything
        return bucket, path, creds['cert'],creds['key']
        
    def mkdir(self, host, username, path, port=None, yabiusername=None, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        mkdir(*self._decode_bucket(host, username, path, yabiusername, creds))
        return "OK"
        
    def rm(self, host, username, path, port=None, yabiusername=None, recurse=False, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        if recurse:
            rmrf( *self._decode_bucket(host, username, path, yabiusername, creds) )
        else:
            rm( *self._decode_bucket(host, username, path, yabiusername, creds) )
        return "OK"
    
    def ls(self, host, username, path, port=None, yabiusername=None, recurse=False, culldots=True, creds={}, priority=0):
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        
        if not recurse:
            files,folders = ls(*self._decode_bucket(host, username, path, yabiusername, creds))
                
            return {
                path : {
                    'files':files,
                    'directories':folders,
                }
            }
        else:
            return lsrecurse(*self._decode_bucket(host, username, path, yabiusername, creds))
        
    def GetWriteFifo(self, host=None, username=None, path=None, port=None, filename=None, fifo=None, yabiusername=None, creds={}, priority=0):
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
            creds = s3auth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        pp, fifo = s3.Copy.WriteToRemote(creds['cert'],dst,password=creds['key'],fifo=fifo)
        
        return pp, fifo
    
    def GetReadFifo(self, host=None, username=None, path=None, port=None, filename=None, fifo=None, yabiusername=None, creds={}, priority=0):
        """sets up the chain needed to setup a read fifo from a remote path as a certain user.
        
        pass in here the username, path, and a deferred
    
        if a fifo pathis apssed in, use that one instead of making one
    
        when everything is setup and ready, deferred will be called with (proc, fifo), with proc being the python subprocess Popen object
        and fifo being the filesystem location of the fifo.
        """
        if DEBUG:
            print "S3::GetReadFifo(",host,username,path,filename,fifo,yabiusername,creds,")"
        assert yabiusername or creds, "You must either pass in a credential or a yabiusername so I can go get a credential. Neither was passed in"
        dst = "%s@%s:%s"%(username,host,os.path.join(path,filename))
        
        # make sure we are authed
        if not creds:
            #print "get creds"
            creds = s3auth.AuthProxyUser(yabiusername, SCHEMA, username, host, path)
            
        pp, fifo = s3.Copy.ReadFromRemote(creds['cert'],dst,password=creds['key'],fifo=fifo)
        #print "read from remote returned"
        
        if DEBUG:
            print "S3::GetReadFifo returning",pp,fifo
        
        return pp, fifo
       