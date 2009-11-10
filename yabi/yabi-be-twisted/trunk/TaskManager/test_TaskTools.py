import stackless
from utils.stacklesstest import StacklessTest

from TaskTools import Sleep

from t_webclient import t_webclient

import random, time

sleep_time = lambda: float(random.randint(1,200))/50.

class OurClient():
    def __init__(self):
        self.getPage = "page"
        self.downloadPage = "dl"
    
oc = OurClient()
    
class TaskToolsTest(t_webclient):
    """Test the server sets up correctly and tears down correctly."""
    def __init__(self):
        self.setClient(oc)
        print "OCD",oc.downloadPage
    
    def setUp(self):
        StacklessTest.setUp(self)
        self.setClient(oc)
        print "DP",oc.downloadPage
        
    def test_sleep(self):
        """Check that the sleep function works"""
        time_delay = sleep_time()
        
        now = time.time()
        
        def test_code():
            Sleep(time_delay)
            
        def _test(data):
            # assert enough time was left
            self.assert_(time.time()-now >= time_delay)
            
            # but not too much
            self.assert_(time.time()-now-time_delay < 0.2)
            
        return self.deferred_test(test_code,_test)
        