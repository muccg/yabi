#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import mimetypes
import os 
import email
import sys
import zipfile
import StringIO
from stat import *

import logging
logger = logging.getLogger('yabiadmin')


def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    logger.debug('')
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
    logger.debug('')
    #print "encode_multipart_formdata(",stream,",",fields,",",files,")"
    BOUNDARY = encode_multipart_make_boundary()
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        stream.send('--' + BOUNDARY + CRLF)
        stream.send('Content-Disposition: form-data; name="%s"' % key + CRLF)
        stream.send(CRLF)
        stream.send(value)
        stream.send(CRLF)
    for (key, filename, fullpath) in files:
        stream.send('--' + BOUNDARY + CRLF)
        stream.send('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
        stream.send('Content-Type: %s' % get_content_type(filename) + CRLF)
        stream.send(CRLF)
        
        fh=open(fullpath,'rb')
        while True:
            dat=fh.read(CHUNKSIZE)
            if len(dat)==0:
                break
            stream.send(dat)
        fh.close()
        
        stream.send(CRLF)
    stream.send('--' + BOUNDARY + '--' + CRLF)
    stream.send(CRLF)
    return
    
def encode_content_length(fields, files):
    #print "encode_content_length(",fields,",",files,")"
    BOUNDARY = encode_multipart_make_boundary()
    CRLF = '\r\n'
    length=0
    for (key, value) in fields:
        length+=len('--' + BOUNDARY + CRLF)
        length+=len('Content-Disposition: form-data; name="%s"' % key + CRLF)
        length+=len(CRLF)
        length+=len(value)
        length+=len(CRLF)
    for (key, filename, fullpath) in files:
        length+=len('--' + BOUNDARY + CRLF)
        length+=len('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
        length+=len('Content-Type: %s' % get_content_type(filename) + CRLF)
        length+=len(CRLF)
        length+=os.stat(fullpath)[ST_SIZE]
        length+=len(CRLF)
    length+=len('--' + BOUNDARY + '--' + CRLF)
    length+=len(CRLF)
    return length

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    

