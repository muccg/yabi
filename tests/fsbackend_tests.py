import datetime
import os
import shutil
import tempfile
import logging
from django.utils import unittest
import subprocess
from nose.plugins.attrib import attr

from yabiadmin.backend.fsbackend import FSBackend
from django.contrib.auth.models import User as DjangoUser
from yabiadmin.yabi.models import Backend, Credential, BackendCredential, User

from .request_test_base import RequestTest
from .fakes3 import fakes3_setup
from .fixture_helpers.admin import private_test_ssh_key, authorise_test_ssh_key, cleanup_test_ssh_key

logger = logging.getLogger(__name__)

getname = lambda entry: entry[0]

from tests.support import conf
TMPDIR = conf.tmpdir

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
        from tests.support import conf
        cls.hostname, cls.backend_path, cls.fscreds = cls.backend_info(conf)
        cls.backend_setup(conf)

    @classmethod
    def backend_setup(cls, conf):
        cls.yabiuser, cls.yabiuser_created = User.objects.get_or_create(
            user__username=conf.yabiusername,
            defaults={})

        cls.credential = Credential.objects.create(
            user=cls.yabiuser,
            description="%s run %s" % (cls.__name__, datetime.datetime.now()),
            **cls.fscreds)

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
        cls.backend_cleanup()

    @classmethod
    def backend_cleanup(cls):
        if cls.yabiuser_created:
            cls.yabiuser.delete()
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
        fscreds = {
            "username": None,
            "password": None,
            "key": None,
        }
        return hostname, backend_path, fscreds

    def get_uri(self, path=""):
        if self.fscreds.get("username", None):
            user_part = "%s@" % self.fscreds["username"]
        else:
            user_part = ""
        path_part = self.backend_path + path
        uri = "%s://%s%s%s" % (self.scheme, user_part, self.hostname, path_part)
        logger.debug("get_uri(%s) -> (%s, %s)", path, uri, path_part)
        return (uri, path_part)

    def getcmd(self, cmd, uri, isjson=True, expected_status=200):
        cmd_uri = self.fscmd(cmd, uri)
        logger.debug("GET %s" % cmd_uri)
        r = self.session.get(cmd_uri)
        #logger.info("response to %s uri=%s is: %s" % (cmd, uri, r.text))
        self.assertEqual(r.status_code, expected_status)
        return r.json() if isjson else r.text

    def getcmdok(self, cmd, uri):
        response_text = self.getcmd(cmd, uri, isjson=False)
        self.assertEqual(response_text, "OK")

    def upload_file(self, uri, name, filename):
        files = {'file': (name, open(filename, 'rb'))}
        logger.debug("about to upload to %s: %s" % (self.fscmd("put", uri), str(files)))
        r = self.session.post(url=self.fscmd("put", uri), files=files)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {
            "message": "no message",
            "level": "success",
            "num_fail": 0,
            "num_success": len(files),
        })

    def download_file(self, uri, filename):
        chunk_size = 4000
        r = self.session.get(url=self.fscmd("get", uri), stream=True)
        self.assertEqual(r.status_code, 200)
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)

    def test_ls(self):
        uri, path = self.get_uri("")
        ls = self.getcmd("ls", uri)
        logger.debug("listing is %s" % repr(ls))
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])

    def make_now_file(self):
        text = "%s\n" % datetime.datetime.now()
        tmp = tempfile.NamedTemporaryFile(dir=TMPDIR)
        tmp.write(text)
        tmp.flush()
        return tmp, text

    def test_ls_something(self):
        uri, path = self.get_uri("")

        tmp, text = self.make_now_file()

        dirname = "test_ls_something_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.getcmdok("mkdir", diruri)
        file1uri = "%s/now1.txt" % diruri
        self.upload_file(file1uri, "now1.txt", tmp.name)
        file2uri, _ = self.get_uri("now2.txt")
        self.upload_file(file2uri, "now2.txt", tmp.name)

        ls = self.getcmd("ls", uri)
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])
        self.assertNotEqual(len(ls[path]["directories"]), 0)
        self.assertIn(dirname.rstrip("/"), [d[0] for d in ls[path]["directories"]])
        logger.debug("files are: %s" % str(ls[path]["files"]))
        self.assertIn("now2.txt", map(getname, ls[path]["files"]))

        ls = self.getcmd("ls", diruri)
        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])
        self.assertIn("now1.txt", map(getname, ls[dirpath]["files"]))

        self.getcmdok("rm", diruri)
        self.getcmdok("rm", file2uri)

    def test_ls_dir(self):
        uri, path = self.get_uri("testdir/")
        self.getcmdok("mkdir", uri)
        ls = self.getcmd("ls", uri)
        logger.debug("listing is %s" % repr(ls))
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])

        # # this relies on files existing in the bucket
        # self.assertEqual(len(ls[path]["files"]), 1)
        # self.assertEqual(len(ls[path]["directories"]), 0)

    def test_ls_dir_no_exist(self):
        uri, path = self.get_uri("this_directory_no_exist/")
        ls = self.getcmd("ls", uri)
        self.assertEqual(ls, {})

    def test_mkdir_ls_rmdir(self):
        path = "test_mkdir_ls_rmdir_%s" % os.getpid()
        test_dir, _ = self.get_uri(path)

        baseuri, basepath = self.get_uri("")

        def dirs(ls):
            return [d[0] for d in ls[basepath]["directories"]]

        ls = self.getcmd("ls", baseuri)

        logger.debug("listing is %s" % str(ls))

        self.assertIn(basepath, ls)
        self.assertNotIn(path, dirs(ls))

        self.getcmdok("mkdir", test_dir)
        ls = self.getcmd("ls", baseuri)

        self.assertIn(path, dirs(ls))

        # fixme: test that directories don't appear in ls["files"]

        self.getcmdok("mkdir", test_dir)
        ls = self.getcmd("ls", baseuri)

        self.assertIn(path, dirs(ls))

        self.getcmdok("rm", test_dir)
        ls = self.getcmd("ls", baseuri)

        self.assertNotIn(path, dirs(ls))


    def test_upload_temp_file(self):
        tmp, text = self.make_now_file()

        logger.debug("uploading...")

        dirname = "test_upload_temp_file_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.getcmdok("mkdir", diruri)
        uri = "%s/now.txt" % diruri
        self.upload_file(uri, "now.txt", tmp.name)

        tmp.close()

        logger.debug("downloading...")

        tmp = tempfile.NamedTemporaryFile(dir=TMPDIR)
        self.download_file(uri, tmp.name)

        self.assertEqual(open(tmp.name).read(), text)

        ls = self.getcmd("ls", diruri)

        logger.debug("ls result 1: %s" % str(ls))

        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])

        self.assertEqual(len(ls[dirpath]["files"]), 1)
        self.assertEqual(ls[dirpath]["files"][0][0], "now.txt")  # file name
        self.assertEqual(ls[dirpath]["files"][0][1], len(text))  # file size

        self.getcmdok("rm", diruri)


    def test_large_upload(self):
        baseuri, basepath = self.get_uri("")
        name = "zeroes_%s.bin" % os.getpid()
        uri, path = self.get_uri(name)

        tmpname = tempfile.mktemp()
        os.mkfifo(tmpname)
        self.addCleanup(os.unlink, tmpname)

        # drop 20 megs of zero into the pipe
        p = subprocess.Popen(["dd", "if=/dev/zero", "of=" + tmpname, "count=20", "bs=1M"])

        # copy in from the fifo
        self.upload_file(baseuri, name, tmpname)

        # join up with defunct dd process
        p.wait()

        # check that file was created and has the right size
        ls = self.getcmd("ls", baseuri)

        self.assertIn(basepath, ls)
        files = [f[0] for f in ls[basepath]["files"]]
        self.assertIn(name, files)
        size = [f[1] for f in ls[basepath]["files"] if f[0] == name][0]
        self.assertEqual(size, 20 * 1024 * 1024)  # 20M

        # delete the uploaded file
        self.getcmdok("rm", uri)

        # check that the file was deleted
        ls = self.getcmd("ls", baseuri)
        self.assertIn(basepath, ls)
        self.assertNotIn(name, [f[0] for f in ls[basepath]["files"]])

    def test_ls_file(self):
        # Running ls on a single file allows yabi to get its file size and
        # mod-time, etc.
        tmp, text = self.make_now_file()

        dirname = "test_ls_file_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.getcmdok("mkdir", diruri)
        fileuri, filepath = self.get_uri(dirname + "now.txt")
        self.upload_file(fileuri, "now.txt", tmp.name)

        ls = self.getcmd("ls", fileuri)
        logger.debug("ls result: %s" % str(ls))
        self.assertIn(filepath, ls)
        self.assertIn("files", ls[filepath])
        self.assertIn("directories", ls[filepath])
        self.assertEqual(ls[filepath]["directories"], [])
        self.assertEqual(map(getname, ls[filepath]["files"]), ["now.txt"])
        self.assertEqual(ls[filepath]["files"][0][1], len(text))

        self.getcmdok("rm", fileuri)
        self.getcmdok("rm", diruri)

    def test_ls_prefix(self):
        dirname = "test_ls_prefix_%s/" % os.getpid()
        diruri, dirpath = self.get_uri(dirname)
        self.getcmdok("mkdir", diruri)

        testuri, testpath = self.get_uri(dirname + "prefix")

        self.getcmdok("mkdir", testuri)
        self.getcmdok("mkdir", testuri + "_test/")

        ls = self.getcmd("ls", diruri)
        self.assertIn(dirpath, ls)
        self.assertIn("files", ls[dirpath])
        self.assertIn("directories", ls[dirpath])
        self.assertEqual(map(getname, ls[dirpath]["files"]), [])
        self.assertEqual(map(getname, ls[dirpath]["directories"]),
                         ["prefix", "prefix_test"])

        ls = self.getcmd("ls", testuri)
        testpath = testpath + "/"  # expect that the slash will be added by ls()
        self.assertIn(testpath, ls)
        self.assertIn("files", ls[testpath])
        self.assertIn("directories", ls[testpath])
        self.assertEqual(map(getname, ls[testpath]["files"]), [])
        self.assertEqual(map(getname, ls[testpath]["directories"]), [])

        self.getcmdok("rm", testuri)
        self.getcmdok("rm", testuri + "_test")
        self.getcmdok("rm", diruri)

    def test_rm_prefix(self):
        uri, path = self.get_uri("")

        # this test makes sure deleting a file won't result in
        # deletion of all files which have its name as a prefix
        tmp, text = self.make_now_file()
        files = ["test_rm_prefix_file1", "test_rm_prefix_file2",
                 "test_rm_prefix_file3", "test_rm_prefix"]
        for f in files:
            self.upload_file(uri + f, f, tmp.name)
        self.getcmdok("mkdir", uri + "test_rm_prefix_dir")

        # test that the files were created
        ls = self.getcmd("ls", uri)
        self.assertIn(path, ls)
        self.assertIn("files", ls[path])
        self.assertIn("directories", ls[path])
        for f in files:
            self.assertIn(f, map(getname, ls[path]["files"]))
        self.assertIn("test_rm_prefix_dir", map(getname, ls[path]["directories"]))

        # remove a file which prefixes the other files
        self.getcmdok("rm", uri + "test_rm_prefix")

        # test that only one file was removed
        ls = self.getcmd("ls", uri)
        for f in files[:-1]:
            self.assertIn(f, map(getname, ls[path]["files"]))
        self.assertIn("test_rm_prefix_dir", map(getname, ls[path]["directories"]))

        # clean up
        for f in files[:-1] + ["test_rm_prefix_dir"]:
            self.getcmdok("rm", uri + f)

    def test_download_file_no_exist(self):
        uri, path = self.get_uri("this_file_no_exist_%s.txt" % os.getpid())
        r = self.session.get(url=self.fscmd("get", uri), stream=True)
        self.assertEqual(r.status_code, 500)

    @staticmethod
    def _make_noperm_file(dirname):
        path = os.path.join(dirname, "noperms.txt")
        with open(path, "w") as f:
            f.write("you shouldn't see this\n")
        os.chmod(path, 0)

    def test_download_file_eperm(self):
        uri, path = self.get_uri("noperms.txt")
        r = self.session.get(url=self.fscmd("get", uri), stream=True)
        self.assertEqual(r.status_code, 500)

    # def test_large_download(self):
    #     pass
    #
    # def test_ls_recursive(self):
    #     pass


