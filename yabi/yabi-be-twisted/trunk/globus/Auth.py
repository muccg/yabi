# -*- coding: utf-8 -*-
"""Encapsulation of globus Authentication proxies as a mixin"""

from utils.stacklesstools import RetryGET, GETFailure, sleep
import json, os
from globus.CertificateProxy import CertificateProxy
from conf import config
import urllib

class NoCredentials(Exception):
    """User has no globus credentials for this server"""
    pass

class AuthException(Exception):
    pass

class GlobusAuth(object):
    
    def CreateAuthProxy(self):
        """creates the authproxy object store"""
        self.authproxy = {}                         # keys are hostnames
    
    def GetAuthProxy(self, hostname):
        return self.authproxy[hostname]
    
    def AuthProxyUser(self, yabiusername, scheme, username, hostname, path, *args):
        """Auth a user via getting the credentials from the json yabiadmin backend. When the credentials are gathered, successcallback is called with the deferred.
        The deferred should be the result channel your result will go back down"""
        assert hasattr(self,"authproxy"), "Class must have an authproxy parameter"
        
        useragent = "YabiFS/0.1"
        
        try:
            status, message, data = RetryGET( path = os.path.join(config.yabiadminpath,"ws/credential/%s/?uri=%s://%s@%s%s"%(yabiusername,scheme,username,hostname,urllib.quote(path))),
                                        host = config.yabiadminserver,
                                        port = config.yabiadminport )
            
            assert status==200
            credentials = json.loads( data )
            
            # create the user proxy
            if hostname not in self.authproxy:
                self.authproxy[hostname]=CertificateProxy()
            expire_time = self.authproxy[hostname].CreateUserProxy(username,credentials['cert'],credentials['key'],credentials['password'])
            
            print "EXPIRES IN:",expire_time
            
            return credentials
        
        except GETFailure, gf:
            gf_message = gf.args[0]
            if gf_message[0]==-1:
                # connection problems
                raise AuthException( "Tried to get credentials from %s:%d and failed: %s"%(config.yabiadminserver,config.yabiadminport,gf_message[1]) )
            raise NoCredentials( "User: %s does not have credentials for this backend %s on host %s\n"%(username,scheme,hostname) )
        
    
    def EnsureAuthed(self, yabiusername, scheme, username, hostname, path):
        # do we have an authenticator for this host?
        if hostname not in self.authproxy:
            # no!
            return self.AuthProxyUser(yabiusername, scheme,username,hostname, path)
        else:
            # yes! lets see if we have a valid cert
            if not self.authproxy[hostname].IsProxyValid(username):
                return self.AuthProxyUser(yabiusername,scheme,username,hostname, path)
            # else user is already authed
                
    def AuthProxyUserWithCredentials(self, hostname, username, cert, key, password):
        if hostname not in self.authproxy:
            self.authproxy[hostname]=CertificateProxy()
        expire_time = self.authproxy[hostname].CreateUserProxy(username,cert,key,password)
        print "EXPIRES IN:",expire_time
        
    def EnsureAuthedWithCredentials(self, hostname, username, cert, key, password):
        if hostname not in self.authproxy:
            # no!
            return self.AuthProxyUserWithCredentials(hostname,username,cert,key,password)
        else:
            # yes! lets see if we have a valid cert
            if not self.authproxy[hostname].IsProxyValid(username):
                return self.AuthProxyUserWithCredentials(hostname,username,cert,key,password)
            # else user is already authed
        