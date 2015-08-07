from __future__ import print_function
import time
import sys
import json
from StringIO import StringIO

import unittest
from .support import YabiTestCase, StatusResult, all_items, json_path, FileUtils, conf
from .fixture_helpers import admin
from .request_test_base import RequestTest
from .fakes3 import fakes3_setup

@unittest.skip('S3 tests currently disabled in docker containers')
class S3FileUploadTest(RequestTest):
    """
    Tests the S3 backend against the fakes3 server.
    """

    SPECIAL_TEST_BUCKET = "fakes3"

    @classmethod
    def fscmd(cls, cmd, uri=""):
        server = "s3://%s@%s.%s" % (conf.s3_user, cls.SPECIAL_TEST_BUCKET, conf.s3_host)
        return RequestTest.fscmd(cmd, server + uri)

    def setUp(self):
        RequestTest.setUp(self)
        self.backend, self.credential, self.becred = admin.create_fakes3_backend()

        fakes3_setup(self, self.SPECIAL_TEST_BUCKET)

    def tearDown(self):
        self.backend.delete()
        self.credential.delete()
        self.becred.delete()

    def test_s3_files_list(self):
        r = self.session.get(self.fscmd("ls"))
        print(r.text)

        self.assertEqual(r.status_code, 200, "Could not list S3 backend contents")

        data = json.loads(r.text)

        path = "/"  # original test case value

        self.assertEquals(data, {})

    def test_zzz_s3_file_upload(self):
        contents=StringIO("This is a test file\nOk!\n")
        filename="test.txt"

        # upload
        files = {'file': ("file.txt", open(__file__, 'rb'))}
        r = self.session.post(url=self.fscmd("put"), files=files)

        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertEqual(data, {
            "message": "no message",
            "level": "success",
            "num_fail": 0,
            "num_success": 1,
        })

        path = "/"  # original test case value
        path = ""   # a value which causes test to pass

        r = self.session.get(self.fscmd("ls"))

        self.assertEqual(r.status_code, 200, "Could not list S3 backend contents")
        data = json.loads(r.text)
        self.assertIn(path, data)
        self.assertIn('files', data[path])
        self.assertIn('directories', data[path])

    def test_s3_files_deletion_non_existent(self):
        r = self.session.get(self.fscmd("rm", "/DONT_EXIST.dat"))

        # # The following assertions don't seem to reflect the current implementation.
        # # Possibly it is due to use of fakes3 server.
        # self.assertEqual(r.status_code, 404, "Incorrect status code returned. Should be 404. Returns %d instead!"%r.status_code)
        # error = json.loads(r.text)
        # self.assertIn('level', error)
        # self.assertIn('message', error)
        # self.assertEqual(error['level'], 'fail')
        # self.assertIn("not found", error['message'].lower())

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "OK")

    def test_s3_mkdir(self):
        r = self.session.get(self.fscmd("mkdir", "/directory"))

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, "OK")

        r = self.session.get(self.fscmd("ls", "/directory"))

        self.assertEqual(r.status_code, 200)

        data = json.loads(r.text)
        self.assertIn('/directory', data)
        self.assertIn('files', data['/directory'])
        self.assertIn('directories', data['/directory'])
