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

class GlobusRunTest(unittest.TestCase):
    """Test the server sets up correctly and tears down correctly."""
    
    def setUp(self):
        import CertificateProxy
        
        # build an invalid proxy we can use when needed
        self.proxy = CertificateProxy.CertificateProxy()
        self.proxy.CreateUserProxy('valid_user', VALID_CERT, VALID_KEY, VALID_KEY_PW)
    
    def test_run_remote_date_no_proxy(self):
        globus = GlobusRun.GlobusRun()
        
        # make an RSL file
        rsl = RSL.ConstructRSL( command="date" )
        filename = RSL.writersltofile(rsl)
        
        # run a job with the certfile
        fh = tempfile.NamedTemporaryFile(suffix=".cert", delete=False)
        fh.write(EXPIRED_CERT)
        fh.close()
        result = globus.run( fh.name, filename )
        
        os.unlink(fh.name)
        
        self.assert_(result.__class__ == subprocess.Popen )
        
        # lets get stdout and stderr
        stdout, stderr = result.communicate()
        
        # we should be informed that we need a proxy
        self.assert_("Submitting job" in stdout)
        self.assert_("Failed" in stdout)
        self.assert_("A proxy is required" in stdout)
        self.assert_(result.returncode!=0)
        
    def test_run_remote_date_with_expired_proxy(self):
        globus = GlobusRun.GlobusRun()
        
        # make an RSL file
        rsl = RSL.ConstructRSL( command="date" )
        filename = RSL.writersltofile(rsl)
        
        # run a job with the certfile
        # expire after 1 minute
        self.proxy.SetExpiryTime(1)
        self.proxy.CreateUserProxy('invalid_user', EXPIRED_CERT, EXPIRED_KEY, EXPIRED_KEY_PW)
        
        # wait 1 minute
        time.sleep(60)
        result = globus.run( self.proxy.ProxyFile('invalid_user'), filename )
        
        self.assert_(result.__class__ == subprocess.Popen )
        
        # lets get stdout and stderr
        stdout, stderr = result.communicate()
        
        # we should be informed that we need a proxy
        self.assert_("Submitting job" in stdout)
        self.assert_("Failed" in stdout)
        self.assert_("expired" in stdout)
        #self.assert_("Could not verify credential" in stdout)
        #self.assert_("Invalid CRL: The available CRL has expired" in stdout)
        self.assert_(result.returncode!=0)
        
    def test_run_remote_date_with_valid_proxy(self):
        globus = GlobusRun.GlobusRun()
        
        # make an RSL file
        rsl = RSL.ConstructRSL( command="date" )
        filename = RSL.writersltofile(rsl)
        
        # run a job with the certfile
        result = globus.run( self.proxy.ProxyFile('valid_user'), filename )
        
        self.assert_(result.__class__ == subprocess.Popen )
        
        # lets get stdout and stderr
        stdout, stderr = result.communicate()
        
        
    
        
    