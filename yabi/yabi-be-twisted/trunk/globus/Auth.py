"""Encapsulation of globus Authentication proxies as a mixin"""

from utils.stacklesstools import GET, GETFailure, sleep
import json
from globus.CertificateProxy import CertificateProxy

class NoCredentials(Exception):
    """User has no globus credentials for this server"""
    pass

class GlobusAuth(object):
    
    def CreateAuthProxy(self):
        """creates the authproxy object store"""
        self.authproxy = {}                         # keys are hostnames
    
    def GetAuthProxy(self, hostname):
        return self.authproxy[hostname]
    
    def AuthProxyUser(self, scheme, username, hostname, *args):
        """Auth a user via getting the credentials from the json yabiadmin backend. When the credentials are gathered, successcallback is called with the deferred.
        The deferred should be the result channel your result will go back down"""
        assert hasattr(self,"authproxy"), "Class must have an authproxy parameter"
        
        host,port = "localhost",8000
        useragent = "YabiFS/0.1"
        
        print "AuthProxyUser %s://%s@%s/"%(scheme,username,host)
        
        try:
            status, message, data = GET( path ="/yabiadmin/ws/credential/%s/%s/%s/"%(scheme,username,hostname),
                                        host = host,
                                        port = port )
            
            assert status==200
            credentials = json.loads( data )
            
            # create the user proxy
            if hostname not in self.authproxy:
                self.authproxy[hostname]=CertificateProxy()
            self.authproxy[hostname].CreateUserProxy(username,credentials['cert'],credentials['key'],credentials['password'])
            
            return credentials
        
        except GETFailure, gf:
            raise NoCredentials( "User: %s does not have credentials for this backend\n"%username )
        
    
    def EnsureAuthed(self, scheme, username, hostname):
        # do we have an authenticator for this host?
        if hostname not in self.authproxy:
            # no!
            return self.AuthProxyUser(scheme,username,hostname)
        else:
            # yes! lets see if we have a valid cert
            if not self.authproxy[hostname].IsProxyValid(username):
                return self.AuthProxyUser(scheme,username,hostname)
            # else user is already authed
                