from twisted.trial import unittest, reporter, runner
from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall
from twisted.python.failure import Failure
from twisted.internet.base import _SignalReactorMixin     
from twisted.python.filepath import FilePath
from twisted.web import server, static
from twisted.web.test.test_webclient import WrappingFactory

import stackless, os
from utils.stacklesstest import StacklessTest

from fs.Exceptions import InvalidPath
from twisted.web2 import server
from twisted.web2 import log
from twisted.application import strports, service, internet

from globus.CertificateProxy import ProxyInitError

import random
import md5

from twisted.web2.test.test_http import HTTPTests, SSLServerTest, ErrorTestCase, CoreHTTPTestCase, PreconditionTestCase

DATA_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmopqrstuvwxyz0123456789!@#$%^&*()`~,./<>?;':\"[]{}-=_+\\| \n\r"

class SSLResourceTest(StacklessTest, SSLServerTest, ErrorTestCase, CoreHTTPTestCase, PreconditionTestCase):
    """Test the server sets up correctly and tears down correctly."""
    timeout = 10.0
    
    def _listen(self, site):
        return reactor.listenTCP(0, site, interface="127.0.0.1")
    
    def setUp(self):
        StacklessTest.setUp(self)
        SSLServerTest.setUp(self)
        
        if False:
            # setup a little server with the connectors
            self.cleanupServerConnections = 0
            from BaseResource import BaseResource
            r = self.r = BaseResource()
            
            # Setup default common access logging
            res = log.LogWrapperResource(r)
            log.DefaultCommonAccessLoggingObserver().start()
    
            
            self.site = server.Site(res)
            
            from twisted.web2 import channel
            self.portno = 8192
            internet.TCPServer(self.portno, channel.HTTPFactory(self.site))

    def tearDown(self):
        StacklessTest.tearDown(self)
        SSLServerTest.tearDown(self)
        
    def test_webservice(self):
        def test_code():
            # test we can access the webpage
            from utils.stacklesstools import GET
            #print "GET",GET,self.portno
            p = GET("/",host="localhost",port=self.portno)
            #print "!!",p
        
        def _test(data):
            #print "EXC:",self.exception
            
            self.assert_( 1 == 1 )
            
        return self.deferred_test(test_code,_test)
         
#ResourceTest.skip = "abstract base class"