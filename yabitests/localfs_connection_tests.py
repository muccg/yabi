import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, YABI_FE, TEST_USERNAME, TEST_PASSWORD
from fixture_helpers import admin
import os
import time
import sys
from urllib import quote
from request_test_base import RequestTest

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

TEST_LOCALFS_SERVER = "localfs://username@localhost.localdomain/tmp/yabi-localfs-test/"
QUOTED_TEST_LOCALFS_SERVER = quote(TEST_LOCALFS_SERVER)

class LocalfsFileTests(RequestTest):
    TIMEOUT = 30.0
    
    @classmethod
    def setUpAdmin(self):
        admin.create_localfs_backend()

    @classmethod
    def tearDownAdmin(self):
        admin.destroy_localfs_backend()

    def test_localfs_files_list(self):
        import requests
        r = self.session.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER) )

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
        
        # upload
        files = {'file': ("file.txt", contents)}
        r = self.session.post( url = YABI_FE+"/ws/fs/put?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER),
                    files = files
                   )
        
        #sys.stderr.write("%d...\n"%r.status_code)
        
        r = self.session.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER))

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
        r = self.session.get( url = YABI_FE+"/ws/fs/get?uri=%sfile.txt"%(QUOTED_TEST_LOCALFS_SERVER) )
        #sys.stderr.write("code => %d\n"%(r.status_code))
        #sys.stderr.write("text => %s\n"%(r.text))
        
        self.assertTrue( len(r.text) == filesize )
        self.assertTrue( r.text == content )
        
        
        
        