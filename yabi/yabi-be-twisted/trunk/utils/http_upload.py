#!/usr/bin/env python

"""http upload functions for testing yabi backend"""

import httplib
import mimetypes
import os 
import email
import sys
import StringIO
from stat import *

from stackless import schedule
import urllib 
from utils.stacklesstools import CallbackHTTPClientFactory, USER_AGENT

from twisted.web import client
from twisted.web.client import HTTPPageDownloader
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

def POST_upload(path,filelist,**kws):
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
        
    errorpage=[None]
        
    if 'datacallback' in kws:
        datacallback = kws['datacallback']
        del kws['datacallback']
    else:
        datacallback = None
        
    # encode an upload
    import StringIO
    data = StringIO.StringIO()
    data.send = data.write                      # make it behave like a socket
    encode_multipart_formdata(data,{},filelist)
            
    
    postdata=urllib.urlencode(kws)
    #postdata="src=gridftp1/cwellington/bi01/cwellington/test&dst=gridftp1/cwellington/bi01/cwellington/test2"
    #print "POST DATA:",postdata
    
    print postdata
    print str(encode_content_length(kws,filelist))
    
    factory = CallbackHTTPClientFactory(
        str("http://%s:%d%s"%(host,port,path)),
        agent = USER_AGENT,
        method="POST",
        postdata=postdata,
        headers={
            'Content-Type':encode_multipart_content_type(),
            'Accept':'*/*',
            'Content-Length':str(encode_content_length(kws,filelist))
            },
        callback=datacallback
        )
        
    factory.noisy=True
        
    get_complete = [False]
    get_failed = [False]
    
    # now if the get fails for some reason. deal with it
    def _doFailure(data):
        if isinstance(data,Failure):
            exc = data.value
            get_failed[0] = -1, str(exc), None
        else:
            get_failed[0] = int(factory.status), factory.message, "Remote host %s:%d%s said: %s"%(host,port,path,factory.last_client.errordata)
    
    def _doSuccess(data):
        #print "Post success"
        get_complete[0] = int(factory.status), factory.message, data
        
    factory.deferred.addCallback(_doSuccess).addErrback(_doFailure)

    reactor.connectTCP(host, port, factory)
    
    # now we schedule this thread until the task is complete
    while not get_complete[0] and not get_failed[0]:
        #print "P"
        schedule()
        
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


def post_multipart(host, selector, fields, files):
	"""
	Post fields and files to an http host as multipart/form-data.
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return the server's response page.
	"""
	print "post_multipart"
	content_type=encode_multipart_content_type()
	h = httplib.HTTP(host)
	h.putrequest('POST', selector)
	h.putheader('content-type', content_type)
	h.putheader('content-length', str(encode_content_length(fields, files)))
	h.endheaders()
	encode_multipart_formdata(h,fields, files)
	#h.send(body)
	#errcode, errmsg, headers = h.getreply()
	return h
	#return h.file.read()


def encode_multipart_make_boundary():
	return '----------ThIs_Is_tHe_bouNdaRY_$'

def encode_multipart_content_type():
	return 'multipart/form-data; boundary=%s' % encode_multipart_make_boundary()

CHUNKSIZE=8192

def encode_multipart_formdata(stream,fields, files):
	"""
	fields is a sequence of (name, value) elements for regular form fields.
	files is a sequence of (name, filename, value) elements for data to be uploaded as files
	Return (content_type, body) ready for httplib.HTTP instance
	"""
	print "encode_multipart_formdata(",stream,",",fields,",",files,")"
	BOUNDARY = encode_multipart_make_boundary()
	CRLF = '\r\n'
	for (key, value) in fields:
		stream.send('--' + BOUNDARY + CRLF)
		stream.send('Content-Disposition: form-data; name="%s"' % key + CRLF)
		stream.send(CRLF)
		stream.send(value)
		stream.send(CRLF)
	for (key, filename, data) in files:
		stream.send('--' + BOUNDARY + CRLF)
		stream.send('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
		stream.send('Content-Type: %s' % get_content_type(filename) + CRLF)
		stream.send(CRLF)
		
		stream.send(data)
		
		stream.send(CRLF)
	stream.send('--' + BOUNDARY + '--' + CRLF)
	stream.send(CRLF)
	return
	
def encode_content_length(fields, files):
	print "encode_content_length(",fields,",",files,")"
	BOUNDARY = encode_multipart_make_boundary()
	CRLF = '\r\n'
	length=0
	for (key, value) in fields:
		length+=len('--' + BOUNDARY + CRLF)
		length+=len('Content-Disposition: form-data; name="%s"' % key + CRLF)
		length+=len(CRLF)
		length+=len(value)
		length+=len(CRLF)
	for (key, filename, data) in files:
		length+=len('--' + BOUNDARY + CRLF)
		length+=len('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
		length+=len('Content-Type: %s' % get_content_type(filename) + CRLF)
		length+=len(CRLF)
		length+=len(data)
		length+=len(CRLF)
	length+=len('--' + BOUNDARY + '--' + CRLF)
	length+=len(CRLF)
	return length

def get_content_type(filename):
	return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
