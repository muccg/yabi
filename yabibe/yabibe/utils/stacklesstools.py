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
"""A suite of tools for using twisted with stackless python. Turns the twisted callback methods into
functions that block a stackless tasklet.
"""

from twisted.web import client
from twisted.web.client import HTTPPageDownloader
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

import urllib
import time
import json
import os, types

import gevent

from CallbackHTTPClient import CallbackHTTPClient, CallbackHTTPClientFactory, CallbackHTTPDownloader
from RememberingHTTPClient import RememberingHTTPClient, RememberingHTTPClientFactory, RememberingHTTPDownloader
from ServerContextFactory import ServerContextFactory

DEBUG = False

from conf import config

USER_AGENT = "YabiStackless/0.1"

## errors
class ConnectionFailure(Exception): pass
class GETFailure(ConnectionFailure): pass

class DeferredError(Exception): pass
class CloseConnections(Exception):
    """A special exception raised in tasklets by the engine shutdown.
    It closes all the open tcp connections associated with this tasklet and then retries the last event.
    """
    pass

def sleep(seconds):
    """Sleep the tasklet for this many seconds"""
    gevent.sleep(seconds)

import urllib

#
# A more abstract set of base classes for the stackless tools
#
class HTTPResponse(object):
    def __init__(self, status=None, message=None, data=None):
        self.status = status
        self.message = message
        self.data = data                # data could be the actual result, or a twistedweb2 stream
    
        self._isread = False
    
    def read(self):
        if self._isread:
            return ""
            
        self._isread = True
        return self.data
        
    @property
    def reason(self):
        return self.message
        
class HTTPConnection(object):
    scheme = 'https'
    PORT = 80
    
    def __init__(self, host, port=None):
        if ':' in host:
            self.host,self.port=host.split(':')
            self.port=int(self.port)
        else:
            self.host = host
            self.port = port or self.PORT
        
    def request(self, method, url, body=None, headers={}, noisy=False):
        """Issue the specified HTTP request"""
        fullpath = "%s://%s:%d%s"%(self.scheme,self.host,self.port,url)

        ascii_headers = {}
        for key,value in headers.iteritems():
            ascii_headers[key]=str(value)
        
        # switches to trigger the unblocking of the stackless thread
        self.get_complete = [False]
        self.get_failed = [False]
        self.connect_failed = [False]
        
        if DEBUG:
            print "HTTP:",fullpath
            print "AGENT:",USER_AGENT
            print "HEADERS:",ascii_headers
            print "HOST:",self.host
            print "PORT:",self.port
        
        factory = RememberingHTTPClientFactory( fullpath, method=method, agent=USER_AGENT, headers=ascii_headers, connect_failed = self.connect_failed)
        factory.noisy = noisy
        
        # now if the get fails for some reason. deal with it
        def _doFailure(data):
            if isinstance(data,Failure):
                exc = data.value
                #get_failed[0] = -1, str(exc), "Tried to GET %s"%(fullpath)
                self.get_failed[0] = -1, str(exc), "Tried to GET %s.\nRemote response was:\n%s"%(fullpath,factory.last_client.errordata)
            else:
                self.get_failed[0] = int(factory.status), factory.message, "Remote host %s:%d%s said: %s"%(host,port,path,factory.last_client.errordata)
            
        def _doSuccess(data):
            if DEBUG:
                print "SUCCESS:",factory.status,factory.message, data
            self.get_complete[0] = int(factory.status), factory.message, data
        
        # start the connection
        factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)
        if self.scheme == 'https':
            reactor.connectSSL(self.host, self.port, factory, ServerContextFactory())
        else:
            reactor.connectTCP(self.host, self.port, factory)

    def getresponse(self):
        # now we schedule this thread until the task is complete
        while not self.get_complete[0] and not self.get_failed[0]:
            gevent.sleep()
        
        if self.connect_failed[0]:
            if DEBUG:
                print "connect_failed=",self.connect_failed
            raise ConnectionFailure(self.connect_failed[0])
        
        if self.get_failed[0]:
            if DEBUG:
                print "get_failed=",self.get_failed
            if type(self.get_failed[0])==tuple and len(self.get_failed[0])==3:
                # failed naturally
                raise GETFailure(self.get_failed[0])
            elif self.get_failed[0]==True:
                # failed by tasklet serialisation and restoration
                raise GETFailed("Base stacklesstools HTTPConnection does not support tasklet deserialisation")
            else:
                #print "GETFailed=",get_failed
                assert False, "got unknown GET failure response"
        
        # create response
        return HTTPResponse( status=self.get_complete[0][0], message=self.get_complete[0][1], data=self.get_complete[0][2] )

