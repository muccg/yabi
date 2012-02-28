import subprocess, os, shutil, glob, time
import config
import unittest
from collections import namedtuple

DEBUG = False
CONFIG_SECTION= os.environ.get('TEST_CONFIG_SECTION','quickstart_tests')
YABI_DIR = os.environ.get('YABI_DIR', '..')

def yabipath(relpath):
    return os.path.join(YABI_DIR, relpath)

class Result(object):
    def __init__(self, status, stdout, stderr, runner):
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.yabi = runner
        self._id = None

        if DEBUG:
            print self.status
            print self.stdout
            print self.stderr

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
        result = self.yabi.run('rm "%s"' % self.stageout_dir)
        if result.status != 0:
            print result.status
            print result.stdout
            print result.stderr

class StatusResult(Result):
    '''Decorates a normal Result with methods to access Worflow properties from yabish status output'''
    WORKFLOW_PROPERTIES = ['id', 'status', 'name', 'stageout', 'jobs']
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
            if name in StatusResult.WORKFLOW_PROPERTIES:
                props[name] = value
        return props

    def create_workflow_from_stdout(self):
        if self.status != 0:
            raise StandardException('yabish status returned non zero code')
        wfl_text, jobs_text = self.stdout.split('=== JOBS ===')
        jobs = self.extract_jobs(jobs_text)
        workflow_props = self.extract_workflow_properties(wfl_text)
        workflow_props['jobs'] = jobs
        workflow = StatusResult.Workflow(**workflow_props)
        return workflow

    @property
    def id(self):
        return self.result.id

    def cleanup(self):
        self.result.cleanup()


class Yabi(object):
    def __init__(self, yabish=yabipath('yabish/yabish')):
        self.conf = config.Configuration(section=CONFIG_SECTION)

        self.command = yabish + ' '
        if self.conf.yabiurl:
            self.command += '--yabi-url="%s"' % self.conf.yabiurl
        self.setup_data_dir()

    def setup_data_dir(self):

        # use data dir passed in from Hudson etc otherwise the one from conf
        if not os.environ.get('TEST_DATA_DIR'):
            self.test_data_dir = self.conf.test_data_dir
        else:
            self.test_data_dir = os.environ.get('TEST_DATA_DIR')

        if not os.path.exists(self.test_data_dir):
            assert False, "Test data directory does not exist: %s" % self.test_data_dir

    def run(self, args=''):
        command = self.command + ' ' + args
        prefix = '. %s && ' % yabipath('yabish/virt_yabish/bin/activate')
        cmd = subprocess.Popen(prefix + command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = cmd.wait()
        return Result(status, cmd.stdout.read(), cmd.stderr.read(), runner=self)

    def login(self, username=None, password=None):
        if not username:
            username = self.conf.username
        if not password:
            password = self.conf.password
        result = self.run('login %s %s' % (username, password))
        return 'Login unsuccessful' not in result.stderr

    def logout(self):
        result = self.run('logout')

    def purge(self):
        result = self.run('purge')

def run_yabiadmin_script(script, *args):
    prefix = 'cd %s && ' % yabipath('yabiadmin/yabiadmin')
    prefix += '. %s && ' % 'virt_yabiadmin/bin/activate'
    command = 'python manage.py runscript %s --pythonpath ../.. --script-args="%s"' % (script, ','.join(args))
    cmd = subprocess.Popen(prefix + command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    status = cmd.wait()
    out = cmd.stdout.read()
    err = cmd.stdout.read()
    if status != 0 or err:
        print 'run_yabiadmin_script failed!'
        print 'Command was: ' + prefix + command
        print 'STATUS was: %d' % status
        print 'STDERR was: \n' + err
        print 'STDOUT was: \n' + out
        raise StandardError('run_yabiadmin_script FAILED')


class YabiTestCase(unittest.TestCase):

    runner = Yabi

    @property
    def classname(self):
        return self.__module__ + '.' + self.__class__.__name__

    def _setup_admin(self):
        if 'setUpAdmin' in dir(self.__class__):
            run_yabiadmin_script('run_class_method', self.classname, 'setUpAdmin')

    def _teardown_admin(self):
        if 'tearDownAdmin' in dir(self.__class__):
            run_yabiadmin_script('run_class_method', self.classname, 'tearDownAdmin')

    def setUp(self):
        self.yabi = self.runner()
        self.yabi.login()
        self._setup_admin()

    def tearDown(self):
        self.yabi.logout()
        self.yabi.purge()
        self._teardown_admin()


class FileUtils(object):
    def setUp(self):
        self.tempfiles = []

    def tearDown(self):
        for f in self.tempfiles:
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.unlink(f)

    def create_tempfile(self, size = 1024, parentdir = None):
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
        if parentdir is not None:
            extra_args = {'dir': parentdir}
        with tempfile.NamedTemporaryFile(prefix='fake_fasta_', suffix='.fa', delete=False, **extra_args) as f:
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

    def create_tempdir(self):
        import tempfile
        dirname = tempfile.mkdtemp()
        self.tempfiles.append(dirname)
        return dirname
        
    def run_cksum_locally(self, filename):
        import subprocess
        cmd = subprocess.Popen('cksum %s' % filename, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = cmd.wait()
        assert status == 0, 'ERROR: ' + cmd.stderr.read()
        output = cmd.stdout.read()
        our_line = filter(lambda l: filename in l, output.split("\n"))[0]
        expected_cksum, expected_size, rest = our_line.split()
        return expected_cksum, expected_size
