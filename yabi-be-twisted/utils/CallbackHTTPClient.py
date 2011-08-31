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
from twisted.web import client
from twisted.web.client import HTTPPageDownloader
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python import failure, log

import os, types

from conf import config

from stackless import tasklet

DEBUG = False

import hmac

HMAC_SECRET = config.config['backend']['hmacsecret']

def sign_uri(uri):
    hmac_digest = hmac.new(HMAC_SECRET)
    hmac_digest.update(uri)
    return hmac_digest.hexdigest()

class CallbackHTTPClient(client.HTTPPageGetter):
    def __init__(self, *args, **kwargs):
        self.callback = None
        self.errordata = None
    
    def SetCallback(self, callback):
        self.callback = callback
        
    def connectionMade(self):
        method = getattr(self.factory, 'method', 'GET')
        if DEBUG:
            print "METHOD:",method
            print "TRANSPORT",self.transport
        self.sendCommand(method, self.factory.path)
        if self.factory.scheme == 'http' and self.factory.port != 80:
            host = '%s:%s' % (self.factory.host, self.factory.port)
        elif self.factory.scheme == 'https' and self.factory.port != 443:
            host = '%s:%s' % (self.factory.host, self.factory.port)
        else:
            host = self.factory.host
        self.sendHeader('Host', self.factory.headers.get("host", host))
        self.sendHeader('User-Agent', self.factory.agent)
        self.sendHeader('Hmac-digest', sign_uri(self.factory.path))
        
        data = getattr(self.factory, 'postdata', None)
        if data is not None:
            self.sendHeader("Content-Length", str(len(data)))

        cookieData = []
        for (key, value) in self.factory.headers.items():
            if key.lower() not in self._specialHeaders:
                # we calculated it on our own
                self.sendHeader(key, value)
            if key.lower() == 'cookie':
                cookieData.append(value)
        for cookie, cookval in self.factory.cookies.items():
            cookieData.append('%s=%s' % (cookie, cookval))
        if cookieData:
            self.sendHeader('Cookie', '; '.join(cookieData))
        self.endHeaders()
        self.headers = {}

        if data is not None:
            self.transport.write(data)
    #def lineReceived(self, line):
        #print "LINE_RECEIVED:",line
        #return client.HTTPPageGetter.lineReceived(self,line)
    
    # ask for page as HTTP/1.1 so we get chunked response
    def sendCommand(self, command, path):
        self.transport.write('%s %s HTTP/1.0\r\n' % (command, path))
        
    # capture "connection:close" so we stay HTTP/1.1 keep alive!
    def sendHeader(self, name, value):
        if name.lower()=="connection" and value.lower()=="close":
            return 
        return client.HTTPPageGetter.sendHeader(self,name,value)
    
    def rawDataReceived(self, data):
        if int(self.status) != 200:
            # we got an error. TODO: something graceful here
            self.errordata=data
            
        elif self.callback:
            # hook in here to process chunked updates
            lines=data.split("\r\n")
            if DEBUG:
                print "LINES",[lines]
            #chunk_size = int(lines[0].split(';')[0],16)
            #chunk = lines[1]
            chunk = lines[0]
            
            #assert len(chunk)==chunk_size, "Chunked transfer decoding error. Chunk size mismatch"
            
            # run the callback in a tasklet!!! Stops scheduler getting into a looped blocking state
            reporter=tasklet(self.callback)
            reporter.setup(chunk)
            reporter.run()
            
        else:
            pass
        #print "RECV",data
        return client.HTTPPageGetter.rawDataReceived(self,data)

class CallbackHTTPPageGetter(client.HTTPPageGetter,CallbackHTTPClient):
    pass


class CallbackHTTPPageDownloader(client.HTTPPageDownloader,CallbackHTTPClient):
    pass


class CallbackHTTPClientFactory(client.HTTPClientFactory):
    protocol = CallbackHTTPClient
    
    def __init__(self, url, method='GET', postdata=None, headers=None,
                 agent="Twisted PageGetter", timeout=0, cookies=None,
                 followRedirect=True, redirectLimit=20, callback=None):
        self._callback=callback
        return client.HTTPClientFactory.__init__(self, url, method, postdata, headers, agent, timeout, cookies, followRedirect, redirectLimit)
    
    def buildProtocol(self, addr):
        #print "bp",addr
        p = client.HTTPClientFactory.buildProtocol(self, addr)
        p.SetCallback(self._callback)
        self.last_client = p
        return p

    def SetCallback(self, callback):
        self._callback=callback

class CallbackHTTPDownloader(CallbackHTTPClientFactory):
    """Download to a file."""

    protocol = CallbackHTTPPageDownloader
    value = None

    def __init__(self, url, fileOrName,
                 method='GET', postdata=None, headers=None,
                 agent="Twisted client", supportPartial=0,
                 timeout=0, cookies=None, followRedirect=1,
                 redirectLimit=20):
        self.requestedPartial = 0
        if isinstance(fileOrName, types.StringTypes):
            self.fileName = fileOrName
            self.file = None
            if supportPartial and os.path.exists(self.fileName):
                fileLength = os.path.getsize(self.fileName)
                if fileLength:
                    self.requestedPartial = fileLength
                    if headers == None:
                        headers = {}
                    headers["range"] = "bytes=%d-" % fileLength
        else:
            self.file = fileOrName
        CallbackHTTPClientFactory.__init__(
            self, url, method=method, postdata=postdata, headers=headers,
            agent=agent, timeout=timeout, cookies=cookies,
            followRedirect=followRedirect, redirectLimit=redirectLimit)


    def gotHeaders(self, headers):
        CallbackHTTPClientFactory.gotHeaders(self, headers)
        if self.requestedPartial:
            contentRange = headers.get("content-range", None)
            if not contentRange:
                # server doesn't support partial requests, oh well
                self.requestedPartial = 0
                return
            start, end, realLength = http.parseContentRange(contentRange[0])
            if start != self.requestedPartial:
                # server is acting wierdly
                self.requestedPartial = 0


    def openFile(self, partialContent):
        if partialContent:
            file = open(self.fileName, 'rb+')
            file.seek(0, 2)
        else:
            file = open(self.fileName, 'wb')
        return file

    def pageStart(self, partialContent):
        """Called on page download start.

        @param partialContent: tells us if the download is partial download we requested.
        """
        if partialContent and not self.requestedPartial:
            raise ValueError, "we shouldn't get partial content response if we didn't want it!"
        if self.waiting:
            try:
                if not self.file:
                    self.file = self.openFile(partialContent)
            except IOError:
                #raise
                self.deferred.errback(failure.Failure())

    def pagePart(self, data):
        if not self.file:
            return
        try:
            self.file.write(data)
        except IOError:
            #raise
            self.file = None
            self.deferred.errback(failure.Failure())
            

    def noPage(self, reason):
        """
        Close the storage file and errback the waiting L{Deferred} with the
        given reason.
        """
        if self.waiting:
            self.waiting = 0
            if self.file:
                try:
                    self.file.close()
                except:
                    log.err(None, "Error closing HTTPDownloader file")
            self.deferred.errback(reason)


    def pageEnd(self):
        self.waiting = 0
        if not self.file:
            return
        try:
            self.file.close()
        except IOError:
            self.deferred.errback(failure.Failure())
            return
        self.deferred.callback(self.value)

