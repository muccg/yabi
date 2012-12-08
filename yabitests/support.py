import subprocess, os, shutil, glob, time
import config
import unittest
from collections import namedtuple

DEBUG = True
CONFIG_SECTION= os.environ.get('TEST_CONFIG','dev_mysql')
conf = config.Configuration(section=CONFIG_SECTION)

def yabipath(relpath):
    return os.path.join(conf.yabidir, relpath)

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

        if DEBUG:
            print "Result (%s)(%s)(%s)"%(self.status, self.stdout, self.stderr)

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
            print "Result (%s)(%s)(%s)"%(result.status, result.stdout, result.stderr)

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


class YabiTimeoutException(Exception):
    pass

class Yabi(object):
    TIMEOUT = conf.timeout

    def __init__(self):
        yabish = yabipath(conf.yabish) 

        self.command = yabish + ' '
        if conf.yabiurl:
            self.command += '--yabi-url="%s"' % conf.yabiurl
        self.setup_data_dir()

    def set_timeout(self, timeout):
        self.TIMEOUT = timeout

    def setup_data_dir(self):
        self.test_data_dir = conf.testdatadir

        if not os.path.exists(self.test_data_dir):
            assert False, "Test data directory does not exist: %s" % self.test_data_dir

    def run(self, args='', timeout=None):
        timeout = timeout or self.TIMEOUT
        #command = self.command + ' --yabi-debug ' + args
        command = self.command + ' ' + args
        starttime = time.time()
        if DEBUG:
            print command
        cmd = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = None
        while status==None:
            status = cmd.poll()
            time.sleep(1.0)

            if time.time()-starttime > timeout:
                raise YabiTimeoutException()

        return Result(status, cmd.stdout.read(), cmd.stderr.read(), runner=self)

    def login(self, username=conf.yabiusername, password=conf.yabipassword):
        result = self.run('login %s %s' % (username, password))
        return 'Login unsuccessful' not in result.stderr

    def logout(self):
        result = self.run('logout')

    def purge(self):
        result = self.run('purge')

def shell_command(command):
    print command
    cmd = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    status = cmd.wait()
    out = cmd.stdout.read()
    err = cmd.stdout.read()
    if status != 0 or err:
        print 'Command was: ' + command
        print 'STATUS was: %d' % status
        print 'STDOUT was: \n' + out
        print 'STDERR was: \n' + err
        raise StandardError('shell_command failed (%s)'%command)

class YabiTestCase(unittest.TestCase):
    TIMEOUT = conf.timeout

    runner = Yabi

    @property
    def classname(self):
        return self.__module__ + '.' + self.__class__.__name__

    def setUp(self):
        shell_command('cd .. && ./yabictl.sh stop')
        shell_command('cd .. && ./yabictl.sh clean')
        shell_command(conf.dbrebuild)
        shell_command('cd .. && ./yabictl.sh start')
        self.yabi = self.runner()
        self.yabi.set_timeout(self.TIMEOUT)
        self.yabi.login()

    def tearDown(self):
        self.yabi.logout()
        self.yabi.purge()
        shell_command('cd .. && ./yabictl.sh stop')
        shell_command('cd .. && ./yabictl.sh clean')

class FileUtils(object):
    def setUp(self):
        self.tempfiles = []

    def tearDown(self):
        for f in self.tempfiles:
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.unlink(f)

    def create_tempfile(self, size = 1024, parentdir = conf.tmpdir):
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

    def delete_on_exit(self, filename):
        self.tempfiles.append(filename)

    def run_cksum_locally(self, filename):
        import subprocess
        cmd = subprocess.Popen('cksum %s' % filename, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        status = cmd.wait()
        assert status == 0, 'ERROR: ' + cmd.stderr.read()
        output = cmd.stdout.read()
        our_line = filter(lambda l: filename in l, output.split("\n"))[0]
        expected_cksum, expected_size, rest = our_line.split()
        return expected_cksum, expected_size
