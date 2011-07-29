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
import copy, os, types, sys
from zope.interface import Interface, Attribute, implements
from twisted.internet.defer import Deferred
from twisted.internet import interfaces as ti_interfaces, defer, reactor, protocol, error as ti_error
from twisted.python import components, log
from twisted.python.failure import Failure
from twisted.web2.stream import SimpleStream, ISendfileableStream
import errno

class FifoStream(SimpleStream):
    implements(ISendfileableStream)
    """A stream that reads data from a fifo"""
    CHUNK_SIZE = 2 ** 2 ** 2 ** 2 - 32

    f = None
    def __init__(self, f, length=None, truncate=None):
        """
        Create the stream from file handle f. If you set length, will be closed when length is reached
        
        prebuffer is something to stream our prior to the actual stream
        """
        self.f = f
        self.prebuffer = ''
        self.length = length
        self.truncate = truncate            # truncate at this many bytes without warning or error
        
    def prepush(self, data):
        self.prebuffer+=data
        
    def read(self, sendfile=False):
        #print "read()",self.length,self.truncate
        
        if self.f is None:
            return None

        length = self.length
        if length == 0:
            self.f = None
            return None
        
        truncate = self.truncate
        if truncate is not None and truncate <= 0:
            self.f=None
            return None

        # Fall back to standard read
        readSize = min(truncate if truncate else self.CHUNK_SIZE, length if length else self.CHUNK_SIZE, self.CHUNK_SIZE)
        #print "Readsize",readSize

        readsuccess = False
        while not readsuccess:
            try:
                b = self.prebuffer+self.f.read(readSize)
                readsuccess=True
            except IOError, ioe:
                #print "IOE",str(ioe)
                if ioe.errno != errno.EAGAIN and ioe.errno != errno.EINTR:
                    raise ioe
            
        self.prebuffer=''
        bytesRead = len(b)              # this could be greater than truncate!
        if not bytesRead:
            if length:
                raise RuntimeError("Ran out of data reading file %r, expected %d more bytes" % (self.f, length))
            else:
                # has the process errored on us
                return None
        else:
            if self.length:
                self.length -= bytesRead
            
            if self.truncate:
                if bytesRead>self.truncate:
                    t = self.truncate
                    self.truncate -= bytesRead
                    self.prebuffer=b[t:]
                    #print "T:",t
                    return b[:t]
                else:
                    self.truncate -= bytesRead
            
            return b

    def close(self, close_handle=True):
        if close_handle:
            self.f.close()
        self.f = None
        SimpleStream.close(self)