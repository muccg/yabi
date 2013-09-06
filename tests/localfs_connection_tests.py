import unittest
from support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from fixture_helpers import admin
import os
import time
import sys
from urllib import quote
from request_test_base import RequestTest, remove_slash_if_has

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

TEST_LOCALFS_SERVER = "localfs://username@localhost.localdomain/tmp/yabi-localfs-test/"
QUOTED_TEST_LOCALFS_SERVER = quote(TEST_LOCALFS_SERVER)

def get_localfs_server():
    return QUOTED_TEST_LOCALFS_SERVER


def make_random_string(length=None):
    import random
    if not length:
        length = random.randint(200,10000)
    return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789)!@#$%^&*()`~-_=+[{]}\\|;:'\",<.>/?") for I in range(length)])

class LocalfsFileTests(RequestTest):
    TIMEOUT = 30.0
    
    def setUp(self):
        RequestTest.setUp(self)
        admin.create_localfs_backend()

    def tearDown(self):
        admin.destroy_localfs_backend()
        RequestTest.tearDown(self)

    def build_file_archive(self, base='/tmp/yabi-localfs-test'):
        """Builds a test directory nested full of files and directories to test archive stuff"""
        # make some /tmp file structures
        import shutil
        try:
            shutil.rmtree(base)
        except OSError, ose:
            pass
        os.makedirs(base)
        
        dirs = [    "dir1",
                    "dir2",
                    "dir1/dir1-1",
                    "dir1/dir1-2",
                    "dir2/dir2-1",
                    "dir2/dir2-2"
                ]
                
        dirstruct = ["./"]
                
        for d in dirs:
            os.mkdir(os.path.join(base,d))
            dirstruct.append(os.path.join(".",d)+"/")
            
            # bundle some random files into these dirs
            for filename in [ "file1.txt", "file2.dat", "file3.bing" ]:
                dirstruct.append(os.path.join(".",d,filename))
                with open(os.path.join(base,dirstruct[-1]), 'wb') as fh:
                    for num in range(20):
                        fh.write( make_random_string() )
                   
        return dirstruct

    def test_localfs_files_list(self):
        import requests
        url = remove_slash_if_has(conf.yabiurl)+ "/ws/fs/ls?uri=%s" % (get_localfs_server())
        print "test_localfs_files_list: url = %s" % url
        r = self.session.get(url)

        self.assertTrue(r.status_code==200, "Could not list localfs backend contents")
        import json
        data = json.loads(r.text)
        
        self.assertTrue("/tmp/yabi-localfs-test/" in data)
        self.assertTrue('files' in data["/tmp/yabi-localfs-test/"])
        self.assertTrue('directories' in data["/tmp/yabi-localfs-test/"])
        
    def xtest_localfs_rcopy(self):
        import requests
        
        # make some /tmp file structures
        basedir = '/tmp/yabi-localfs-test/'
        srcdir = basedir + "input-rcopy/"
        destdir = basedir + "output-rcopy/"
        dirs = self.build_file_archive(srcdir)
        os.system("mkdir -p %s" % destdir)
            
        payload = {
            'yabiusername':conf.yabiusername,
            'src':TEST_LOCALFS_SERVER+"input-rcopy/",
            'dst':TEST_LOCALFS_SERVER+"output-rcopy/"
        }
        
        r = self.session.post(remove_slash_if_has(conf.yabiurl) + "/ws/fs/rcopy", data=payload)
        import sys
        sys.stderr.write(r.text)
        self.assertTrue(r.status_code==200, "Could not perform rcopy")
  
        # diff the two directories
        result = os.system("diff -r '%s' '%s'"%(srcdir, destdir))
        
        self.assertTrue(result==0, "Diff between the input and output failed")
        
        # clean up
        import shutil
        shutil.rmtree(basedir)

    def xtest_localfs_zget(self):
        import requests
        
        # make some /tmp file structures
        dirs = self.build_file_archive('/tmp/yabi-localfs-test/')
                    
        payload = {
            'yabiusername':conf.yabiusername,
            'uri':  get_localfs_server()
            #'uri':TEST_LOCALFS_SERVER,
        }
        
        r = self.session.get(remove_slash_if_has(conf.yabiurl) +"/ws/fs/zget", params=payload, stream=True)
        import sys
        self.assertTrue(r.status_code==200, "Could not perform zget. return code was: %d"%r.status_code)

        # create a process to parse the tarball result
        import subprocess
        detar = subprocess.Popen(["tar","-tz"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # get the payload and pipe it into tar 
        rawdata = r.raw
        stdout, stderr = detar.communicate(rawdata)
            
        detar_result = [(X[:-1] if X[-1]=='\n' else X) for X in stdout.split('\n')]
        
        self.assertTrue(detar.returncode==0, "detar of returned result failed exit code: %d"%(detar.returncode))
        
        # check each entry is represented
        for d in dirs:
            self.assertTrue(d in detar_result, "entry '%s' not found in detar result"%d)
            
        # and the reverse. So that there are no extra entries
        for d in detar_result:
            self.assertTrue(d in dirs, "entry '%s' only found in detar result"%d)
        
        import shutil
        shutil.rmtree('/tmp/yabi-localfs-test/')


    def test_localfs_file_upload_and_download(self):
        content = make_random_string()
        length = len(content)
        
        from StringIO import StringIO
        contents=StringIO(content)
        filename="test.txt"
        
        import requests
        
        # upload
        files = {'file': ("file.txt", contents)}
        url = remove_slash_if_has(conf.yabiurl) + "/ws/fs/put?uri=%s"% get_localfs_server()
        r = self.session.post(url=url, files=files)
        sys.stderr.write("%d...\n" % r.status_code)

        self.assertTrue(r.status_code == 200, "Expected status code 200. Actual = %s" % r.status_code)
        url = remove_slash_if_has(conf.yabiurl) + "/ws/fs/ls?uri=%s" % get_localfs_server()
        r = self.session.get(url)
        self.assertTrue(r.status_code==200, "Could not list localfs backend contents - status code = %s" % r.status_code)
        import json
        data = json.loads(r.text)
        
        sys.stderr.write("=> %s\n\n"%(str(data)))
        
        files = data["/tmp/yabi-localfs-test/"]["files"]
        self.assertTrue(len(files)==1)
        
        filename,filesize,filedate,symlink = files[0]
        self.assertTrue(symlink==False)
        self.assertTrue(filename=='file.txt')
        
        #sys.stderr.write("=> %d != %d\n\n"%(filesize,length))
        self.assertTrue(filesize==length)
        
        # get the file so we can compare
        r = self.session.get(url=remove_slash_if_has(conf.yabiurl) + "/ws/fs/get?uri=%sfile.txt"%(get_localfs_server()) )
        #sys.stderr.write("code => %d\n"%(r.status_code))
        #sys.stderr.write("text => %s\n"%(r.text))
        
        self.assertTrue( len(r.text) == filesize )
        self.assertTrue( r.text == content )
