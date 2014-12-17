from __future__ import print_function
import subprocess, os, shutil, glob, time
import sys
from . import config
import unittest
from collections import namedtuple
from contextlib import contextmanager, nested
from six.moves import filter
import logging
from StringIO import StringIO

conf = config.Configuration(os.environ.get("TEST_CONFIG_FILE") or None,
                            os.environ.get("YABI_CONFIG") or None)

logger = logging.getLogger(__name__)

def json_path(name):
    return os.path.join(conf.jsondir, name + '.json')

def all_items(fn, items):
    for i in items:
        if not fn(i):
            return False
    return True

class Result(object):
    def __init__(self, status, stdout, stderr, runner):
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.yabi = runner
        self._id = None

        logging.debug("Result (%s)(%s)(%s)"%(self.status, self.stdout, self.stderr))

    @property
    def id(self):
        if not self._id:
            for line in self.stdout.split("\n"):
                if "Running your job on the server. Id: " in line:
                    rest, id = line.rsplit(' ', 1)
                    self._id = id
                    return self._id
            raise ValueError("Id not found in stdout: %s", self.stdout)
        return self._id

    def cleanup(self):
        result = self.yabi.run(['rm', self.stageout_dir])
        if result.status != 0:
            print("Result (%s)(%s)(%s)"%(result.status, result.stdout, result.stderr))

class StatusResult(Result):
    '''Decorates a normal Result with methods to access Worflow properties from yabish status output'''
    WORKFLOW_PROPERTIES = ['id', 'status', 'name', 'stageout', 'jobs', 'tags', 'created_on', 'last_modified_on']
    Workflow = namedtuple('Workflow', WORKFLOW_PROPERTIES)
    Job = namedtuple('Job', ['id', 'status', 'toolname'])

    def __init__(self, result):
        self.result = result
        self.status = self.result.status
        self.stdout = self.result.stdout
        self.stderr = self.result.stderr
        self.yabi = self.result.yabi

        self.workflow = self.create_workflow_from_stdout()

    def extract_jobs(self, jobs_text):
        jobs_text = jobs_text.split("\n")[3:] # skip header and separator
        jobs = []
        for line in filter(lambda l: l.strip(), jobs_text):
            jobs.append(StatusResult.Job(*line.split()))
        return jobs

    def extract_workflow_properties(self, wfl_text):
        props = dict.fromkeys(StatusResult.WORKFLOW_PROPERTIES)
        for line in filter(lambda l: l.strip(), wfl_text.split("\n")):
            name, value = line.split(":", 1)
            props[name] = value
        return props

    def create_workflow_from_stdout(self):
        if self.status != 0:
            raise Exception('yabish status returned non zero code')
        text_before, our_text = self.stdout.split('=== STATUS ===')
        wfl_text, jobs_text = our_text.split('=== JOBS ===')
        jobs = self.extract_jobs(jobs_text)
        workflow_props = self.extract_workflow_properties(wfl_text)
        workflow_props['jobs'] = jobs
        print(workflow_props)
        workflow = StatusResult.Workflow(**workflow_props)
        return workflow

    @property
    def id(self):
        return self.result.id

    def cleanup(self):
        self.result.cleanup()


class YabiTimeoutException(Exception):
    pass

class Yabi(object):

    def __init__(self):
        self.shargs = ['--yabi-url', conf.yabiurl] if conf.yabiurl else []
        self.shargs.append('--yabi-debug')
        self.setup_data_dir()

    def setup_data_dir(self):
        self.test_data_dir = conf.testdatadir

        if not os.path.exists(self.test_data_dir):
            assert False, "Test data directory does not exist: %s" % self.test_data_dir

    def run(self, args=[]):
        args = ["yabish"] + self.shargs + args
        logger.debug(" ".join(args))
        patches = (sys_patch("argv", args), sys_patch("stdout", StringIO()),
                   sys_patch("stderr", StringIO()),
                   sys_patch("stdin", open("/dev/null")))
        from yabishell.yabish import main
        with nested(*patches):
            try:
                status = main()
            except SystemExit as e:
                status = e.code
            return Result(status or 0, sys.stdout.getvalue(), sys.stderr.getvalue(), runner=self)

    def login(self, username=conf.yabiusername, password=conf.yabipassword):
        result = self.run(['login', username, password])
        return 'Login unsuccessful' not in result.stderr

    def logout(self):
        result = self.run(['logout'])

    def purge(self):
        result = self.run(['purge'])

@contextmanager
def sys_patch(attr, patch):
    orig_attr = getattr(sys, attr)
    setattr(sys, attr, patch)
    try:
        yield
    finally:
        setattr(sys, attr, orig_attr)

class YabiTestCase(unittest.TestCase):

    runner = Yabi

    @property
    def classname(self):
        return self.__module__ + '.' + self.__class__.__name__

    def setUp(self):
        self.yabi = self.runner()
        self.yabi.login()

    def tearDown(self):
        self.yabi.logout()
        self.yabi.purge()

class FileUtils(object):
    def setUp(self):
        self.tempfiles = []

    def tearDown(self):
        for f in self.tempfiles:
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.unlink(f)

    def create_tempfile(self, size=1024, parentdir=conf.tmpdir, fname_prefix="fake_fasta_"):
        import tempfile
        import stat
        import random as rand
        CHUNK_SIZE = 1024
        def data(length, random=False):
            if not random:
                return "a" * length
            data = ""
            for i in range(length):
                data += rand.choice('abcdefghijklmnopqrstuvwxyz')
            return data
        extra_args = {}
        if parentdir is not None:
            extra_args = {'dir': parentdir}
        with tempfile.NamedTemporaryFile(prefix=fname_prefix, suffix='.fa', delete=False, **extra_args) as f:
            chunks = size / CHUNK_SIZE
            remaining = size % CHUNK_SIZE
            for i in range(chunks):
                if i == 0:
                    f.write(data(1024, random=True))
                else:
                    f.write(data(1024))
            f.write(data(remaining,random=True))
        filename = f.name

        self.tempfiles.append(filename)
        return filename

    def create_tempdir(self, parentdir = conf.tmpdir):
        import tempfile
        dirname = tempfile.mkdtemp(dir=parentdir)
        self.tempfiles.append(dirname)
        return dirname

    def delete_on_exit(self, filename):
        self.tempfiles.append(filename)

    def run_cksum_locally(self, filename):
        import subprocess
        from pipes import quote
        cmd = subprocess.Popen('cksum %s' % quote(filename), shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, err = cmd.communicate()
        assert cmd.returncode == 0, 'ERROR: ' + err
        out = out.decode('utf-8')
        our_line = list(filter(lambda l: filename in l, out.split("\n")))[0]
        expected_cksum, expected_size, rest = our_line.split(None, 2)
        return expected_cksum, expected_size
