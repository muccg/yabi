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

from debug import class_annotate

import stackless

def no_intr(func, *args, **kw):
    while True:
        try:
            return func(*args, **kw)
        except (OSError, IOError), e:
            if e.errno == errno.EINTR or e.errno == errno.EAGAIN:
                stackless.schedule()
            else:
                raise

import StringIO

@class_annotate
class MimeStreamDecoder(object):
    """This is my super no memory usage streaming Mime upload decoder"""
    
    def __init__(self):
        self.line_ending=None                   # the EOL characters
        self._carry = ""                        # for subsequent iterations, this is our carry, our unprocessed data
        self.fileopen = None                    # if we are presently writing the data to a file, this is the file
        self.boundary = None                    # the mime boundary market
        self._is_header = False                 # are we parsing a subfiles header?
        self.content_type = "None/None"
        self.bodyline=False
        
        self.datastream = None                  # for saving data segments (not files)
        self.datakeyname = None                 # save the keyname
        self.datavalues = {}                    # storage 
        
    def set_boundary(self, boundary):
        self.boundary = boundary
    
    def open_data_stream(self):
        self.datastream = StringIO.StringIO()
    
    def close_data_stream(self):
        #print "DATA",self.datakeyname,"=",self.datastream.getvalue()
        self.datavalues[self.datakeyname]=self.datastream.getvalue()
        self.datastream = None
    
    def open_write_stream(self, filename):
        """Override this to return the file like object"""
        self.fileopen = open(filename,'wb')
    
    def close_write_stream(self):
        """Override this to close the file like object"""
        self.fileopen.close()
        self.fileopen = None
        
    def write_line(self, line):
        no_intr(getattr(self.fileopen or self.datastream,"write"),line)
        
    def write_line_ending(self):
        if self.fileopen:
            self.fileopen.write(self.line_ending)
        else:
            self.datastream.write(self.line_ending)
    
    def guess_line_ending(self, data):
        """from a section of data, try and guess the line ending"""
        if "\r\n" in data:
            self.line_ending = "\r\n"
        elif "\n\r" in data:
            self.line_ending = "\n\r"
        elif "\r" in data:
            self.line_ending = "\r"
        elif "\n" in data:
            self.line_ending = "\n"
        else:
            self.line_ending = None
    
    def parse_content_disposition(self,line):
        parts = [X.strip() for X in line.split(";")]
        extra = {}
        for part in parts:
            if part.lower().startswith('content-disposition:'):
                assert part.endswith('form-data')
            else:
                if len(part):
                    key,value = part.split('=')
                    extra[key] = value if (value[0]!='"' and value[1]!='"') else value[1:-1]
        
        # open our file write handle
        if 'filename' not in extra:
            #data segment
            self.datakeyname = extra['name']
            self.open_data_stream()
        else:
            self.open_write_stream(extra['filename'])
        
    def parse_content_type(self,line):
        assert line.lower().startswith('content-type:')
        ctype = line.lower().split()[-1]
        self.content_type = ctype
    
    def feed(self,data):
        # try and guess the line ending if we don't know it yet
        if self.line_ending is None:
            self.guess_line_ending(data)
            
        # split our data on line ending if possible
        if self.line_ending is not None:
            lines = (self._carry + data).split(self.line_ending)
            
            for num,line in enumerate(lines[:-1]):
                # parse content
                if self.boundary in line:
                    bounds = line.split(self.boundary)
                    self.bodyline = False
                    assert False not in [X=='--' or X=='' for X in bounds], "Boundary in request is malformed"
                    bound_start, bound_end = [X=="--" for X in bounds]               # bound_end is true for last boundary
                    if not bound_end:
                        # we've got a new openning boundary
                        if self.fileopen:
                            # close the file. this is the inbetween boundary. another file is coming
                            self.close_write_stream()
                            self._is_header = True
                        elif self.datastream:
                            self.close_data_stream()
                            self._is_header = True
                        else:
                            # this is our first boundary
                            self._is_header = True
                    else:
                        # all the boundaries are written. close the stream
                        if self.fileopen:
                            # close the file. this is the inbetween boundary. another file is coming
                            self.close_write_stream()
                            self._is_header = True
                        elif self.datastream:
                            self.close_data_stream()
                            self._is_header = True
                else:
                    if self._is_header:
                        if line.lower().startswith('content-disposition:'):
                            self.parse_content_disposition(line)
                        elif line.lower().startswith('content-type:'):
                            self.parse_content_type(line)
                        elif not len(line):
                            # end of header is signified by blank line
                            self._is_header = False
                        else:
                            # error
                            raise Exception("Malformed MIME subcontent header section")
                        
                    else:
                        # file body
                        if self.bodyline:
                            self.write_line_ending()
                        self.write_line(line)
                        if num<len(lines)-1:
                            self.bodyline = True
                        
            self._carry = lines[-1]

