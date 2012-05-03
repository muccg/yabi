import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE
from fixture_helpers import admin
import os
import time
import sys

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

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

        r = s.get(YABI_FE+"/ws/fs/ls?uri=s3%3A//username@localhost.localdomain:8080/")

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
        r = s.post( url = YABI_FE+"/ws/fs/put?uri=s3%3A//username@localhost.localdomain%3A8080/",
                    files = {__file__: open(__file__, 'rb')}
                   )
        
        print r.status
        

        r = s.get(YABI_FE+"/ws/fs/ls?uri=s3%3A//username@localhost.localdomain:8080/")

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

        r = s.get(YABI_FE+"/ws/fs/rm?uri=s3%3A//username@localhost.localdomain:8080/DONT_EXIST.dat")

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

        r = s.get(YABI_FE+"/ws/fs/mkdir?uri=s3%3A//username@localhost.localdomain:8080/directory")

        #sys.stderr.write("status: %d\n"%r.status_code)
        #sys.stderr.write("headers: %s\n"%str(r.headers))
        #sys.stderr.write("body: %s\n"%r.text)

         
    