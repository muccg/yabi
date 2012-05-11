import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE
from fixture_helpers import admin
import os
import time
import sys

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

# test user
TEST_USER = "demo"
TEST_PASSWORD = "demo"

from urllib import quote

try:
    import requests
except ImportError, ioe:
    pass                            # admin imports this file aswell... but doesn't have requests installed :P

class RequestTest(YabiTestCase):
    """This baseclass logs in as the user to perform testing on the yabi frontend"""
    def setUp(self):
        YabiTestCase.setUp(self)
        
        # login
        self.session = requests.session()
        r = self.session.post(YABI_FE+"/login", data={'username':TEST_USER,'password':TEST_PASSWORD})
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

    def tearDown(self):
        YabiTestCase.tearDown(self)


    