def WaitForDeferredData(deferred):
    """Causes a stackless thread to wait until data is available on a deferred, then returns that data.
    If an errback chain is called, it raises an DeferredError exception with the contents as the error 
    passthrough (probably a Failure intsance)
    """
    if not isinstance(deferred,defer.Deferred):
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
        stackless.schedule()                  # sleep the thread until we are asked to continue
        
    if err[0]:
        raise DeferredError, err[0]
    
    return data[0]



@class_annotate
class ProxyClient(HTTPClient):
    """Used by ProxyClientFactory to implement a simple web proxy."""

    _finished = False

    def __init__(self, command, rest, version, headers, instream, father,factory):
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
            print "SEND HEADER",header,value
            if header=="Expect" and '100' in value[0] and 'continue' in value[0]:
                self.wait_for_continue = True
            if header!="Connection":
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
            print "Stream Finish"
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

@class_annotate
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

@class_annotate
class UploadClient(LineReceiver):
    """Used by UploadClientFactory to implement a simple upload web proxy."""
    def __init__(self, command, rest, version, headers, instream, backchannel,factory):
        print "UploadClient:",command,",",rest,",",version,",",instream,",",backchannel,",",factory
        
        self.backchannel = father
        self.command = command
        self.version = version
        self.rest = rest
        if headers.hasHeader("proxy-connection"):
            headers.removeHeader("proxy-connection")
        headers.setHeader("connection", "close")
        self.headers = headers
        self.instream = instream
        self.factory = factory
        
        # for sending back to our caller
        self.status = None
        self.backchannel = None
   
        self.remoteheaders = {}
        self.header_section = True      # are we in the headers section
   
        return
    
    def connectionMade(self):
        print "connectionMade"
        # send the query
        self.sendLine(self.command+" "+self.rest+" HTTP/%d.%d"%self.version)
        for header, value in self.headers.getAllRawHeaders():
            print "SEND HEADER",header,value
            if header=="Expect" and '100' in value[0] and 'continue' in value[0]:
                self.wait_for_continue = True
            if header!="Connection":
                self.sendLine(header+": "+value[0])
        self.sendLine("")
        
    def rawDataReceived(self, data):
        """Override this for when raw data is received.
        """
        print "rawDataReceived",data

    def lineReceived(self, line):
        """Override this for when each line is received.
        """
        print "lineReceived",line
        if line=="\r\n":
            self.header_section = False
    
    def dataReceived(self, data):
        print "dataReceived",data

    def connectionLost(self, reason=connectionDone):
        print "connectionLost",reason



@class_annotate
class UploadClientFactory(protocol.ClientFactory):
    """Used by ProxyRequest to implement a simple web proxy."""

    def __init__(self, command, rest, version, headers, stream, backchannel):
        self.backchannel = backchannel
        self.command = command
        self.rest = rest
        self.headers = headers
        self.stream = stream
        self.version = version


    def buildProtocol(self, addr):
        return UploadClient(self.command, self.rest, self.version,
                           self.headers, self.stream, self.backchannel,self)

    def clientConnectionFailed(self, connector, reason):
        err = "<H1>Could not connect</H1>"
        self.backchannel.callback(http.Response( responsecode.BAD_GATEWAY,  {'content-type': http_headers.MimeType('text', 'html')}, err ))


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
        
        if request.method == 'POST':
            ctype = request.headers.getHeader('content-type')
            print "content-type",ctype
            
            #result = http.Response( self.status[1],  self.forward_headers, self.stream ))
            backchannel = defer.Deferred()
            
            print "STREAM",request.stream
            print "request",dir(request)
            print "method",request.method
            print "headers",[str(x) for x in request.headers.getAllRawHeaders()]
            
            # start a stackless threadlet to pump upload proxy
            
            def upload_tasklet(req, channel):
                """Tasklet to do file upload"""
                ctype = req.headers.getHeader('content-type')
                assert ctype.mediaType == 'multipart' and ctype.mediaSubtype == 'form-data'
                boundary = ctype.params.get('boundary')
                if boundary is None:
                    return channel.callback( http.HTTPError( http.StatusResponse( responsecode.BAD_REQUEST, "Boundary not specified in Content-type.")))
                
                class MyMimeStreamDecoder(MimeStreamDecoder):
                    """Override the readers and writers to do HTTP file uploads to the remote proxy"""
                    pass
                
                parser = MyMimeStreamDecoder()
                parser.set_boundary(boundary)
                
                reader = req.stream.read()
                
                try:
                    while reader is not None:
                        dat = WaitForDeferredData(reader)
                        
                        # feed this data into the parser
                        parser.feed(dat)
                        
                        reader = req.stream.read()
                        stackless.schedule()
                except IOError, ioe:
                    return channel.callback( http.Response( responsecode.BAD_REQUEST, {'content-type':http_headers.MimeType('text','plain')}, "OK\n"))
                
            tl = stackless.tasklet(upload_tasklet)(request,backchannel)
                
            return backchannel
            
        else:
            backchannel = defer.Deferred()
        
            print "method",request.method
            print "headers",[str(x) for x in request.headers.getAllRawHeaders()]
            
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
