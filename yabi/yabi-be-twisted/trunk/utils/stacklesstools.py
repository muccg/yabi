"""A suite of tools for using twisted with stackless python. Turns the twisted callback methods into
functions that block a stackless tasklet.
"""

from twisted.web import client
from twisted.internet import reactor
from twisted.internet.defer import Deferred

import urllib
import time
import json
import os

from stackless import schedule, tasklet

WS_HOST, WS_PORT = "localhost",8000
USER_AGENT = "YabiStackless/0.1"

## errors
class GETFailure(Exception): pass
class DeferredError(Exception): pass

def sleep(seconds):
    """Sleep the tasklet for this many seconds"""
    wakeup = time.time()+seconds
    while time.time()<wakeup:
        schedule()

def GET(path, host=WS_HOST, port=WS_PORT, factory_class=client.HTTPClientFactory):
    """Stackless integrated twisted webclient GET
    Pass in the path to get and optionally the host and port
    raises a GETFailure exception on failure
    returns the return code and data on success 
    """
    factory = factory_class(
        "http://%s:%d%s"%(host,port,path),
        agent = USER_AGENT
        )
    
    # switches to trigger the unblocking of the stackless thread
    get_complete = [False]
    get_failed = [False]
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        print "Failed:",factory,":",type(data),data.__class__
        print data
        get_failed[0] = "GET failed"
    
    def _doSuccess(data):
        get_complete[0] = int(factory.status), factory.message, data
    
    # start the connection
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)
    reactor.connectTCP(host, port, factory)

    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0]:
        schedule()
        
    if get_failed[0]:
        raise GETFailure(get_failed[0])
    
    return get_complete[0]

def POST(path,**kws):
    """Stackless integrated twisted webclient POST"""
    if 'host' in kws:
        host = kws['host']
        del kws['host']
    else:
        host = WS_HOST
        
    if 'port' in kws:
        port = kws['port']
        del kws['port']
    else:
        port = WS_PORT
        
    if 'datacallback' in kws:
        datacallback = kws['datacallback']
        del kws['datacallback']
    else:
        datacallback = None
    
    postdata=urllib.urlencode(kws)
    #postdata="src=gridftp1/cwellington/bi01/cwellington/test&dst=gridftp1/cwellington/bi01/cwellington/test2"
    print "POST DATA:",postdata
    
    if datacallback:
        factory = CallbackHTTPClientFactory(
            str("http://%s:%d%s"%(host,port,path)),
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
    else:
        factory = client.HTTPClientFactory(
            str("http://%s:%d%s"%(host,port,path)),
            agent = USER_AGENT,
            method="POST",
            postdata=postdata,
            headers={
                'Content-Type':"application/x-www-form-urlencoded",
                'Accept':'*/*',
                'Content-Length':"65"
                },
            )
        
    get_complete = [False]
    get_failed = [False]
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        print "Post Failed:",factory,":",type(data),data.__class__
        get_failed[0] = "Copy failed... "+data.value.response
    
    def _doSuccess(data):
        print "Post success"
        get_complete[0] = data
        
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)

    reactor.connectTCP(host, port, factory)
    
    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0]:
        schedule()
        
    if get_failed[0]:
        raise GetFailure(get_failed[0])
    
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
        schedule()                  # sleep the thread until we are asked to continue
        
    if err[0]:
        raise DeferredError, err[0]
    
    return data[0]
    