import subprocess, os, shutil, glob, time
import config
import unittest

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
        self._workflow_status = None

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

    @property
    def workflow_status(self):
        if not self._workflow_status:
            result = self.yabi.run('status %s' % self.id)
            self._workflow_status = result.stdout
        return self._workflow_status

    @property
    def stageout_dir(self):
        for line in self.workflow_status.split('\n'):
            if 'stageout' in line:
                key, value = line.split(':', 1)
                return "%s/" % value.rsplit('/', 2)[0] # the stageout is for a job, get dir above that
        raise ValueError('No stageout directory found in workflow status\n%s' % self.workflow_status)

    def cleanup(self):
        result = self.yabi.run('rm "%s"' % self.stageout_dir)
        if result.status != 0:
            print result.status
            print result.stdout
            print result.stderr


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

