# -*- coding: utf-8 -*-

# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.


"""Simplistic HTTP proxy support.

This comes in two main variants - the Proxy and the ReverseProxy.

When a Proxy is in use, a browser trying to connect to a server (say,
www.yahoo.com) will be intercepted by the Proxy, and the proxy will covertly
connect to the server, and return the result.

When a ReverseProxy is in use, the client connects directly to the ReverseProxy
(say, www.yahoo.com) which farms off the request to one of a pool of servers,
and returns the result.

Normally, a Proxy is used on the client end of an Internet connection, while a
ReverseProxy is used on the server end.
"""

# twisted imports
from twisted.web2 import client, http, responsecode, http_headers
from twisted.web2.client.http import HTTPClientProtocol
from twisted.internet import reactor, protocol
from twisted.web2 import resource, server
from zope.interface import implements, Interface
from twisted.web2.channel.http import HTTPChannel
from twisted.web2.iweb import IResource
from twisted.internet import defer

# system imports
import urlparse

# web1 imports
from twisted.web.http import HTTPClient
from twisted.protocols.basic import LineReceiver

from twisted.web2.stream import SimpleStream, ISendfileableStream, ProducerStream
from twisted.web2.http_headers import Headers

def method_decorator(class_declaration):
    class NewClass():
        pass
    for key in class_declaration.__dict__:
        if hasattr(class_declaration.__dict__[key], '__call__'):
            def new_method(*args, **kwargs):
                print str(dir()) #Replace this with your code.
                class_declaration.__dict__[key](*args, **kwargs)
            setattr(NewClass, str(key), new_method)
    return NewClass
 
@method_decorator
class ProxyClient(HTTPClientProtocol,HTTPClient):
    """Used by ProxyClientFactory to implement a simple web proxy."""

    def __init__(self, command, rest, version, headers, instream, father,factory):
        HTTPClientProtocol.__init__(self)
        
        print "ProxyClient:",command,",",rest,",",version,",",instream,",",father
        
        self.father = father
        self.command = command
        self.rest = rest
        if headers.hasHeader("proxy-connection"):
            headers.removeHeader("proxy-connection")
        headers.setHeader("connection", "close")
        self.headers = headers
        self.instream = instream
        self.factory = factory
        
        # for sending back to our caller
        self.forward_headers = Headers()
        self.status = None
        self.backchannel = None
        self.stream = ProducerStream()          #ProxyStream()
        
        self.wait_for_continue = False          # for uploads, wait for "100 COntinue" flag

    def connectionMade(self):
        print "CONNECTION MADE"
        print self.command
        print self.rest
        
        self.sendCommand(self.command, self.rest)
        for header, value in self.headers.getAllRawHeaders():
            if value==['c, l, o, s, e']:
                value = ['close']
            print "SEND HEADER",header,value
            if header=="Expect" and '100' in value[0] and 'continue' in value[0]:
                self.wait_for_continue = True
            self.sendHeader(header, value)
        self.endHeaders()   
        
        
    def dummy_(self):
        # now lets copy any instream down the pipola!
        reader = self.instream.read()
        print "Reader:",reader
        
        if reader:
            def _data_in(data):
                print "_data_in",data
                self.transport.write(data)
                
                next = self.instream.read()
                print "reader is now",next
                
                if next:
                    next.addCallback(_data_in)
                #else:
                    #self.endHeaders()
                
            reader.addCallback(_data_in)
        else:
            self.endHeaders()
        
        #stream = defer.Deferred()
        #self.father.callback(http.Response( 200,  {}, stream ))
        
        #stream.callback("this ")
        #stream.callback("is a test")
    def dataReceived(self, data):
        print "dataReceived",data
        return LineReceiver.dataReceived(self,data)
        
    def lineReceived(self, line):
        print "LR:",line
        return HTTPClient.lineReceived(self,line)

    def rawDataReceived(self, data):
        print "RDR:",data
        print data
        return HTTPClient.rawDataReceived(self,data)

    def handleStatus(self, version, code, message):
        print "handleStatus",version,code,message
        self.status = version,code,message
        #return HTTPPageGetter.handleStatus(self,version,code,message)

    def handleHeader(self, key, value):
        print "handleHeader",key,value
        self.forward_headers.setRawHeaders(key,[value])
        #return HTTPPageGetter.handleHeader(self,key,value)

    def handleEndHeaders(self):
        print "handleEndHeaders",self.forward_headers
        # start out back connection with our response
        self.father.callback(http.Response( self.status[1],  self.forward_headers, self.stream ))
        #return HTTPPageGetter.handleEndHeaders(self)
    
    def handleResponsePart(self, buffer):
        print "handleResponsePart",len(buffer)
        self.stream.write(buffer)
        return HTTPClient.handleResponsePart(self,buffer)

    def handleResponseEnd(self):
        print "handleResponseEnd"
        if not self.wait_for_continue:
            self.stream.finish()
            return HTTPClient.handleResponseEnd(self)
        else:
            print "Continue?"
            
        
        
    def handleResponse(self,buff):
        print "handleResponse()"

    def connectionLost(self, reason):
        return HTTPClient.connectionLost(self, reason)
        print "connectionLost",reason
        self.stream.close()