@attr("s3", "backend")
class S3BackendTests(FSBackendTests, RequestTest):
    """
    Tests against either of:
    1. Our yabitest bucket in the syd region. This bucket
       has a 1 day object expiration rule. Put s3_bucket=yabitest in
       tests.conf.
    2. A fakes3 server launched by the test class. Fakes3 isn't quite
       good enough so a lot of tests are disabled. Put
       s3_bucket=fakes3 in tests.conf.
    """

    scheme = "s3"

    @classmethod
    def backend_info(cls, conf):
        # test classes need to redefine these
        hostname = conf.s3_bucket
        backend_path = "/"
        fscreds = {
            "username": "backendtests",
            "password": conf.aws_secret_access_key,
            "key": conf.aws_access_key_id,
        }
        return hostname, backend_path, fscreds

    def setUp(self):
        self.skipTest('S3 tests currently disabled in docker containers')
        RequestTest.setUp(self)
        #fakes3_setup(self, "fakes3")

    def skip_if_fakes3(self, msg=None):
        if self.hostname == "fakes3":
            self.skipTest(msg or "test doesn't work with fakes3")

    def test_ls(self):
        self.skipTest("doesn't work for s3")

    def test_ls_dir(self):
        self.skipTest("doesn't work for s3")

    def test_ls_dir_no_exist(self):
        self.skipTest("doesn't work for s3")

    def test_download_file_eperm(self):
        # can't test on this backend
        pass

    def test_large_upload(self):
        self.skip_if_fakes3("multipart upload doesn't work with fakes3")
        super(S3BackendTests, self).test_large_upload()

    def test_ls_prefix(self):
        self.skip_if_fakes3()
        super(S3BackendTests, self).test_ls_prefix()

    def test_ls_something(self):
        self.skip_if_fakes3()
        super(S3BackendTests, self).test_ls_something()

    def test_mkdir_ls_rmdir(self):
        self.skip_if_fakes3()
        super(S3BackendTests, self).test_mkdir_ls_rmdir()

    def test_rm_prefix(self):
        self.skip_if_fakes3()
        super(S3BackendTests, self).test_rm_prefix()

    def getcmdok(self, cmd, uri):
        if cmd == "rm" and self.hostname == "s3test":
            logger.warning("rm disabled on fakes3")
        else:
            return super(S3BackendTests, self).getcmdok(cmd, uri)

