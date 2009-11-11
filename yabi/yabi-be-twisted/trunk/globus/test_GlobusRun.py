import GlobusRun
import RSL

from twisted.trial import unittest, reporter, runner
import tempfile
import os
from processing import Process, Queue
from twisted.internet import reactor, protocol
import random
import time
import subprocess

from test_certificates import EXPIRED_CERT, EXPIRED_KEY, EXPIRED_KEY_PW
from test_certificates import VALID_CERT, VALID_KEY, VALID_KEY_PW

import stackless
from utils.stacklesstest import StacklessTest
from utils.stacklesstools import sleep

import re

re_uuid = re.compile(r'.*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}.*',flags=re.MULTILINE)

def has_valid_uuid(data):
    """return true if the data contains a valid uuid"""
    return re_uuid.search(data)!=None

class GlobusRunTest(StacklessTest):
    """Test the server sets up correctly and tears down correctly."""
    timeout = 70.0
    
    
    def setUp(self):
        StacklessTest.setUp(self)
        
        import CertificateProxy
        
        # build an invalid proxy we can use when needed
        self.proxy = CertificateProxy.CertificateProxy()
        
    def test_run_remote_date_no_proxy(self):
        def test_code():
            # validate the proxy user
            self.proxy.CreateUserProxy('valid_user', VALID_CERT, VALID_KEY, VALID_KEY_PW)
            
            globus = GlobusRun.GlobusRun()
            
            # make an RSL file
            rsl = RSL.ConstructRSL( command="date" )
            filename = RSL.writersltofile(rsl)
            
            # run a job with the certfile
            fh = tempfile.NamedTemporaryFile(suffix=".cert", delete=False)
            fh.write(EXPIRED_CERT)
            fh.close()
            
            pp = globus.run( fh.name, filename )
            
            # wait until pp is finished
            while not pp.isDone():
                stackless.schedule()
                
            os.unlink(fh.name)
                
            return pp
                
        # now the files are set up, lets test the runner with these tests
        def _test(pp):
            stdout, stderr, exitcode = pp.out, pp.err, pp.exitcode
            
            # we should be informed that we need a proxy
            self.assert_("Submitting job" in stderr)
            self.assert_("Failed" in stderr)
            self.assert_("A proxy is required" in stderr or "Couldn't read proxy's private key from bio" in stderr)
            self.assert_(exitcode!=0)
        
        return self.deferred_test(test_code,_test)
        
    def test_run_remote_date_with_expired_proxy(self):
        def test_code():
            self.proxy.CreateUserProxy('valid_user', VALID_CERT, VALID_KEY, VALID_KEY_PW)
            
            globus = GlobusRun.GlobusRun()
            
            # make an RSL file
            rsl = RSL.ConstructRSL( command="date" )
            filename = RSL.writersltofile(rsl)
            
            # run a job with the certfile
            # expire after 1 minute
            self.proxy.SetExpiryTime(1)
            self.proxy.CreateUserProxy('invalid_user', EXPIRED_CERT, EXPIRED_KEY, EXPIRED_KEY_PW)
            
            # wait 1 minute
            sleep(60)
            pp = globus.run( self.proxy.ProxyFile('invalid_user'), filename )
            
            # wait until pp is finished
            while not pp.isDone():
                stackless.schedule()
            
            return pp
            
        def _test(pp):
            stdout, stderr, exitcode = pp.out, pp.err, pp.exitcode
            
            # we should be informed that we need a proxy
            self.assert_("Submitting job" in stderr)
            self.assert_("Failed" in stderr)
            self.assert_("expired" in stderr)
            #self.assert_("Could not verify credential" in stdout)
            #self.assert_("Invalid CRL: The available CRL has expired" in stdout)
            self.assert_(exitcode!=0)
        
        return self.deferred_test(test_code,_test)
        
    def test_run_remote_date_with_valid_proxy(self):
        def test_code():
            self.proxy.CreateUserProxy('valid_user', VALID_CERT, VALID_KEY, VALID_KEY_PW)
            
            globus = GlobusRun.GlobusRun()
            
            # make an RSL file
            rsl = RSL.ConstructRSL( command="date" )
            filename = RSL.writersltofile(rsl)
            
            # run a job with the certfile
            pp = globus.run( self.proxy.ProxyFile('valid_user'), filename )
            
            # wait until pp is finished
            while not pp.isDone():
                stackless.schedule()
            
            return pp
        
        def _test(pp):
            stdout, stderr, exitcode = pp.out, pp.err, pp.exitcode
            
            # we should be informed that we need a proxy
            self.assert_("Submitting job" in stderr)
            self.assert_("Done." in stderr)
            self.assert_("Job ID: uuid:" in stderr)
            self.assert_("Termination time:" in stderr)
             
            # make sure it contains a valid uuid
            self.assert_(has_valid_uuid(stderr))
             
            self.assert_(exitcode==0)
        
        return self.deferred_test(test_code,_test)
        
        
    test_run_remote_date_with_expired_proxy.skip = "Expired proxy test taskes too long"
        
    