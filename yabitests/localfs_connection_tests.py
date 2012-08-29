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

def make_random_string(length=None):
    import random
    if not length:
        length = random.randint(200,10000)
    return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789)!@#$%^&*()`~-_=+[{]}\\|;:'\",<.>/?") for I in range(length)])

class LocalfsFileTests(RequestTest):
    TIMEOUT = 30.0
    
    @classmethod
    def setUpAdmin(self):
        admin.create_localfs_backend()

    @classmethod
    def tearDownAdmin(self):
        admin.destroy_localfs_backend()

    def notest_localfs_files_list(self):
        import requests
        r = self.session.get(YABI_FE+"/ws/fs/ls?uri=%s"%(QUOTED_TEST_LOCALFS_SERVER) )

        self.assertTrue(r.status_code==200, "Could not list localfs backend contents")
        import json
        data = json.loads(r.text)
        
        self.assertTrue("/tmp/yabi-localfs-test/" in data)
        self.assertTrue('files' in data["/tmp/yabi-localfs-test/"])
        self.assertTrue('directories' in data["/tmp/yabi-localfs-test/"])
        
    def test_localfs_rcopy(self):
        import requests
        
        # make some /tmp file structures
        try:
            os.mkdir("/tmp/yabi-localfs-test/")
        except OSError, ose:
            pass
        
        dirs = [    "dir1",
                    "dir2",
                    "dir1/dir1-1",
                    "dir1/dir1-2",
                    "dir2/dir2-1",
                    "dir2/dir2-2"
                ]
        
        basedir = "/tmp/yabi-localfs-test/input-rcopy/"
        os.mkdir(basedir)
        
        for d in dirs:
            os.mkdir(os.path.join(basedir,d))
            
            # bundle some random files into these dirs
            for filename in [ "file1.txt", "file2.dat", "file3.bing" ]:
                with open(os.path.join(basedir,d,filename), 'w') as fh:
                    for num in range(20):
                        fh.write( make_random_string() )
            
        # now lets rcopy it to here:
        destdir = "/tmp/yabi-localfs-test/output-rcopy/"
        
        payload = {
            'yabiusername':TEST_USERNAME,
            'src':QUOTED_TEST_LOCALFS_SERVER+"input-rcopy/",
            'dst':QUOTED_TEST_LOCALFS_SERVER+"output-rcopy/"
        }
        
        r = self.session.post(YABI_FE+"/ws/fs/rcopy", data=payload)
        import sys
        #sys.stderr.write("error code: %d\n"%r.status_code)
        #sys.stderr.write("error response: %s\n"%r.text)
        self.assertTrue(r.status_code==200, "Could not perform rcopy")
        
        # diff the two directories
        result = os.system("diff -r '%s' '%s'"%(basedir,destdir))
        sys.stderr.write("diff result: %s\n"%(result))
        
        
    def notest_localfs_file_upload_and_download(self):
        content = make_random_string()
        length = len(content)
        
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
        
        
        
        