@attr("swift", "backend", "external_service")
class SwiftBackendTests(FSBackendTests, RequestTest):
    scheme = "swift"

    @classmethod
    def backend_info(cls, conf):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        cls.bucket_name = "%s-%s" % (conf.swift_bucket, timestamp)
        cls.swiftenv = {
            "OS_USERNAME": conf.swift_username,
            "OS_PASSWORD": conf.swift_password,
            "OS_AUTH_URL": "https://%s/v2.0/" % conf.keystone_host,
            "OS_TENANT_NAME": conf.swift_tenant,
            #"OS_REGION": None,
        }
        hostname = conf.keystone_host
        backend_path = "/%s/%s/" % (conf.swift_tenant, cls.bucket_name)
        fscreds = {
            "username": conf.swift_username,
            "password": conf.swift_password,
            "key": "",
        }
        return hostname, backend_path, fscreds

    def test_ls_dir_no_exist(self):
        self.skipTest("doesn't work for swift")

    def test_download_file_eperm(self):
        # can't test on this backend
        pass

    @classmethod
    def setUpClass(cls):
        super(SwiftBackendTests, cls).setUpClass()
        cls.swiftclient("post", cls.bucket_name)

    @classmethod
    def tearDownClass(cls):
        super(SwiftBackendTests, cls).tearDownClass()
        cls.swiftclient("delete", cls.bucket_name)

    @classmethod
    def swiftclient(cls, *args):
        env = dict(os.environ)
        env.update(cls.swiftenv)
        cmd = ["swift"] + list(args)
        logger.debug("Running: %s" % " ".join(cmd))
        subprocess.check_call(cmd, env=env)