class ProxyClientFactory(protocol.ClientFactory):
    """Used by ProxyRequest to implement a simple web proxy."""

    def __init__(self, command, rest, version, headers, stream, backchannel):
        self.backchannel = backchannel
        self.command = command
        self.rest = rest
        self.headers = headers
        self.stream = stream
        self.version = version


    def buildProtocol(self, addr):
        return ProxyClient(self.command, self.rest, self.version,
                           self.headers, self.stream, self.backchannel,self)

    def clientConnectionFailed(self, connector, reason):
        err = "<H1>Could not connect</H1>"
        self.backchannel.callback(http.Response( responsecode.BAD_GATEWAY,  {'content-type': http_headers.MimeType('text', 'html')}, err ))



class ProxyRequest(http.Request):
    """Used by Proxy to implement a simple web proxy."""

    protocols = {'http': ProxyClientFactory}
    ports = {'http': 80}

    def process(self):
        parsed = urlparse.urlparse(self.uri)
        protocol = parsed[0]
        host = parsed[1]
        port = self.ports[protocol]
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        rest = urlparse.urlunparse(('','')+parsed[2:])
        if not rest:
            rest = rest+'/'
        class_ = self.protocols[protocol]
        headers = self.getAllHeaders().copy()
        if not headers.has_key('host'):
            headers['host'] = host
        self.content.seek(0, 0)
        s = self.content.read()
        clientFactory = class_(self.method, rest, self.clientproto, headers,
                               s, self)
        reactor.connectTCP(host, port, clientFactory)


class Proxy(HTTPChannel):
    """This class implements a simple web proxy.

    Since it inherits from twisted.protocols.http.HTTPChannel, to use it you
    should do something like this::

        from twisted.web2 import http
        f = http.HTTPFactory()
        f.protocol = Proxy

    Make the HTTPFactory a listener on a port as per usual, and you have
    a fully-functioning web proxy!
    """

    requestFactory = ProxyRequest


class ReverseProxyRequest(http.Request):
    """Used by ReverseProxy to implement a simple reverse proxy."""

    def process(self):
        self.received_headers['host'] = self.factory.host
        clientFactory = ProxyClientFactory(self.method, self.uri,
                                            self.clientproto,
                                            self.getAllHeaders(), 
                                            self.content.read(), self)
        reactor.connectTCP(self.factory.host, self.factory.port,
                           clientFactory)

class ReverseProxy(HTTPChannel):
    """Implements a simple reverse proxy.

    For details of usage, see the file examples/proxy.py"""

    requestFactory = ReverseProxyRequest

class IConnector(Interface):
    """attribute name"""
    def connect(factory):
        """connect ClientFactory"""

class TCPConnector:
    implements(IConnector)
    def __init__(self, host, port):
        self.host = host
        self.name = host
        self.port = port
    def connect(self, factory):
        reactor.connectTCP(self.host, self.port, factory)


class UNIXConnector:
    implements(IConnector)
    name = 'n/a'
    def __init__(self, socket):
        self.socket = socket
    def connect(self, factory):
        reactor.connectUNIX(self.socket, factory)


def ReverseProxyResource(host, port, path):
    return ReverseProxyResourceConnector(TCPConnector(host, port), path)

class ReverseProxyResourceConnector(object):
    """Resource that renders the results gotten from another server

    Put this resource in the tree to cause everything below it to be relayed
    to a different server.
    """
    isLeaf = True
    implements(IResource)

    def __init__(self, connector, path):
        self.connector = connector
        self.path = path

    def locateChild(self,request,segments):
        print "locateChild",request,",",segments
        return self, server.StopTraversal

    def renderHTTP(self,request):
        print "request:",dir(request)
        print "CONN:",self.connector.name
        
        request.headers.setHeader('host',self.connector.name)
        
        qs = urlparse.urlparse(request.uri)[4]
        path = self.path+'/'.join(request.postpath)
        if qs:
            rest = path + '?' + qs
        else:
            rest = path
            
        print "path=",path
        print "rest=",rest
        
        backchannel = defer.Deferred()
        
        print "method",request.method
        print "headers",[str(x) for x in request.headers.getAllRawHeaders()]
        
        if request.method == 'POST':
            ctype = request.headers.getHeader('content-type')
            print "content-type",ctype
            
            print "STREAM",request.stream
            
            clientFactory = ProxyClientFactory(request.method, rest, 
                                        request.clientproto, 
                                        request.headers,
                                        request.stream,
                                        backchannel)
            self.connector.connect(clientFactory)
        else:
            clientFactory = ProxyClientFactory(request.method, rest, 
                                        request.clientproto, 
                                        request.headers,
                                        request.stream,
                                        backchannel)
            self.connector.connect(clientFactory)
        
        return backchannel

    def prender(self, request):
        print "RPRC::render()"
        request.received_headers['host'] = self.connector.name
        request.content.seek(0, 0)
        qs = urlparse.urlparse(request.uri)[4]
        path = self.path+'/'.join(request.postpath)
        if qs:
            rest = path + '?' + qs
        else:
            rest = path
        clientFactory = ProxyClientFactory(request.method, rest, 
                                     request.clientproto, 
                                     request.getAllHeaders(),
                                     request.content.read(),
                                     request)
        self.connector.connect(clientFactory)
        return server.NOT_DONE_YET
