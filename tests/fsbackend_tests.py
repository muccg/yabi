import datetime
import os
import shutil
import tempfile
import logging
from django.utils import unittest
import subprocess
from nose.plugins.attrib import attr
from mockito import *

from yabiadmin.backend.fsbackend import FSBackend
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import Backend, Credential, BackendCredential, User

logger = logging.getLogger(__name__)

getname = lambda entry: entry[0]

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

    @classmethod
    def setUpClass(cls):
        yabiusername = "demo"

        from tests.support import conf

        cls.hostname, cls.backend_path, cls.creds = cls.backend_info(conf)

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

    @classmethod
    def backend_info(cls, conf):
        # test classes need to redefine these
        hostname = None
        backend_path = "/"
        creds = {
            "username": None,
            "password": None,
            "cert": None,
            "key": None,
        }
        return hostname, backend_path, creds

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
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])

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
        self.assertIn("now2.txt", map(getname, ls[path]["files"]))

        ls = self.be.ls(diruri)
        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])
        self.assertIn("now1.txt", map(getname, ls[dirpath]["files"]))

        self.be.rm(diruri)
        self.be.rm(file2uri)

    def test_ls_dir(self):
        uri, path = self.get_uri("testdir/")
        ls = self.be.ls(uri)
        logger.debug("listing is %s" % repr(ls))
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])

        # # this relies on files existing in the bucket
        # self.assertEqual(len(ls[path]["files"]), 1)
        # self.assertEqual(len(ls[path]["directories"]), 0)

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
        verify(queue).put(True)

        queue = mock()

        tmp = tempfile.NamedTemporaryFile()
        self.be.download_file(uri, tmp.name, queue)

        verify(queue).put(True)

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

        # fixme: this kills the swift and s3 backend tests
        if self.scheme not in ("swift", "s3"):
            self.assertEqual(ls, {})

    def test_large_upload(self):
        name = "zeroes_%s.bin" % os.getpid()
        uri, path = self.get_uri(name)

        queue = mock()
        tmpname = tempfile.mktemp()
        os.mkfifo(tmpname)
        self.addCleanup(os.unlink, tmpname)

        # drop 20 megs of zero into the pipe
        p = subprocess.Popen(["dd", "if=/dev/zero", "of=" + tmpname, "count=20", "bs=1M"])

        # fixme: why doesn't mkdir have credential setting?
        self.be.set_cred(uri)

        # copy in from the fifo
        self.be.upload_file(uri, tmpname, queue)

        # should have put a success value onto the queue
        verify(queue).put(True)

        # join up with defunct dd process
        p.wait()

        # check that file was created and has the right size
        baseuri, basepath = self.get_uri("")
        ls = self.be.ls(baseuri)

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

    def test_ls_file(self):
        # Running ls on a single file allows yabi to get its file size and
        # mod-time, etc.
        tmp, text = self.make_now_file()

        dirname = "test_ls_file_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.be.mkdir(diruri)
        fileuri, filepath = self.get_uri(dirname + "now.txt")
        self.be.upload_file(fileuri, tmp.name, mock())

        ls = self.be.ls(fileuri)
        self.assertIn(filepath, ls)
        self.assertIn("files", ls[filepath])
        self.assertIn("directories", ls[filepath])
        self.assertEqual(ls[filepath]["directories"], [])
        self.assertEqual(map(getname, ls[filepath]["files"]), ["now.txt"])
        self.assertEqual(ls[filepath]["files"][0][1], len(text))

        self.be.rm(fileuri)
        self.be.rm(diruri)

    def test_ls_prefix(self):
        dirname = "test_ls_prefix_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.be.mkdir(diruri)

        testuri, testpath = self.get_uri(dirname + "prefix")

        self.be.mkdir(testuri)
        self.be.mkdir(testuri + "_test/")

        ls = self.be.ls(diruri)
        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])
        self.assertIn("directories", ls[dirpath])
        self.assertEqual(map(getname, ls[dirpath]["files"]), [])
        self.assertEqual(map(getname, ls[dirpath]["directories"]),
                         ["prefix", "prefix_test"])

        ls = self.be.ls(testuri)
        testpath = testpath + "/"  # expect that the slash will be added by ls()
        self.assertIn(testpath, ls)
        self.assertIn("files", ls[testpath])
        self.assertIn("directories", ls[testpath])
        self.assertEqual(map(getname, ls[testpath]["files"]), [])
        self.assertEqual(map(getname, ls[testpath]["directories"]), [])

        self.be.rm(testuri)
        self.be.rm(testuri + "_test")
        self.be.rm(diruri)

    def test_rm_prefix(self):
        uri, path = self.get_uri("")

        # fixme: shouldn't have to do this
        self.be.set_cred(uri)

        # this test makes sure deleting a file won't result in
        # deletion of all files which have its name as a prefix
        tmp, text = self.make_now_file()
        files = ["test_rm_prefix_file1", "test_rm_prefix_file2",
                 "test_rm_prefix_file3", "test_rm_prefix"]
        for f in files:
            self.be.upload_file(uri + f, tmp.name, mock())
        self.be.mkdir(uri + "test_rm_prefix_dir")

        # test that the files were created
        ls = self.be.ls(uri)
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])
        for f in files:
            self.assertIn(f, map(getname, ls[path]["files"]))
        self.assertIn("test_rm_prefix_dir", map(getname, ls[path]["directories"]))

        # remove a file which prefixes the other files
        self.be.rm(uri + "test_rm_prefix")

        # test that only one file was removed
        ls = self.be.ls(uri)
        for f in files[:-1]:
            self.assertIn(f, map(getname, ls[path]["files"]))
        self.assertIn("test_rm_prefix_dir", map(getname, ls[path]["directories"]))

        # clean up
        for f in files[:-1] + ["test_rm_prefix_dir"]:
            self.be.rm(uri + f)

    # def test_large_download(self):
    #     pass
    #
    # def test_ls_recursive(self):
    #     pass


