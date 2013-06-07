import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from fixture_helpers import admin
import os
import time
import sys

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

from urllib import quote

try:
    import requests
except ImportError, ioe:
    pass                            # admin imports this file aswell... but doesn't have requests installed :P

class RequestTest(YabiTestCase):
    """This baseclass logs in as the user to perform testing on the yabi frontend"""
    def setUp(self):
        YabiTestCase.setUp(self)
        
        # demo login session
        self.session = requests.session()
        r = self.session.post(conf.yabiurl+"/login", data={'username':conf.yabiusername,'password':conf.yabipassword})
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

    def tearDown(self):
        YabiTestCase.tearDown(self)
        
        
class RequestTestWithAdmin(RequestTest):
    """This baseclass logs in as the user to perform testing on the yabi frontend"""
    def setUp(self):
        RequestTest.setUp(self)
        
        # demo login session
        self.adminsession = requests.session()
        r = self.adminsession.post(conf.yabiurl+"/login", data={'username':conf.yabiadminusername,'password':conf.yabiadminpassword})
        self.assertTrue(r.status_code == 200, "Could not login as admin to frontend. Frontend returned: %d"%(r.status_code))

    def tearDown(self):
        RequestTest.tearDown(self)

    
