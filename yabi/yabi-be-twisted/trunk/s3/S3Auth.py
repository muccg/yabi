# -*- coding: utf-8 -*-
"""Encapsulation of globus Authentication proxies as a mixin"""

from utils.stacklesstools import RetryGET, GETFailure, sleep
import json, os
from globus.Auth import NoCredentials, AuthException
from conf import config
import urllib

DEBUG = True

class S3Auth(object):
    
    def AuthProxyUser(self, yabiusername, scheme, username, hostname, path, *args):
        """Auth a user via getting the credentials from the json yabiadmin backend. When the credentials are gathered, successcallback is called with the deferred.
        The deferred should be the result channel your result will go back down"""
        useragent = "YabiFS/0.1"
        
        try:
            path = os.path.join(config.yabiadminpath,"ws/credential/%s/?uri=%s://%s@%s%s"%(yabiusername,scheme,username,hostname,urllib.quote(path)))
            host = config.yabiadminserver
            port = config.yabiadminport
            
            if DEBUG:
                print "S3Auth getting credential. Doing GET on path:",path
                print "host:",host
                print "port:",port
            
            status, message, data = RetryGET( path = path, host=host, port=port )
            
            assert status==200
            credentials = json.loads( data )
            
            return credentials
        
        except GETFailure, gf:
            gf_message = gf.args[0]
            #if gf_message[0]==-1:
                ## connection problems
                #raise AuthException( "Tried to get credentials from %s:%d and failed: %s"%(config.yabiadminserver,config.yabiadminport,gf_message[1]) )
            raise NoCredentials( "User: %s does not have credentials for this backend %s on host %s\n"%(username,scheme,hostname) )
