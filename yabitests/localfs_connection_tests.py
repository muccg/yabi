import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE, TEST_USERNAME, TEST_PASSWORD
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
TEST_LOCALFS_SERVER = "localfs://username@localhost.localdomain/tmp/yabi-localfs-test/"

# to run a fakes3 server, install fakes3 then make an empty directory to server
# then run with something like:
#
# /var/lib/gems/1.8/bin/fakes3 -r ./fakes3 -p 8080
#

# login credentials
logindetails={'username':TEST_USERNAME,'password':TEST_PASSWORD}

from urllib import quote

QUOTED_TEST_LOCALFS_SERVER = quote(TEST_LOCALFS_SERVER)

class LocalfsFileTests(YabiTestCase, FileUtils):
    @classmethod
    def setUpAdmin(self):
        admin.create_localfs_backend()

    @classmethod
    def tearDownAdmin(self):
        admin.destroy_localfs_backend()

    def setUp(self):
        YabiTestCase.setUp(self)
        #FileUtils.setUp(self)

    def tearDown(self):
        YabiTestCase.tearDown(self)
        #FileUtils.tearDown(self)

    def test_localfs_files_list(self):
        import requests
        
        # login
        s = requests.session()
        r = s.post(YABI_FE+"/login", data=logindetails)
        
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        r = s.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER) )

        self.assertTrue(r.status_code==200, "Could not list localfs backend contents")
        import json
        data = json.loads(r.text)
        
        self.assertTrue("/tmp/yabi-localfs-test/" in data)
        self.assertTrue('files' in data["/tmp/yabi-localfs-test/"])
        self.assertTrue('directories' in data["/tmp/yabi-localfs-test/"])
        
    def test_localfs_file_upload_and_download(self):
        import random
        length = random.randint(200,10000)
        content = "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789)!@#$%^&*()`~-_=+[{]}\\|;:'\",<.>/?") for I in range(length)])

        from StringIO import StringIO
        contents=StringIO(content)
        filename="test.txt"
        
        import requests
        
        # login
        s = requests.session()
        r = s.post(YABI_FE+"/login", data=logindetails)
        
        self.assertTrue(r.status_code == 200, "Could not login to frontend. Frontend returned: %d"%(r.status_code))

        # upload
        files = {'file': ("file.txt", contents)}
        r = s.post( url = YABI_FE+"/ws/fs/put?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER),
                    files = files
                   )
        
        #sys.stderr.write("%d...\n"%r.status_code)
        
        r = s.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER))

        self.assertTrue(r.status_code==200, "Could not list localfs backend contents")
        import json
        data = json.loads(r.text)
        
        #sys.stderr.write("=> %s\n\n"%(str(data)))
        
        files = data["/tmp/yabi-localfs-test/"]["files"]
        self.assertTrue(len(files)==1)
        
        filename,filesize,filedate,symlink = files[0]
        self.assertTrue(symlink==False)
        self.assertTrue(filename=='file.txt')
        
        #sys.stderr.write("=> %d != %d\n\n"%(filesize,length))
        self.assertTrue(filesize==length)
        
        # get the file so we can compare
        r = s.get( url = YABI_FE+"/ws/fs/get?uri=%sfile.txt"%(QUOTED_TEST_LOCALFS_SERVER) )
        #sys.stderr.write("code => %d\n"%(r.status_code))
        #sys.stderr.write("text => %s\n"%(r.text))
        
        self.assertTrue( len(r.text) == filesize )
        self.assertTrue( r.text == content )
        
        
        
        