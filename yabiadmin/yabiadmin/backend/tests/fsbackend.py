# -*- coding: utf-8 -*-

import datetime
import os
import shutil
import tempfile
import logging
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import subprocess
from nose.plugins.attrib import attr
from mockito import *

from yabiadmin.backend.fsbackend import FSBackend
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import Backend, Credential, BackendCredential, User

logger = logging.getLogger(__name__)

@attr("django")
class FSBackendTests(object):
    """File storage tests with real backends.

    Should do some testing where swiftclient.client.Connection is
    mocked out.

    Then should do some unit tests.
     - checking exception handling and that threads are properly terminated.
     - swapping bucket names and seeing how it breaks with cached bucket objects
    """

    scheme = None  # test classes should define this string
    hostname = None  # likewise
    backend_path = "/"
    creds = {
        "username": None,
        "password": None,
        "cert": None,
        "key": None,
    }
    base_uri = None

    @classmethod
    def setUpClass(cls):
        yabiusername = "demo"

        cls.yabiuser, cls.yabiuser_created = User.objects.get_or_create(
            user__username=yabiusername,
            defaults={})

        cls.credential = Credential.objects.create(
            user=cls.yabiuser,
            description="%s run %s" % (cls.__name__, datetime.datetime.now()),
            **cls.creds)

        cls.model_backend, cls.model_backend_created = Backend.objects.get_or_create(
            name=cls.__name__,
            scheme=cls.scheme,
            hostname=cls.hostname,
            path=cls.backend_path,
            port=None,
            defaults={
                "description": "Test run %s" % datetime.datetime.now(),
            })

        cls.bcs, cls.bcs_created = BackendCredential.objects.get_or_create(
            credential=cls.credential,
            backend=cls.model_backend,
            homedir="",
            visible=True,
        )

    @classmethod
    def tearDownClass(cls):
        if cls.bcs_created:
            cls.bcs.delete()
        if cls.model_backend_created:
            cls.model_backend.delete()
        cls.credential.delete()
        if cls.yabiuser_created:
            cls.yabiuser.delete()

    def setUp(self):
        self.be = FSBackend.create_backend_for_scheme(self.scheme)
        self.be.yabiusername = self.yabiuser.user.username  # this is required for FSBackend.set_cred()

    def get_uri(self, path=""):
        if self.creds.get("username", None):
            user_part = "%s@" % self.creds["username"]
        else:
            user_part = ""
        path_part = self.backend_path + path
        uri = "%s://%s%s%s" % (self.scheme, user_part, self.hostname, path_part)
        logger.debug("get_uri(%s) -> (%s, %s)", path, uri, path_part)
        return (uri, path_part)

    def test_ls(self):
        uri, path = self.get_uri("")
        ls = self.be.ls(uri)
        logger.debug("listing is %s" % repr(ls))
        self.assertTrue(path in ls)
        self.assertTrue("files" in ls[path])
        self.assertTrue("directories" in ls[path])

    def make_now_file(self):
        text = "%s\n" % datetime.datetime.now()
        tmp = tempfile.NamedTemporaryFile()
        tmp.write(text)
        tmp.flush()
        return tmp, text

    def test_ls_something(self):
        uri, path = self.get_uri("")

        tmp, text = self.make_now_file()

        dirname = "test_ls_something_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.be.mkdir(diruri)
        file1uri = "%s/now1.txt" % diruri
        self.be.upload_file(file1uri, tmp.name, mock())
        file2uri, _ = self.get_uri("now2.txt")
        self.be.upload_file(file2uri, tmp.name, mock())

        ls = self.be.ls(uri)
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])
        self.assertNotEqual(len(ls[path]["directories"]), 0)
        self.assertIn(dirname.rstrip("/"), [d[0] for d in ls[path]["directories"]])
        logger.debug("files are: %s" % str(ls[path]["files"]))
        self.assertEqual(len(ls[path]["files"]), 1)
        self.assertEqual(ls[path]["files"][0][0], "now2.txt")

        ls = self.be.ls(diruri)
        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])
        self.assertEqual(len(ls[dirpath]["files"]), 1)
        self.assertEqual(ls[dirpath]["files"][0][0], "now1.txt")

        self.be.rm(diruri)
        self.be.rm(file2uri)

    def test_ls_dir(self):
        uri, path = self.get_uri("testdir/")
        ls = self.be.ls(uri)
        logger.debug("listing is %s" % repr(ls))
        self.assertTrue(path in ls)
        self.assertTrue("files" in ls[path])
        self.assertTrue("directories" in ls[path])

        # # this relies on files existing in the bucket
        # self.assertEqual(len(ls[path]["files"]), 1)
        # self.assertEqual(len(ls[path]["directories"]), 0)

    @unittest.skip("doesn't work for swift")
    def test_ls_dir_no_exist(self):
        uri, path = self.get_uri("this_directory_no_exist/")
        ls = self.be.ls(uri)
        self.assertEqual(ls, {})

    def test_mkdir_ls_rmdir(self):
        path = "test_mkdir_ls_rmdir_%s" % os.getpid()
        test_dir, _ = self.get_uri(path)

        baseuri, basepath = self.get_uri("")

        def dirs(ls):
            return [d[0] for d in ls[basepath]["directories"]]

        ls = self.be.ls(baseuri)

        logger.debug("listing is %s" % str(ls))

        self.assertIn(basepath, ls)
        self.assertNotIn(path, dirs(ls))

        self.be.mkdir(test_dir)
        ls = self.be.ls(baseuri)

        self.assertIn(path, dirs(ls))

        # fixme: test that directories don't appear in ls["files"]

        self.be.mkdir(test_dir)
        ls = self.be.ls(baseuri)

        self.assertIn(path, dirs(ls))

        self.be.rm(test_dir)
        ls = self.be.ls(baseuri)

        self.assertNotIn(path, dirs(ls))


    def test_upload_temp_file(self):
        queue = mock()

        tmp, text = self.make_now_file()

        dirname = "test_upload_temp_file_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.be.mkdir(diruri)
        uri = "%s/now.txt" % diruri
        self.be.upload_file(uri, tmp.name, queue)

        tmp.close()

        # should have put a success value onto the queue
        verify(queue).put(0)

        queue = mock()

        tmp = tempfile.NamedTemporaryFile()
        self.be.download_file(uri, tmp.name, queue)

        verify(queue).put(0)

        self.assertEqual(open(tmp.name).read(), text)

        ls = self.be.ls(diruri)

        logger.debug("ls result 1: %s" % str(ls))

        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])

        self.assertEqual(len(ls[dirpath]["files"]), 1)
        self.assertEqual(ls[dirpath]["files"][0][0], "now.txt")  # file name
        self.assertEqual(ls[dirpath]["files"][0][1], len(text))  # file size

        self.be.rm(diruri)

        ls = self.be.ls(diruri)

        logger.debug("ls result 2: %s" % str(ls))

        self.assertEqual(ls[dirpath]["files"], [])

    def test_large_upload(self):
        name = "zeroes_%s.bin" % os.getpid()
        uri, path = self.get_uri(name)

        queue = mock()
        tmpname = tempfile.mktemp()
        os.mkfifo(tmpname)
        #self.addCleanup(os.unlink, tmpname)  # no dice for py2.6

        # drop 20 megs of zero into the pipe
        p = subprocess.Popen(["dd", "if=/dev/zero", "of=" + tmpname, "count=20", "bs=1M"])

        # fixme: why doesn't mkdir have credential setting?
        self.be.set_cred(uri)

        # copy in from the fifo
        self.be.upload_file(uri, tmpname, queue)

        # should have put a success value onto the queue
        verify(queue).put(0)

        # join up with defunct dd process
        p.wait()

        os.unlink(tmpname)

        # check that file was created and has the right size
        baseuri, basepath = self.get_uri("")
        ls = self.be.ls(baseuri)

        logger.debug("********* looking for %s" % basepath)
        logger.debug("ls result is %s" % str(ls))

        self.assertIn(basepath, ls)
        files = [f[0] for f in ls[basepath]["files"]]
        self.assertIn(name, files)
        size = [f[1] for f in ls[basepath]["files"] if f[0] == name][0]
        self.assertEqual(size, 20 * 1024 * 1024)  # 20M

        # delete the uploaded file
        self.be.rm(uri)

        # check that the file was deleted
        ls = self.be.ls(baseuri)
        self.assertIn(basepath, ls)
        self.assertNotIn(name, [f[0] for f in ls[basepath]["files"]])

