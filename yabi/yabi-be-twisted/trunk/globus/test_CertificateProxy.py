import stacklessreactor
#stacklessreactor.install()

from twisted.application.reactors import Reactor

stacked = Reactor('stackless','stacklessreactor.StacklessReactor', 'Reactor that pumps the stackless loop')

import CertificateProxy
from twisted.trial import unittest, reporter, runner
import os

from twisted.internet import reactor

from test_certificates import TEST_CERT, TEST_KEY, TEST_KEY_PW

class CertificateProxyTest(unittest.TestCase):
    """Test the server sets up correctly and tears down correctly."""
    _suppressUpDownWarning = True
    PORT = 9000

    def setUpClass(self):
        self.proxy = CertificateProxy.CertificateProxy()

    def test_certificate_stores_created(self):
        """Check that the storage is created"""
        self.failUnless( os.path.exists(self.proxy.storage) )
        
    def test_unauthed_user_proxy_is_invalid(self):
        self.assert_( self.proxy.IsProxyValid('dummy_user')==False )
        
    def test_create_valid_user_proxy(self):
        """Test that we can successfuly create a user proxy cert"""
        import stackless
        def run():
            self.proxy.CreateUserProxy('test_user', TEST_CERT, TEST_KEY, TEST_KEY_PW)
            
        from twisted.internet.task import LoopingCall
        
        def call():
            print "call"
            stackless.schedule()
        
        lc = LoopingCall(call)
        lc.start(0.1)
        
        
            
        if True:
            task = stackless.tasklet(run)
            task.setup()
            task.run()
            
            while task.alive:
                pass
                #reactor.doIteration(0.1)
                #stackless.schedule()
        else:
            run()
            
        self.assert_( os.path.exists( self.proxy.ProxyFile('test_user') ) )
        self.assert_( self.proxy.IsProxyValid('test_user') )
        
    def notest_create_invalid_user_proxy(self):
        INVALID_CERT = TEST_CERT.split()
       
        # change 20 characters randomly
        import random
        for i in range(20):
            INVALID_CERT[random.randint(0,len(INVALID_CERT)-1)]=random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            
        INVALID_CERT = "".join(INVALID_CERT)
        
        self.assertRaises(CertificateProxy.ProxyInitError,self.proxy.CreateUserProxy,'test_user', INVALID_CERT, TEST_KEY, TEST_KEY_PW)
        
    def notest_invalid_cert_password(self):
        self.assertRaises(CertificateProxy.ProxyInvalidPassword,self.proxy.CreateUserProxy,'test_user', TEST_CERT, TEST_KEY, "this is an invalid password")
        
    def test_zzz_cleanup(self):
        """Test that the cleanup script works"""
        directory = self.proxy.storage
        self.failUnless( os.path.exists(directory) )
        self.proxy.CleanUp()
        self.failIf( os.path.exists(directory) )

