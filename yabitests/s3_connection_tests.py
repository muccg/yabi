import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE
from fixture_helpers import admin
import os
import time
import sys

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

# to test s3, the default setup is to setup a fakes3 server on localhost on port 8080
# and to test against that. To change the server you are testing against change the 
# admin setup to connect to it and then change the following:
TEST_S3_SERVER = "s3://username@localhost.localdomain:8080/"

# to run a fakes3 server, install fakes3 then make an empty directory to server
# then run with something like:
#
# /var/lib/gems/1.8/bin/fakes3 -r ./fakes3 -p 8080
#

from urllib import quote

QUOTED_TEST_S3_SERVER = quote(TEST_S3_SERVER)

class S3FileUploadTest(YabiTestCase, FileUtils):
    @classmethod
    def setUpAdmin(self):
        #admin.create_tool_cksum()
        admin.create_fakes3_backend()

    @classmethod
    def tearDownAdmin(self):
        from yabiadmin.yabi import models
        #models.Tool.objects.get(name='cksum').delete()

    def setUp(self):
        YabiTestCase.setUp(self)
        #FileUtils.setUp(self)

    def tearDown(self):
        YabiTestCase.tearDown(self)
        #FileUtils.tearDown(self)

    def test_s3_files_list(self):
        import requests
        
        # login
        s = requests.session()
        r = s.post(YABI_FE+"/login", data={'username':'demo','password':'demo'})
        
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        r = s.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_S3_SERVER) )

        self.assertTrue(r.status_code==200, "Could not list S3 backend contents")
        import json
        data = json.loads(r.text)
        self.assertTrue('/' in data)
        self.assertTrue('files' in data['/'])
        self.assertTrue('directories' in data['/'])
        
    def test_zzz_s3_file_upload(self):
        from StringIO import StringIO
        contents=StringIO("This is a test file\nOk!\n")
        filename="test.txt"
        
        import requests
        
        # login
        s = requests.session()
        r = s.post(YABI_FE+"/login", data={'username':'demo','password':'demo'})
        
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        # upload
        files = {'file': ("file.txt", open(__file__, 'rb'))}
        r = s.post( url = YABI_FE+"/ws/fs/put?uri=%s"%(QUOTED_TEST_S3_SERVER),
                    files = files
                   )
        
        print r.status
        

        r = s.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_S3_SERVER))

        self.assertTrue(r.status_code==200, "Could not list S3 backend contents")
        import json
        data = json.loads(r.text)
        self.assertTrue('/' in data)
        self.assertTrue('files' in data['/'])
        self.assertTrue('directories' in data['/'])
        
    def test_s3_files_deletion_non_existent(self):
        import requests
        
        # login
        s = requests.session()
        r = s.post(YABI_FE+"/login", data={'username':'demo','password':'demo'})
        
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        r = s.get(YABI_FE+"/ws/fs/rm?uri=%s/DONT_EXIST.dat"%(QUOTED_TEST_S3_SERVER))

        self.assertTrue(r.status_code == 404, "Incorrect status code returned. Should be 404. Returns %d instead!"%r.status_code)

        import json
        error = json.loads(r.text)
        self.assertTrue('level' in error)
        self.assertTrue('message' in error)
        self.assertTrue(error['level']=='fail')
        self.assertTrue("not found" in error['message'].lower())

        
    def test_s3_mkdir(self):
        import requests
        
        # login
        s = requests.session()
        r = s.post(YABI_FE+"/login", data={'username':'demo','password':'demo'})
        
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        r = s.get(YABI_FE+"/ws/fs/mkdir?uri=%s/directory"%(QUOTED_TEST_S3_SERVER))

        #sys.stderr.write("status: %d\n"%r.status_code)
        #sys.stderr.write("headers: %s\n"%str(r.headers))
        #sys.stderr.write("body: %s\n"%r.text)

         
    