@attr("backend")
class FileBackendTests(FSBackendTests, RequestTest):
    scheme = "localfs"

    @classmethod
    def backend_info(cls, conf):
	# AH check this
        hostname = "localhost"
        fscreds = {
            "username": conf.yabiusername,
            "password": "",
            "key": "",
        }
        return hostname, cls.backend_path, fscreds

    @classmethod
    def setUpClass(cls):
        cls.backend_path = tempfile.mkdtemp(dir=TMPDIR, prefix="yabitest-") + "/"
        cls._make_noperm_file(cls.backend_path)
        super(FileBackendTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(FileBackendTests, cls).tearDownClass()
        shutil.rmtree(cls.backend_path)

    def test_download_file_eperm(self):
        self.skipTest("Can't make ccgstaff not being able to access a file under /data")

@attr("backend")
class SFTPBackendTests(FSBackendTests, RequestTest):
    scheme = "sftp"

    @classmethod
    def backend_info(cls, conf):
        hostname = "sshtest"

        fscreds = {
            "username": "root",
            "password": "root",
        }
        return hostname, cls.backend_path, fscreds

    @classmethod
    def setUpClass(cls):
        cls.backend_path = tempfile.mkdtemp(dir=TMPDIR, prefix="yabitest-") + "/"
        cls._make_noperm_file(cls.backend_path)
        authorise_test_ssh_key()
        super(SFTPBackendTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(SFTPBackendTests, cls).tearDownClass()
        cleanup_test_ssh_key()
        shutil.rmtree(cls.backend_path)

    def test_ls_prefix(self):
        self.skipTest("sftp backend is losing the trailing slash")

    def test_download_file_eperm(self):
        self.skipTest("sftp currently running as root, fix later")
