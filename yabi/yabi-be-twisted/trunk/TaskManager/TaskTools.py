"""All these funcs are done in a blocking manner using a stackless aproach. Not your normal funcs"""

from stackless import schedule
from twisted.web import client
from twisted.internet import reactor
import time

COPY_RETRY = 3
COPY_PATH = "/fs/copy"
COPY_HOST, COPY_PORT = "localhost",8000
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





class GetFailure(Exception):
    pass

def Get(host,port,path):
    """Stackless integrated twisted webclient"""
    factory = client.HTTPClientFactory(
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
        
    if get_failed:
        raise GetFailure(get_failed[0])
    
    return get_complete[0]

import urllib
def Post(host,port,path,**kws):
    """Stackless integrated twisted webclient"""
    postdata=urllib.urlencode(kws)
    #postdata="src=gridftp1/cwellington/bi01/cwellington/test&dst=gridftp1/cwellington/bi01/cwellington/test2"
    print "POST DATA:",postdata
    
    factory = client.HTTPClientFactory(
        "http://%s:%d%s"%(host,port,path),
        agent = USER_AGENT,
        method="POST",
        postdata=postdata,
        headers={
            'Content-Type':"application/x-www-form-urlencoded;charset=utf-8"
            }
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
        
    if get_failed:
        raise GetFailure(get_failed[0])
    
    return get_complete[0]


def Sleep(seconds):
    """sleep tasklet for this many seconds. seconds is a float"""
    now = time.time()
    then = now+seconds
    while time.time()<then:
        schedule()

def Copy(src,dst):
    """Copy src (url) to dst (url) using the fileservice"""
    print "Copying %s to %s"%(src,dst)
    for num in range(COPY_RETRY):
        try:
            Post(COPY_HOST,COPY_PORT,COPY_PATH,src=src,dst=dst)
            # success!
            return True
        except GetFailure, err:
            print "Copy failed with error:",err
            Sleep(5.0)
    return False