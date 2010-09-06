# -*- coding: utf-8 -*-
"""
This is a module level certificate proxy for globus. It runs 'grid-proxy-cert' and generates a proxy to use. It keeps this
around until it expires.
"""
import tempfile
import subprocess
import os
import time
import stat
import sys

import log

from twisted.internet import protocol
from twisted.internet import reactor

from conf import config

import stackless

class ProxyInitError(Exception):
    pass

class ProxyInvalidPassword(Exception):
    pass

GLOBUS_TIME_FORMAT = "%a %b %d %H:%M:%S %Y"
DEFAULT_CERTIFICATE_EXPIRY_MINUTES = 60*3                          # set this for how often we refresh
DEFAULT_CERTIFICATE_EXPIRY_MINUTES = 2                          # set this for how often we refresh

def _decode_time(timestring):
    """turn 'Tue Jun  9 04:02:41 2009' into a unix timestamp"""
    return time.strptime( timestring, GLOBUS_TIME_FORMAT )

def rm_rf(root):
    for path, dirs, files in os.walk(root, False):
        for fn in files:
            os.unlink(os.path.join(path, fn))
        for dn in dirs:
            os.rmdir(os.path.join(path, dn))
    os.rmdir(root)

class GridProxyInitProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, stdin=None):
        self.stdin=stdin
        self.err = ""
        self.out = ""
        self.exitcode = None
        
    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        #print "CM"
        if self.stdin:
            #print "writing",self.stdin
            self.transport.write(str(self.stdin))
        self.transport.closeStdin()
        
    def connectionLost(self):
        #print "CL"
        pass
        
    def outReceived(self, data):
        #print "OR",data
        self.out += data
        
    def errReceived(self, data):
        #print "ER", data
        self.err += data
            
    def processEnded(self, status_object):
        #print "PE"
        self.exitcode = status_object.value.exitCode
        
    def isDone(self):
        return self.exitcode != None

class CertificateProxy(object):
    grid_proxy_init = "/usr/local/globus/bin/grid-proxy-init"
    
    def __init__(self, expiry=DEFAULT_CERTIFICATE_EXPIRY_MINUTES, storage=None):
        if not storage:
            self._make_cert_storage()
        else:
            assert os.path.exists(storage) and os.path.isdir(storage), "storage path needs to exist and be a directory"
            self.tempdir=storage
        self.SetExpiryTime(expiry)
        
        self.pp_info = {}                           # info about process protocol for a grid-proxy-init possibly running in another stackless thread
    
    def SetExpiryTime(self, expiry):
        self.CERTIFICATE_EXPIRY_MINUTES = expiry
        self.CERTIFICATE_EXPIRY_SECONDS = 60*self.CERTIFICATE_EXPIRY_MINUTES
        self.CERTIFICATE_EXPIRY_TIME = "%d:%d"%(self.CERTIFICATE_EXPIRY_MINUTES/60,self.CERTIFICATE_EXPIRY_MINUTES%60)
    
    def CleanUp(self):
        """Clean up the proxy directory"""
        assert(self.tempdir)
        rm_rf(self.tempdir)
        self.tempdir=None
    
    @property
    def storage(self):
        """A property that is the directory we store the cert proxies in"""
        return self.tempdir
    
    def ProxyFile(self, userid):
        """return the proxy file location for the specified user"""
        return os.path.join( self.tempdir, "%s.proxy"%userid )
    
    def IsProxyValid(self, userid):
        """Tells us if the creation time of the users proxy indicates that its valid or invalid"""
        filename = self.ProxyFile(userid)
        if not os.path.exists(filename):
            # doesn't exist. Not valid
            return False
        
        # get timestamp
        fstat = os.stat(filename)
        ctime = fstat[stat.ST_CTIME]
        
        return time.time()-ctime < self.CERTIFICATE_EXPIRY_SECONDS

    def _make_cert_storage(self, directory=None):
        """makes a directory for storing the certificates in"""
        directory = directory or config.config['backend']['certificates']
        
        self.tempdir = tempfile.mkdtemp(prefix="yabi-credentials-", dir=directory)
        log.info("Certificate Proxy Store created in '%s'"%self.tempdir)
        
    def DestroyUserProxy(self, userid):
        os.unlink( self.ProxyFile(userid) )
        
    def CreateUserProxy(self, userid, cert, key, password):
        """creates the proxy object for the specified user, using the passed in cert and key, decrypted by password
        returns a struct_time representing the expiry time of the proxy
        
        TODO: What happens if this task blocks? The whole server blocks with it!
        """

        if userid in self.pp_info:
            pp = self.pp_info[userid]
            # we are already decrypting the proxy cert elsewhere. Lets just wait until that job is done and then return it.
            while not pp.isDone():
                print "CLASH!!!!!!"
                stackless.schedule()
                
            # the other task is complete now. let the other tasklet delete stale files.
            # decode the expiry time and return it as timestamp
            res = pp.out.split("\n")
            
            # get first line
            res = [X.split(':',1)[1] for X in res if X.startswith('Your proxy is valid until:')][0]
            
            return _decode_time(res.strip())
            
        # file locations
        certfile = os.path.join( self.tempdir, "%s.cert"%userid )
        keyfile = os.path.join( self.tempdir, "%s.key"%userid )
  

        # write out the pems
        with open( certfile, 'wb' ) as fh:
            fh.write(cert)
            
        with open( keyfile, 'wb' ) as fh:
            fh.write(key)
            
        # file permissions
        os.chmod( keyfile, 0600 )
        os.chmod( certfile, 0644 )
         
        # where our proxy will live
        proxyfile = self.ProxyFile(userid)
        
        # now run the grid-proxy-init code
        # run "/usr/local/globus/bin/grid-proxy-init -cert PEMFILE -key KEYFILE -pwstdin -out PROXYFILE"
        subenv = os.environ.copy()
        path="/usr/bin"
        pp = self.pp_info[userid] = GridProxyInitProcessProtocol("%s\n\n"%password)
        reactor.spawnProcess(   pp,
                                self.grid_proxy_init,
                                [  self.grid_proxy_init,
                                    "-debug",
                                    "-cert", certfile,
                                    "-key", keyfile,
                                    "-valid", self.CERTIFICATE_EXPIRY_TIME,
                                    "-pwstdin", 
                                    "-out", proxyfile ],
                                env=subenv,
                                path=path
                            )
        
        while not pp.isDone():
            stackless.schedule()

        code = pp.exitcode
        
        if code:
            # error
            if "Bad passphrase for key" in pp.out:
                raise ProxyInvalidPassword, "Could not initialise proxy: Invalid password"
            print "ERROR WHILE INITIALISING PROXY:"
            print "OUT:"
            print pp.out
            print "ERR:"
            print pp.err
            raise ProxyInitError, "Could not initialise proxy: %s"%(pp.out.split("\n")[0])
        
        # WTF are we getting unlink errors here. Lets list this directory for debug
        print "PRE UNLINK:",self.tempdir,"->",os.listdir(self.tempdir)
        
        with open(proxyfile) as fh:
            print "DUMP FILE:",fh.read()
        
        # delete the key and cert files now we have proxy
        os.unlink( certfile )
        os.unlink( keyfile )
        
        # decode the expiry time and return it as timestamp
        res = pp.out.split("\n")
        
        # get first line
        res = [X.split(':',1)[1] for X in res if X.startswith('Your proxy is valid until:')][0]
        
        del self.pp_info[userid]
        
        return _decode_time(res.strip())
      
