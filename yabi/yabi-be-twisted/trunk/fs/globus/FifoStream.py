import copy, os, types, sys
from zope.interface import Interface, Attribute, implements
from twisted.internet.defer import Deferred
from twisted.internet import interfaces as ti_interfaces, defer, reactor, protocol, error as ti_error
from twisted.python import components, log
from twisted.python.failure import Failure
from twisted.web2.stream import SimpleStream, ISendfileableStream

class FifoStream(SimpleStream):
    implements(ISendfileableStream)
    """A stream that reads data from a fifo"""
    CHUNK_SIZE = 2 ** 2 ** 2 ** 2 - 32

    f = None
    def __init__(self, f, length=None):
        """
        Create the stream from file handle f. If you set length, will be closed when length is reached
        
        prebuffer is something to stream our prior to the actual stream
        """
        self.f = f
        self.prebuffer = ''
        self.length = length
        
    def prepush(self, data):
        self.prebuffer+=data
        
    def read(self, sendfile=False):
        if self.f is None:
            return None

        length = self.length
        if length == 0:
            self.f = None
            return None

        # Fall back to standard read
        if length:
            readSize = min(length, self.CHUNK_SIZE)
        else:
            readSize = self.CHUNK_SIZE

        b = self.prebuffer+self.f.read(readSize)
        self.prebuffer=''
        bytesRead = len(b)
        if not bytesRead:
            if length:
                raise RuntimeError("Ran out of data reading file %r, expected %d more bytes" % (self.f, length))
            else:
                # has the process errored on us
                return None
        else:
            if self.length:
                self.length -= bytesRead
            return b

    def close(self):
        self.f = None
        SimpleStream.close(self)