class S3BackendTests(FSBackendTests, unittest.TestCase):
    """
    Tests against our yabitest bucket in the syd region. This bucket
    has a 1 day object expiration rule. If ci tests start to cost
    money (they shouldn't) then maybe the fakes3 server could be used
    instead.
    """

    scheme = "s3"
    hostname = "yabitest"
    backend_path = "/"
    creds = {
        "username": "backendtests",
        "password": "",
        "cert": "insert AWS_ACCESS_KEY_ID here",
        "key": "insert AWS_SECRET_ACCESS_KEY here",
    }
    base_uri = "s3://backendtests@yabitest"


class SwiftBackendTests(FSBackendTests, unittest.TestCase):
    scheme = "swift"
    hostname = "keystone.bioplatforms.com"
    backend_path = "/yabitest/test/"
    creds = {
        "username": "yabitest",
        "password": "yabitest",
        "cert": "",
        "key": "",
    }
    base_uri = "swift://yabitest@keystone.bioplatforms.com:443/yabitest/test"

class FileBackendTests(FSBackendTests, unittest.TestCase):
    scheme = "localfs"
    hostname = "localhost"
    creds = {
        "username": "ccg-user",
        "password": "",
        "cert": "",
        "key": "",
    }

    @classmethod
    def setUpClass(cls):
        cls.backend_path = tempfile.mkdtemp(prefix="yabitest-") + "/"
        cls.base_uri = "localfs://ccg-user@localhost/%s" % cls.backend_path.strip("/")
        # fixme: get rid of this setup, fix the ls_dir tests
        with open(os.path.join(cls.backend_path, "hello.txt"), "w") as f:
            f.write("hello\n")
        os.mkdir(os.path.join(cls.backend_path, "testdir"))
        with open(os.path.join(cls.backend_path, "testdir", "qwerty.txt"), "w") as f:
            f.write("asdf\n")
        super(FileBackendTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.backend_path)
        super(FileBackendTests, cls).tearDownClass()

    def test_upload_temp_file(self):
        self.skipTest("filebackend is different")

    def test_large_upload(self):
        self.skipTest("filebackend is different")

    def test_ls_something(self):
        self.skipTest("filebackend is different")

        # FileBackend doesn't have upload_file, so just put the files in
        self.be.upload_file = lambda *args: mock()

        os.mkdir(os.path.join(self.backend_path, "test_ls_something"))
        with open(os.path.join(self.backend_path, "test_ls_something", "now1.txt"), "w") as f:
            f.write("now1.txt\n")
        with open(os.path.join(self.backend_path, "now2.txt"), "w") as f:
            f.write("now2.txt\n")

        super(FileBackendTests, self).test_ls_something()