#def GET(path, host=WS_HOST, port=WS_PORT, factory_class=CallbackHTTPClientFactory,**kws):
def GET(path, scheme=None, host=None, port=None, factory_class=RememberingHTTPClientFactory,**kws):
    """Stackless integrated twisted webclient GET
    Pass in the path to get and optionally the host and port
    raises a GETFailure exception on failure
    returns the return code and data on success 
    """
    # defaults to us
    if config.config['backend']['start_https']:
        # use https because its switched on
        host=host if host else config.config['backend']['sslport'][0] 
        host = "127.0.0.1" if host=="0.0.0.0" else host
        port=port if port else config.config['backend']['sslport'][1]
        scheme = scheme if scheme else "https"
    else:
        #use http
        host=host if host else config.config['backend']['port'][0]
        host = "127.0.0.1" if host=="0.0.0.0" else host
        port=port if port else config.config['backend']['port'][1]
        scheme = scheme if scheme else "http"

    getdata=urllib.urlencode(kws)
    
    if DEBUG:
        print "=>",str("%s://%s:%d%s"%(scheme,host,port,path+"?"+getdata))
        
    fullpath=str("%s://%s:%d%s"%(scheme,host,port,path))
    if getdata:
        fullpath += "?"+getdata
        
    # switches to trigger the unblocking of the stackless thread
    get_complete = [False]
    get_failed = [False]
    connect_failed = [False]
        
    factory = factory_class(
        fullpath,
        agent = USER_AGENT,
        connect_failed = connect_failed
        )
    factory.noisy=False
    
    if DEBUG:
        print "GETing",fullpath
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        if connect_failed[0]:
            return
        if isinstance(data,Failure):
            exc = data.value
            #get_failed[0] = -1, str(exc), "Tried to GET %s"%(fullpath)
            get_failed[0] = -1, str(exc), "Tried to GET %s.\nRemote response was:\n%s"%(fullpath,factory.last_client.errordata), int(factory.status)
        else:
            get_failed[0] = int(factory.status), factory.message, "Remote host %s:%d%s said: %s"%(host,port,path,factory.last_client.errordata)
        
    def _doSuccess(data):
        if DEBUG:
            print "SUCCESS:",factory.status,factory.message, data
        get_complete[0] = int(factory.status), factory.message, data
    
    # start the connection
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)
    if fullpath.startswith('https'):
        reactor.connectSSL(host, port, factory, ServerContextFactory())
    else:
        reactor.connectTCP(host, port, factory)

    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0] and not connect_failed[0]:
        if DEBUG:
            pass
            #print "G",get_complete[0],"G2",get_failed[0],"CF",connect_failed[0]
        # has out actual initial connection failed?
        gevent.sleep()
        
    if connect_failed[0]:
        if DEBUG:
            print "connect_failed=",connect_failed
        raise ConnectionFailure(connect_failed[0])
        
    if get_failed[0]:
        if DEBUG:
            print "get_failed=",get_failed
        if type(get_failed[0])==tuple and len(get_failed[0])==4:
            # failed naturally
            raise GETFailure(get_failed[0])
        elif get_failed[0]==True:
            # failed by tasklet serialisation and restoration
            return GET(path, host, port, factory_class, **kws)
        else:
            #print "GETFailed=",get_failed
            assert False, "got unknown GET failure response"
    
    return get_complete[0]

