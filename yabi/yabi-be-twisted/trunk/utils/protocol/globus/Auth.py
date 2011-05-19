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
"""Encapsulation of globus Authentication proxies as a mixin"""

from utils.stacklesstools import RetryGET, GETFailure, sleep
import json, os, time
from utils.protocol.globus.CertificateProxy import CertificateProxy
from conf import config
import urllib
from twisted.internet import reactor
from Exceptions import BlockingException, NoCredentials, AuthException

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
            
            return credentials
        
        except GETFailure, gf:
            gf_message = gf.args[0]
            if gf_message[0]==-1 and "404" in gf_message[1]:
                # connection problems
                raise NoCredentials( "User: %s does not have credentials for this user: %s backend: %s on host: %s\n"%(yabiusername,username,scheme,hostname) )
            
            raise AuthException( "Tried to get credentials from %s:%d and failed: %s %s"%(config.yabiadminserver,config.yabiadminport,gf_message[1],gf_message[2]) )
            
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
        #print "AuthProxyUserWithCredentials"
        if hostname not in self.authproxy:
            self.authproxy[hostname]=CertificateProxy()
        expire_time = self.authproxy[hostname].CreateUserProxy(username,cert,key,password)
        expires_in = time.mktime(expire_time)-time.time()
        
        #schedule a removal of the proxy file in this many seconds
        reactor.callLater(expires_in,self.authproxy[hostname].DestroyUserProxy,username) 
        
    def EnsureAuthedWithCredentials(self, hostname, username, cert, key, password):
        if hostname not in self.authproxy:
            # no!
            return self.AuthProxyUserWithCredentials(hostname,username,cert,key,password)
        else:
            # yes! lets see if we have a valid cert
            if not self.authproxy[hostname].IsProxyValid(username):
                return self.AuthProxyUserWithCredentials(hostname,username,cert,key,password)
            # else user is already authed