from yabiadmin.backend.swiftbackend import SwiftBackend

class SwiftURIParseTests(unittest.TestCase):
    def test_basic(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "file.txt")
        self.assertEqual(swift.path_part, "/tenant/bucket/file.txt")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_path(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "path/to/file.txt")
        self.assertEqual(swift.path_part, "/tenant/bucket/path/to/file.txt")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_prefix(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant/bucket")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_prefix_with_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/bucket/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant/bucket")  # fixme?

    def test_without_bucket(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_bucket_with_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/tenant/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "/tenant")  # fixme?

    def test_without_tenant(self):
        uri = "swift://username@keystone.bioplatforms.com:443"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, None)
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "")
        self.assertEqual(swift.uri, uri.replace(":443", "").replace("username@", ""))

    def test_without_tenant_with_slash(self):
        uri = "swift://username@keystone.bioplatforms.com:443/"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, None)
        self.assertEqual(swift.bucket, None)
        self.assertEqual(swift.prefix, "")
        self.assertEqual(swift.path_part, "")

    def test_without_username_port(self):
        uri = "swift://keystone.bioplatforms.com/tenant/bucket/path/to/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "path/to/file.txt")
        self.assertEqual(swift.path_part, "/tenant/bucket/path/to/file.txt")
        self.assertEqual(swift.uri, uri)

    def test_extra_slashes(self):
        uri = "swift://username@keystone.bioplatforms.com:443//tenant///bucket//path///to//file.txt///"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "tenant")
        self.assertEqual(swift.bucket, "bucket")
        self.assertEqual(swift.prefix, "path/to/file.txt/")
        self.assertEqual(swift.path_part, "/tenant/bucket/path/to/file.txt/")
        self.assertEqual(swift.uri, "swift://keystone.bioplatforms.com/tenant/bucket/path/to/file.txt/")

    def test_extra_extra_slashes(self):
        uri = "swift:///username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        self.assertRaises(ValueError, SwiftBackend.SwiftPath.parse, uri)

    def test_bad_scheme_spec(self):
        uri = "gopher://username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")

    def test_missing_scheme(self):
        uri = "//username@keystone.bioplatforms.com:443/tenant/bucket/path/to/file.txt"
        # fixme: maybe yabi code should raise ValueError instead of assertion
        self.assertRaises(AssertionError, SwiftBackend.SwiftPath.parse, uri)

    def test_very_long_uri(self):
        username = "lah" * 100
        hostname = ".".join(["keystone.bioplatforms.com"] * 100)
        path = "/qwerty/asdf/12345" * 100
        uri = "".join(["swift://", username, "@", hostname, path])
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://%s/v2.0/" % hostname)
        self.assertEqual(swift.tenant, "qwerty")
        self.assertEqual(swift.bucket, "asdf")
        self.assertEqual(swift.path_part, path)

    def test_unicode_uri(self):
        uri = "swift://keystone.bioplatforms.com/☃/☣/α/β/φ.txt"
        swift = SwiftBackend.SwiftPath.parse(uri)
        self.assertEqual(swift.keystone, "https://keystone.bioplatforms.com/v2.0/")
        self.assertEqual(swift.tenant, "☃")
        self.assertEqual(swift.bucket, "☣")
        self.assertEqual(swift.prefix, "α/β/φ.txt")
        self.assertEqual(swift.path_part, "/☃/☣/α/β/φ.txt")
        self.assertEqual(swift.uri, uri)

    # todo: maybe test url escaping
