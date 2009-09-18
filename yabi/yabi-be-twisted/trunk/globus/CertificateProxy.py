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

class ProxyInitError(Exception):
    pass

class ProxyInvalidPassword(Exception):
    pass

GLOBUS_TIME_FORMAT = "%a %b %d %H:%M:%S %Y"
DEFAULT_CERTIFICATE_EXPIRY_MINUTES = 60*3                          # set this for how often we refresh

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

class CertificateProxy(object):
    grid_proxy_init = "/usr/local/globus/bin/grid-proxy-init"
    
    def __init__(self, expiry=DEFAULT_CERTIFICATE_EXPIRY_MINUTES, storage=None):
        if not storage:
            self._make_cert_storage()
        else:
            assert os.path.exists(storage) and os.path.isdir(storage), "storage path needs to exist and be a directory"
            self.tempdir=storage
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

    def _make_cert_storage(self):
        """makes a directory for storing the certificates in"""
        self.tempdir = tempfile.mkdtemp(prefix="yabi-credentials-")
        log.info("Certificate Proxy Store created in '%s'"%self.tempdir)
        
    def CreateUserProxy(self, userid, cert, key, password):
        """creates the proxy object for the specified user, using the passed in cert and key, decrypted by password
        returns a struct_time representing the expiry time of the proxy
        
        TODO: What happens if this task blocks? The whole server blocks with it!
        """
        #print "CreateUserProxy",userid
        #print "CERT",cert
        #print "KEY",key
        #print "PASSWORD",password
        
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
        
        # run "/usr/local/globus/bin/grid-proxy-init -cert PEMFILE -key KEYFILE -pwstdin -out PROXYFILE"
        proc = subprocess.Popen( [  self.grid_proxy_init,
                                    "-debug",
                                    "-cert", certfile,
                                    "-key", keyfile,
                                    "-valid", self.CERTIFICATE_EXPIRY_TIME,
                                    "-pwstdin", 
                                    "-out", proxyfile ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
                                    
        # run it passing in our password
        try:
            # TODO: non blocking version of this call
            stdout, stderr = proc.communicate( password )
        except OSError, ose:
            if ose[0]==32:
                # broken pipe
                raise ProxyInitError, "Could not initialise proxy: Broken pipe (key/cert file could be corrupt)"
            else:
                raise ose
        finally:
            # clean up the key/cert files
            os.unlink(certfile)
            os.unlink(keyfile)

        code = proc.returncode
        
        if code:
            # error
            if "Bad passphrase for key" in stdout:
                raise ProxyInvalidPassword, "Could not initialise proxy: Invalid password"
            raise ProxyInitError, "Could not initialise proxy: %s"%(stdout.split("\n")[0])
        
        # decode the expiry time and return it as timestamp
        res = stdout.split("\n")
        
        # get first line
        res = [X.split(':',1)[1] for X in res if X.startswith('Your proxy is valid until:')][0]
        
        return _decode_time(res.strip())
      