@attr("s3", "backend")
class S3BackendTests(FSBackendTests, unittest.TestCase):
    """
    Tests against our yabitest bucket in the syd region. This bucket
    has a 1 day object expiration rule. If ci tests start to cost
    money (they shouldn't) then maybe the fakes3 server could be used
    instead.
    """

    scheme = "s3"

    @classmethod
    def backend_info(cls, conf):
        # test classes need to redefine these
        hostname = conf.s3_bucket
        backend_path = "/"
        creds = {
            "username": "backendtests",
            "password": "",
            "cert": conf.aws_access_key_id,
            "key": conf.aws_secret_access_key,
        }
        return hostname, backend_path, creds

    def test_ls_dir_no_exist(self):
        self.skipTest("doesn't work for s3")

    def test_ls_prefix(self):
        self.skipTest("s3 backend not returning same as other backends")

@attr("swift", "backend")
class SwiftBackendTests(FSBackendTests, unittest.TestCase):
    scheme = "swift"

    @classmethod
    def backend_info(cls, conf):
        hostname = conf.keystone_host
        backend_path = "/%s/%s/" % (conf.swift_tenant, conf.swift_bucket)
        creds = {
            "username": conf.swift_username,
            "password": conf.swift_password,
            "cert": "",
            "key": "",
        }
        return hostname, backend_path, creds

    def test_ls_dir_no_exist(self):
        self.skipTest("doesn't work for swift")

@attr("backend")
class FileBackendTests(FSBackendTests, unittest.TestCase):
    scheme = "localfs"

    @classmethod
    def backend_info(cls, conf):
        hostname = "localhost"
        creds = {
            "username": "ccg-user",
            "password": "",
            "cert": "",
            "key": "",
        }
        return hostname, cls.backend_path, creds

    @classmethod
    def setUpClass(cls):
        cls.backend_path = tempfile.mkdtemp(prefix="yabitest-") + "/"
        # fixme: get rid of this setup, fix the ls_dir tests
        with open(os.path.join(cls.backend_path, "hello.txt"), "w") as f:
            f.write("hello\n")
        os.mkdir(os.path.join(cls.backend_path, "testdir"))
        with open(os.path.join(cls.backend_path, "testdir", "qwerty.txt"), "w") as f:
            f.write("asdf\n")
        super(FileBackendTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(FileBackendTests, cls).tearDownClass()
        shutil.rmtree(cls.backend_path)
