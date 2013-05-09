import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from fixture_helpers import admin
from request_test_base import RequestTest
import os
import time
import sys

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

# to run a fakes3 server, install fakes3 then make an empty directory to server
# then run with something like:
#
# /var/lib/gems/1.8/bin/fakes3 -r ./fakes3 -p 8090
#

from urllib import quote

QUOTED_TEST_S3_SERVER = quote(conf.s3_server)

class S3FileUploadTest(RequestTest):

    def setUp(self):
        RequestTest.setUp(self)
        admin.create_fakes3_backend()


    def tearDown(self):
        RequestTest.tearDown(self)

    def notest_s3_files_list(self):
        import requests
        
        r = self.session.get(conf.yabiurl+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_S3_SERVER) )
        print r.text

        self.assertTrue(r.status_code==200, "Could not list S3 backend contents")
        
        import json
        data = json.loads(r.text)
        self.assertTrue('/' in data)
        self.assertTrue('files' in data['/'])
        self.assertTrue('directories' in data['/'])
        
    def notest_zzz_s3_file_upload(self):
        from StringIO import StringIO
        contents=StringIO("This is a test file\nOk!\n")
        filename="test.txt"
        
        import requests
       
        # upload
        files = {'file': ("file.txt", open(__file__, 'rb'))}
        r = self.session.post( url = conf.yabiurl+"/ws/fs/put?uri=%s"%(QUOTED_TEST_S3_SERVER),
                    files = files
                   )
        
        print r.status
        

        r = self.session.get(conf.yabiurl+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_S3_SERVER))

        self.assertTrue(r.status_code==200, "Could not list S3 backend contents")
        import json
        data = json.loads(r.text)
        self.assertTrue('/' in data)
        self.assertTrue('files' in data['/'])
        self.assertTrue('directories' in data['/'])
        
    def notest_s3_files_deletion_non_existent(self):
        import requests
        
        r = self.session.get(conf.yabiurl+"/ws/fs/rm?uri=%s/DONT_EXIST.dat"%(QUOTED_TEST_S3_SERVER))

        self.assertTrue(r.status_code == 404, "Incorrect status code returned. Should be 404. Returns %d instead!"%r.status_code)

        import json
        error = json.loads(r.text)
        self.assertTrue('level' in error)
        self.assertTrue('message' in error)
        self.assertTrue(error['level']=='fail')
        self.assertTrue("not found" in error['message'].lower())

        
    def notest_s3_mkdir(self):
        import requests
        
        r = self.session.get(conf.yabiurl+"/ws/fs/mkdir?uri=%s/directory"%(QUOTED_TEST_S3_SERVER))

        #sys.stderr.write("status: %d\n"%r.status_code)
        #sys.stderr.write("headers: %s\n"%str(r.headers))
        #sys.stderr.write("body: %s\n"%r.text)

         
    
