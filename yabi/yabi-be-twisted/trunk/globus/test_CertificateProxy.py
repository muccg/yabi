import CertificateProxy
from twisted.trial import unittest, reporter, runner
import os

from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall
from twisted.python.failure import Failure
from twisted.internet.base import _SignalReactorMixin     

from test_certificates import TEST_CERT, TEST_KEY, TEST_KEY_PW

import stackless
from utils.stacklesstest import StacklessTest

class CertificateProxyTest(StacklessTest):
    """Test the server sets up correctly and tears down correctly."""
    _suppressUpDownWarning = True
    PORT = 9000

    timeout = 10.0

    def setUp(self):
        StacklessTest.setUp(self)
        self.proxy = CertificateProxy.CertificateProxy()
        
    def test_certificate_stores_created(self):
        """Check that the storage is created"""
        self.failUnless( os.path.exists(self.proxy.storage) )
        
    def test_unauthed_user_proxy_is_invalid(self):
        self.assert_( self.proxy.IsProxyValid('dummy_user')==False )
    
    def test_create_valid_user_proxy(self):
        """Test that we can successfuly create a user proxy cert"""
        def _test(runner):
            self.assert_( self.exception is None )
            self.assert_( os.path.exists( self.proxy.ProxyFile('test_user') ) )
            self.assert_( self.proxy.IsProxyValid('test_user') )
        
        return self.deferred_test(self.proxy.CreateUserProxy,_test,['test_user', TEST_CERT, TEST_KEY, TEST_KEY_PW])
        
    def test_create_invalid_user_proxy(self):
        INVALID_CERT = TEST_CERT.split()
       
        # change 20 characters randomly
        import random
        for i in range(20):
            INVALID_CERT[random.randint(0,len(INVALID_CERT)-1)]=random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            
        INVALID_CERT = "".join(INVALID_CERT)
        
        def _test(task):
            # make sure as exception is raised and its "CertificateProxy.ProxyInitError"
            self.assert_( self.exception.__class__,CertificateProxy.ProxyInitError )
        
        return self.deferred_test(self.proxy.CreateUserProxy,_test,['test_user', INVALID_CERT, TEST_KEY, TEST_KEY_PW])
         
    def test_invalid_cert_password(self):
        return self.assertRaises(CertificateProxy.ProxyInvalidPassword,self.proxy.CreateUserProxy,'test_user', TEST_CERT, TEST_KEY, "this is an invalid password")
        
    def test_zzz_cleanup(self):
        """Test that the cleanup script works"""
        directory = self.proxy.storage
        self.failUnless( os.path.exists(directory) )
        self.proxy.CleanUp()
        self.failIf( os.path.exists(directory) )

