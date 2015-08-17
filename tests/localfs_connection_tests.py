# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import unittest
from .support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from .fixture_helpers import admin
import os
import time
import sys
import subprocess
from StringIO import StringIO
import json
import shutil

from .request_test_base import RequestTest

TEST_LOCALFS_SERVER = "localfs://username@localhost.localdomain/data/yabi-localfs-test/"

def make_random_string(length=None):
    import random
    if not length:
        length = random.randint(200,10000)
    return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789)!@#$%^&*()`~-_=+[{]}\\|;:'\",<.>/?") for I in range(length)])

class LocalfsFileTests(RequestTest):
    TIMEOUT = 30.0

    @staticmethod
    def fscmd(cmd, path=""):
        return RequestTest.fscmd(cmd, TEST_LOCALFS_SERVER + path)

    def setUp(self):
        RequestTest.setUp(self)
        admin.create_localfs_backend()

    def tearDown(self):
        admin.destroy_localfs_backend()
        RequestTest.tearDown(self)

    def build_file_archive(self, base='/data/yabi-localfs-test', include_parent_dir=False):
        """Builds a test directory nested full of files and directories to test archive stuff"""
        # make some tmp file structures
        TOP_DIR = "."
        if include_parent_dir:
            TOP_DIR = "yabi-localfs-test"
        try:
            shutil.rmtree(base)
        except OSError as ose:
            pass
        os.makedirs(base)

        dirs = [    "dir1",
                    "dir2",
                    "dir1/dir1-1",
                    "dir1/dir1-2",
                    "dir2/dir2-1",
                    "dir2/dir2-2"
                ]

        dirstruct = [TOP_DIR + "/"]

        for d in dirs:
            current_dir = os.path.join(base, d)
            os.mkdir(current_dir)
            dirstruct.append(os.path.join(TOP_DIR,d) + "/")

            # bundle some random files into these dirs
            for filename in [ "file1.txt", "file2.dat", "file3.bing" ]:
                dirstruct.append(os.path.join(TOP_DIR, d, filename))
                with open(os.path.join(current_dir, filename), 'wb') as fh:
                    for num in range(20):
                        fh.write( make_random_string() )

        return dirstruct

    def test_localfs_files_list(self):
        url = self.fscmd("ls")
        print("test_localfs_files_list: url = %s" % url)
        r = self.session.get(url)

        self.assertEqual(r.status_code, 200, "Could not list localfs backend contents")
        data = json.loads(r.text)

        self.assertIn("/data/yabi-localfs-test/", data)
        self.assertIn('files', data["/data/yabi-localfs-test/"])
        self.assertIn('directories', data["/data/yabi-localfs-test/"])

    def test_localfs_rcopy(self):
        # make some tmp file structures
        basedir = '/data/yabi-localfs-test/'
        srcdir = basedir + "input-rcopy"
        destdir = basedir + "output-rcopy/"
        dirs = self.build_file_archive(srcdir)
        os.system("mkdir -p %s" % destdir)

        payload = {
            'yabiusername':conf.yabiusername,
            'src':TEST_LOCALFS_SERVER+"input-rcopy/",
            'dst':TEST_LOCALFS_SERVER+"output-rcopy/"
        }

        r = self.session.post(self.fscmd("rcopy"), data=payload)
        self.assertEqual(r.status_code, 200, "Could not perform rcopy")

        # diff the two directories
        result = os.system("diff -r '%s' '%s'"%(srcdir, os.path.join(destdir, 'input-rcopy')))

        self.assertEqual(result, 0, "Diff between the input and output failed")

        # clean up
        shutil.rmtree(basedir)

    def test_localfs_zget(self):
        # make some tmp file structures
        dirs = self.build_file_archive('/data/yabi-localfs-test/', include_parent_dir=True)

        payload = {
            'yabiusername':conf.yabiusername,
            'uri':TEST_LOCALFS_SERVER,
        }

        r = self.session.get(self.fscmd("zget"), params=payload, stream=True)
        self.assertEqual(r.status_code, 200, "Could not perform zget. return code was: %d"%r.status_code)

        # create a process to parse the tarball result
        detar = subprocess.Popen(["tar","-tz"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        # get the payload and pipe it into tar
        stdout, stderr = detar.communicate(r.raw.read())

        detar_result = [X.rstrip() for X in stdout.split('\n') if X.rstrip() != '']

        self.assertEqual(detar.returncode, 0, "detar of returned result failed exit code: %d"%(detar.returncode))

        # check each entry is represented
        for d in dirs:
            self.assertIn(d, detar_result)

        # and the reverse. So that there are no extra entries
        for d in detar_result:
            self.assertIn(d, dirs)

        shutil.rmtree('/data/yabi-localfs-test/')


    def test_localfs_file_upload_and_download(self):
        content = make_random_string()
        length = len(content)

        contents=StringIO(content)
        filename="test.txt"

        # upload
        files = {'file': ("file.txt", contents)}
        url = self.fscmd("put")
        r = self.session.post(url=url, files=files)

        self.assertEqual(r.status_code, 200)
        url = self.fscmd("ls")
        r = self.session.get(url)
        self.assertEqual(r.status_code, 200, "Could not list localfs backend contents - status code = %s" % r.status_code)
        data = json.loads(r.text)

        files = data["/data/yabi-localfs-test/"]["files"]
        self.assertEqual(len(files), 1)

        filename,filesize,filedate,symlink = files[0]
        self.assertFalse(symlink)
        self.assertEqual(filename, 'file.txt')

        self.assertEqual(filesize, length)

        # get the file so we can compare
        r = self.session.get(url=self.fscmd("get", "file.txt"))

        self.assertEqual(len(r.text), filesize)
        self.assertEqual(r.text, content)
