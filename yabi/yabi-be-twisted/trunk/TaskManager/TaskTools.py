"""All these funcs are done in a blocking manner using a stackless aproach. Not your normal funcs"""

from stackless import schedule, tasklet
from twisted.web import client
from twisted.internet import reactor
import time
import json

COPY_RETRY = 3
COPY_PATH = "/fs/copy"
LIST_PATH = "/fs/ls"
EXEC_PATH = "/exec/%(backend)s/%(username)s"
MKDIR_PATH = "/fs/mkdir"

WS_HOST, WS_PORT = "localhost",8000
USER_AGENT = "YabiStackless/0.1"

def encode_multipart_formdata(fields={}, files=[], content_type='application/octet-stream'):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    content_type is the contentype to send
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields.iteritems():
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(str(value))
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s";filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % content_type)
        L.append('')
        L.append(str(value))
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


class CallbackHTTPClient(client.HTTPPageGetter):
    callback = None
    
    def SetCallback(self, callback):
        self.callback = callback
    
    #def lineReceived(self, line):
        #print "LINE_RECEIVED:",line
        #return client.HTTPPageGetter.lineReceived(self,line)
    
    # ask for page as HTTP/1.1 so we get chunked response
    def sendCommand(self, command, path):
        self.transport.write('%s %s HTTP/1.1\r\n' % (command, path))
        
    # capture "connection:close" so we stay HTTP/1.1 keep alive!
    def sendHeader(self, name, value):
        if name.lower()=="connection" and value.lower()=="close":
            return
        return client.HTTPPageGetter.sendHeader(self,name,value)
    
    def rawDataReceived(self, data):
        if self.callback:
            print "CALLING CALLBACK",self.callback
            # hook in here to process chunked updates
            lines=data.split("\r\n")
            chunk_size = int(lines[0].split(';')[0],16)
            chunk = lines[1]
            
            assert len(chunk)==chunk_size, "Chunked transfer decoding error. Chunk size mismatch"
            
            # run the callback in a tasklet!!! Stops scheduler getting into a looped blocking state
            reporter=tasklet(self.callback)
            reporter.setup(chunk)
            reporter.run()
            
        else:
            print "NO CALLBACK"
        return client.HTTPPageGetter.rawDataReceived(self,data)

class CallbackHTTPClientFactory(client.HTTPClientFactory):
    protocol = CallbackHTTPClient
    
    def __init__(self, url, method='GET', postdata=None, headers=None,
                 agent="Twisted PageGetter", timeout=0, cookies=None,
                 followRedirect=True, redirectLimit=20, callback=None):
        self._callback=callback
        return client.HTTPClientFactory.__init__(self, url, method, postdata, headers, agent, timeout, cookies, followRedirect, redirectLimit)
    
    def buildProtocol(self, addr):
        p = client.HTTPClientFactory.buildProtocol(self, addr)
        p.SetCallback(self._callback)
        return p

    def SetCallback(self, callback):
        self._callback=callback


class GetFailure(Exception):
    pass

def Get(path, host=WS_HOST, port=WS_PORT, factory_class=client.HTTPClientFactory):
    """Stackless integrated twisted webclient"""
    factory = factory_class(
        "http://%s:%d%s"%(host,port,path),
        agent = USER_AGENT
        )
    reactor.connectTCP(host, port, factory)
    
    get_complete = [False]
    get_failed = [False]
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        print "Failed:",factory,":",type(data),data.__class__
        print data
        get_failed[0] = "Copy failed"
    
    def _doSuccess(data):
        print "success"
        get_complete[0] = data
        
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)
    
    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0]:
        schedule()
        
    if get_failed[0]:
        raise GetFailure(get_failed[0])
    
    return get_complete[0]

import urllib
def Post(path,**kws):
    """Stackless integrated twisted webclient"""
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
        
    reactor.connectTCP(host, port, factory)
    
    get_complete = [False]
    get_failed = [False]
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        #print "Failed:",factory,":",type(data),data.__class__
        get_failed[0] = "Copy failed... "+data.value.response
    
    def _doSuccess(data):
        #print "success"
        get_complete[0] = data
        
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)
    
    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0]:
        schedule()
        
    if get_failed[0]:
        raise GetFailure(get_failed[0])
    
    return get_complete[0]

def Sleep(seconds):
    """sleep tasklet for this many seconds. seconds is a float"""
    now = time.time()
    then = now+seconds
    while time.time()<then:
        schedule()

def Copy(src,dst,retry=COPY_RETRY):
    """Copy src (url) to dst (url) using the fileservice"""
    print "Copying %s to %s"%(src,dst)
    for num in range(retry):
        try:
            Post(COPY_PATH,src=src,dst=dst)
            # success!
            return True
        except GetFailure, err:
            print "Copy failed with error:",err
            Sleep(5.0)
    raise err
    
def List(path,recurse=False):
    #print "posting",LIST_PATH,path,recurse
    data = Post(LIST_PATH,dir=path,recurse=recurse)
    #print "LIST:",data
    return json.loads(data)

def Mkdir(path):
    return Post(MKDIR_PATH,dir=path)

     
def Log(logpath,message):
    """Report an error to the webservice"""
    print "Reporting error to %s"%(logpath)
    Post(logpath, message=message)              # error exception should bubble up and be caught
    
def Status(statuspath, message):
    """Report some status to the webservice"""
    print "Reporting status to %s"%(statuspath)
    Post(statuspath, status=message)              # error exception should bubble up and be caught
    
def Exec(backend, username, command, callbackfunc=None, **kwargs):
    # setup the status callback
    Post(EXEC_PATH%{'backend':backend, 'username':username}, command=command, datacallback=callbackfunc, **kwargs )
    