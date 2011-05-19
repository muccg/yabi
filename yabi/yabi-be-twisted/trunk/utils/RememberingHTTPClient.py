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

class RememberingHTTPClient(client.HTTPPageGetter):
    errordata=None
    
    def rawDataReceived(self, data):
        if int(self.status) != 200:
            # we got an error. TODO: something graceful here
            #print "ERROR. NON 200 CODE RETURNED FOR JOB EXEC STATUS"
            self.errordata=data
            #print "errordata",data
        return client.HTTPPageGetter.rawDataReceived(self,data)        

class RememberingHTTPClientFactory(client.HTTPClientFactory):
    protocol = RememberingHTTPClient
    
    def __init__(self, *args, **kwargs):
        self.connect_failed = kwargs['connect_failed']
        del kwargs['connect_failed']
        client.HTTPClientFactory.__init__(self,*args,**kwargs)
        
    
    def buildProtocol(self, addr):
        self.last_client = client.HTTPClientFactory.buildProtocol(self, addr)
        return self.last_client
    
    #def connectionLost(self, reason):
        #print "connectionLost",reason
        #return client.HTTPClientFactory.connectionLost(self, reason)
            
    #def clientConnectionLost(self, connector, reason):
        #print "clientConnectionLost",connector, reason
        #return client.HTTPClientFactory.clientConnectionLost(self, connector, reason)
  
    def clientConnectionFailed(self, connector, reason):
        print "clientConnectionFailed",connector, reason, self.connect_failed
        self.connect_failed[0]=reason
        print "Set to",self.connect_failed
        return client.HTTPClientFactory.clientConnectionFailed(self, connector, reason)

class RememberingHTTPPageGetter(client.HTTPPageGetter,RememberingHTTPClient):
    pass


class RememberingHTTPPageDownloader(client.HTTPPageDownloader,RememberingHTTPClient):
    pass

class RememberingHTTPDownloader(RememberingHTTPClientFactory):
    """Download to a file."""

    protocol = RememberingHTTPPageDownloader
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
        RememberingHTTPClientFactory.__init__(
            self, url, method=method, postdata=postdata, headers=headers,
            agent=agent, timeout=timeout, cookies=cookies,
            followRedirect=followRedirect, redirectLimit=redirectLimit)


    def gotHeaders(self, headers):
        RememberingHTTPClientFactory.gotHeaders(self, headers)
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
        
    def clientConnectionFailed(self, connector, reason):
        print "BAM"