def POST(path,**kws):
    """Stackless integrated twisted webclient POST"""
    print "POST",path
    
    if 'scheme' in kws:
        scheme = kws['scheme']
        del kws['scheme']
    else:
        scheme = "https" if config.config['backend']['start_https'] else "http"
    
    if 'host' in kws:
        host = kws['host']
        del kws['host']
    else:
        if config.config['backend']['start_https']:
            # use https because its switched on
            host=config.config['backend']['sslport'][0] 
            host = "127.0.0.1" if host=="0.0.0.0" else host
            scheme = "https"
        else:
            #use http
            host=config.config['backend']['port'][0]
            host = "127.0.0.1" if host=="0.0.0.0" else host
            scheme = "http"

        
    if 'port' in kws:
        port = kws['port']
        del kws['port']
    else:
        if config.config['backend']['start_https']:
            # use https because its switched on
            port=config.config['backend']['sslport'][1]
        else:
            #use http
            port=config.config['backend']['port'][1]
        
    errorpage=[None]
        
    if 'datacallback' in kws:
        datacallback = kws['datacallback']
        del kws['datacallback']
    else:
        datacallback = None
    
    postdata=urllib.urlencode(kws)
    #postdata="src=gridftp1/cwellington/bi01/cwellington/test&dst=gridftp1/cwellington/bi01/cwellington/test2"
    
    fullpath=str("%s://%s:%d%s"%(scheme,host,port,path))
    
    if DEBUG:
        print "POST =>",fullpath
    
    factory = CallbackHTTPClientFactory(
        fullpath,
        agent = USER_AGENT,
        method="POST",
        postdata=postdata,
        headers={
            'Content-Type':"application/x-www-form-urlencoded",
            'Accept':'*/*',
            'Content-Length':"65"
            },
        callback=datacallback
        )
        
    factory.noisy=False
        
    get_complete = [False]
    get_failed = [False]
    connect_failed = [False]
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        if isinstance(data,Failure):
            exc = data.value
            get_failed[0] = -1, str(exc), "Tried to POST %s to %s.\nRemote response was:\n%s"%(postdata,str("https://%s:%d%s"%(host,port,path)),factory.last_client.errordata)
        else:
            get_failed[0] = int(factory.status), factory.message, "Remote host %s:%d%s said: %s"%(host,port,path,factory.last_client.errordata)
    
    def _doSuccess(data):
        #print "Post success"
        get_complete[0] = int(factory.status), factory.message, data
        
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)

    if fullpath.startswith('https'):
        reactor.connectSSL(host, port, factory, ServerContextFactory())
    else:
        reactor.connectTCP(host, port, factory)
    
    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0] and not connect_failed[0]:
        gevent.sleep()

    if connect_failed[0]:
        if DEBUG:
            print "connect_failed=",connect_failed
        raise ConnectionFailure(connect_failed[0])
        
    if get_failed[0]:
        if type(get_failed[0])==tuple and len(get_failed[0])==3:
            # failed naturally
            raise GETFailure(get_failed[0])
        elif get_failed[0]:
            # failed by tasklet serialisation and restoration
            return POST(path, host=host, port=port, datacallback=datacallback, **kws)
        else:
            #print "POSTFailed=",get_failed
            assert False, "got unknown POST failure response"
    
    return get_complete[0]


def WaitForDeferredData(deferred):
    """Causes a stackless thread to wait until data is available on a deferred, then returns that data.
    If an errback chain is called, it raises an DeferredError exception with the contents as the error 
    passthrough (probably a Failure intsance)
    """
    if not isinstance(deferred,Deferred):
        return deferred
    
    cont = [False]                  # continue?
    data = [None]                   # data that we will be passed and will pass on
    err = [None]                    # the failure if errbacks are called
    
    def _cont(dat):
        cont[0] = True              # unblock
        data[0] = dat               # pass out the data
        return True
        
    def _err(dat):
        cont[0] = True
        err[0] = dat
        return False
        
    deferred.addCallback(_cont)     # trigger our callback on data
    
    while not cont[0]:
        gevent.sleep()                  # sleep the thread until we are asked to continue
        
    if err[0]:
        raise DeferredError, err[0]
    
    return data[0]

def AdminBackoffSchedule():
    """Generator that generates the various delays to wait between retries when admin fails"""
    delay = 1.0
    while delay<300.0:                      # 5 minutes
        yield delay
        delay*=2
    while True:                             # retry forever
        yield 300.0
        
def RetryCall(call, *args, **kwargs):
    delays = AdminBackoffSchedule()
    while True:
        try:
            return call(*args, **kwargs)
        except ConnectionFailure, cf:
            # the connection is refused. Definately retry
            print "Connection attempt failed",cf[0],"retrying"
            try:
                sleep(delays.next())
            except StopIteration:
                raise cf
        
# two curried functions
RetryPOST = lambda *a,**b: RetryCall(POST,*a,**b)
RetryGET = lambda *a,**b: RetryCall(GET,*a,**b)