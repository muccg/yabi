from fabric.api import env, local, lcd
from ccgfab.base import *

import os

env.username = os.environ["USER"]
env.app_root = '/usr/local/python/ccgapps/'
env.app_name = 'yabiadmin'
env.repo_path = 'yabiadmin'
env.app_install_names = ['yabiadmin'] # use app_name or list of names for each install
env.vc = 'mercurial'

env.writeable_dirs.extend([]) # add directories you wish to have created and made writeable
env.content_excludes.extend([]) # add quoted patterns here for extra rsync excludes
env.content_includes.extend([]) # add quoted patterns here for extra rsync includes
env.auto_confirm_purge = False #controls whether the confirmation prompt for purge is used

env.celeryd_options = "--config=settings -l debug -E -B"
env.ccg_pip_options = "--download-cache=/tmp --use-mirrors --no-index --mirrors=http://c.pypi.python.org/ --mirrors=http://d.pypi.python.org/ --mirrors=http://e.pypi.python.org/"

env.gunicorn_listening_on = "127.0.0.1:8000"
env.gunicorn_workers = 5
env.gunicorn_worker_timeout = 300


# Used by config related tasks
CONFS_DIR = 'appsettings_dir'
CONF_LN_NAME = 'appsettings'
TEST_CONF_LN_NAME = os.path.join(CONFS_DIR, 'testdb')

class LocalPaths():

    target = env.username

    def getSettings(self):
        return os.path.join(env.app_root, env.app_install_names[0], self.target, env.app_name, "settings.py")

    def getProjectDir(self):
        return os.path.join(env.app_root, env.app_install_names[0], self.target, env.app_name)

    def getParentDir(self):
        return os.path.join(env.app_root, env.app_install_names[0], self.target)

    def getCeleryd(self):
        return os.path.join(self.getProjectDir(), 'virtualpython/bin/celeryd')

    def getVirtualPython(self):
        return os.path.join(self.getProjectDir(), 'virtualpython/bin/python')

    def getEggCacheDir(self):
        return os.path.join(self.getProjectDir(), 'scratch', 'egg-cache')

    def getCeleryEggCacheDir(self):
        return os.path.join(self.getProjectDir(), 'scratch', 'egg-cache-celery')

localPaths = LocalPaths()


def deploy(auto_confirm_purge = False, migration = True):
    """
    Make a user deployment
    """
    env.auto_confirm_purge = auto_confirm_purge
    _ccg_deploy_user(migration)

def snapshot(auto_confirm_purge=False):
    """
    Make a snapshot deployment
    """
    env.auto_confirm_purge=auto_confirm_purge
    _ccg_deploy_snapshot()
    localPaths.target="snapshot"

def release(*args, **kwargs):
    """
    Make a release deployment
    """
    migration = kwargs.get("migration", True)
    requirements = kwargs.get("requirements", "requirements.txt")
    tag = kwargs.get("tag", None)
    env.ccg_requirements = requirements
    env.auto_confirm=False
    _ccg_deploy_release(tag=tag,migration=migration)

def testrelease(*args, **kwargs):
    """
    Make a release deployment using the dev settings file
    """
    migration = kwargs.get("migration", True)
    env.auto_confirm=False
    if len(args):
        _ccg_deploy_release(devrelease=True, tag=args[0], migration=migration)
    else:
        _ccg_deploy_release(devrelease=True, migration=migration)

def purge(auto_confirm_purge=False):
    """
    Remove the user deployment
    """
    env.auto_confirm_purge = auto_confirm_purge
    _ccg_purge_user()

def purge_snapshot(auto_confirm_purge = False):
    """
    Remove the snapshot deployment
    """
    env.auto_confirm_purge = auto_confirm_purge
    _ccg_purge_snapshot()

def celeryd():
    """
    Foreground celeryd using your deployment of admin
    """
    _celeryd()

def celeryd_quickstart(bg=False):
    """
    Foreground celeryd using your deployment of admin
    """
    _celeryd_quickstart(bg)


def snapshot_celeryd():
    """
    Foreground celeryd using snapshot deployment of admin
    """
    localPaths.target = "snapshot"
    _celeryd()

def initdb():
    """
    Creates the DB schema and runs the DB migrations
    To be used on initial project setup only
    """
    local("python manage.py syncdb --noinput")
    migrate()

def dropdb():
    """
    Drops the DB used by the application
    """
    _local_env()
    local("python db_utils.py dropdb")

def createdb():
    """
    Creates the DB used by the application
    """
    _local_env()
    local("python db_utils.py createdb")

def recreatedb():
    """
    Recreates (dropdb then createdb) the DB used by the application
    """
    _local_env()
    local("python db_utils.py recreatedb")

def migrate():
    """
    Runs the DB migrations
    """
    local("python manage.py migrate")


def runserver(bg=False):
    """
    Runs the gunicorn server for local development
    """
    cmd = "gunicorn_django -w %s -b %s -t %s" % (env.gunicorn_workers, env.gunicorn_listening_on, env.gunicorn_worker_timeout)
    if bg:
        cmd += " >yabiadmin.log 2>&1 &"
    os.environ["PROJECT_DIRECTORY"] = "." 
    local(cmd, capture=False)


def killserver():
    """
    Kills the gunicorn server for local development
    """
    def anyfn(fn, iterable):
        for e in iterable:
            if fn(e): return True
        return False
    import psutil
    gunicorn_pss = [p for p in psutil.process_iter() if p.name == 'gunicorn_django']
    our_gunicorn_pss = [p for p in gunicorn_pss if anyfn(lambda arg: env.gunicorn_listening_on in arg, p.cmdline)]
    counter = 0
    for ps in our_gunicorn_pss:
        if psutil.pid_exists(ps.pid):
            counter += 1
            ps.terminate()
    print "%i processes terminated" % counter

def killcelery():
    """
    Kills the celery server for local development
    """
    def anyfn(fn, iterable):
        for e in iterable:
            if fn(e): return True
        return False
    import psutil
    celeryd_pss = [p for p in psutil.process_iter() if p.name == 'python' and anyfn(lambda arg: 'celery.bin.celeryd' in arg, p.cmdline)]
    counter = 0
    for ps in celeryd_pss:
        if psutil.pid_exists(ps.pid):
            counter += 1
            ps.terminate()
    print "%i processes terminated" % counter


def syncdb():
    """
    syncdb using your deployment of yabi admin
    """
    manage("syncdb")

def runserver_plus(*args):
    manage("runserver_plus",*args)

def manage(*args):
    _django_env()
    print local(localPaths.getVirtualPython() + " " + localPaths.getProjectDir() + "/manage.py " + " ".join(args), capture=False)

def list_configs():
    '''display the available configurations'''

    configs = sorted(filter(lambda i: os.path.isdir(os.path.join(CONFS_DIR, i)), os.listdir(CONFS_DIR)))
    if not configs:
        print "No configurations are available"
        return

    print "Available configurations:"
    for c in configs:
        config = c
        if os.path.exists(CONF_LN_NAME) and os.path.samefile(CONF_LN_NAME, os.path.join(CONFS_DIR, c)):
            config = config + " (ACTIVE)"
        print '\t' + config

def active_config():
    '''display the currently active configuration'''

    config = "No config activated"
    if os.path.islink(CONF_LN_NAME) and os.path.samefile(os.path.dirname(os.readlink(CONF_LN_NAME)), CONFS_DIR):
        config = os.path.basename(os.readlink(CONF_LN_NAME))

    print '\t' + config

def activate_config(config_dir):
    '''activate the passed in configuration'''

    full_dir = os.path.join(CONFS_DIR, config_dir)
    if not (os.path.exists(full_dir)):
        print "Invalid config (for a list of available configs use fab list_configs)"
        return
    if os.path.exists(CONF_LN_NAME) and not os.path.islink(CONF_LN_NAME):
        raise StandardError("Can't create symlink %s, because %s already exists" % (CONF_LN_NAME, CONF_LN_NAME))
    if os.path.islink(CONF_LN_NAME):
        os.unlink(CONF_LN_NAME)
    local("ln -s %s %s" % (full_dir, CONF_LN_NAME))

def deactivate_config():
    '''deactivate the current configuration'''

    if os.path.islink(CONF_LN_NAME):
        os.unlink(CONF_LN_NAME)

def _get_selected_test_config():
    config = None
    if os.path.islink(TEST_CONF_LN_NAME):
        target = os.readlink(TEST_CONF_LN_NAME)
        if target.endswith('/'): target = target[:-1]
        config = os.path.basename(target)
    return config

def assert_test_config_is_selected():
    '''fails if the test configuration isn't set'''
    config = _get_selected_test_config()
    if config is None:
        print '\n\tNo configuration is selected for running tests. Please use select_test_config to select one.\n'
        raise Exception('No configuration is selected for running tests. Please use select_test_config to select one.')


def selected_test_config():
    '''displays the configuration used for running tests'''

    config = _get_selected_test_config()
    if config is None:
        config = "No test config activated"
    print '\t' + config
 
def select_test_config(config_dir):
    '''selects the passed in configuration to be used for running tests'''

    if config_dir == os.path.basename(TEST_CONF_LN_NAME):
        print "You can't set %s to point to itself!" % os.path.basename(TEST_CONF_LN_NAME)
        return

    full_dir = os.path.join(CONFS_DIR, config_dir)
    if not (os.path.exists(full_dir)):
        print "Invalid config (for a list of available configs use fab list_configs)"
        raise StandardError("Invalid config (for a list of available configs use fab list_configs)")
    if os.path.exists(TEST_CONF_LN_NAME) and not os.path.islink(TEST_CONF_LN_NAME):
        raise StandardError("Can't create symlink %s, because %s already exists" % (TEST_CONF_LN_NAME, TEST_CONF_LN_NAME))
    if os.path.islink(TEST_CONF_LN_NAME):
        os.unlink(TEST_CONF_LN_NAME)
    with lcd(CONFS_DIR):
        local("ln -s %s %s" % (config_dir, os.path.basename(TEST_CONF_LN_NAME)))


def tests():
    '''runs all the tests in the Yabiadmin project'''

    _local_env()
    local("nosetests -v")

def require(requirements_file):
    '''pip installs the requirements specified in the passed in file'''
    local("pip install -r %s" % requirements_file)

def _celeryd():
    _django_env()
    print local("python -m celery.bin.celeryd " + env.celeryd_options, capture=False)

def _celeryd_quickstart(bg=False):
    _celery_env()
    cmd = "python -m celery.bin.celeryd " + env.celeryd_options
    if bg:
        cmd += " >celery.log 2>&1 &"
    print local(cmd, capture=False)

def _django_env():
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=localPaths.getProjectDir()
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=localPaths.getProjectDir()
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + localPaths.getProjectDir() + ":" + localPaths.getParentDir()
    os.environ["PROJECT_DIRECTORY"] = localPaths.getProjectDir()

def _local_env():
    os.environ["DJANGO_SETTINGS_MODULE"]="settings" 
    os.environ["DJANGO_PROJECT_DIR"]="." 
    os.environ["PROJECT_DIRECTORY"] = "." 
    os.environ["PYTHONPATH"] = ".:.."

def _celery_env(): 
    _local_env()
    os.environ["CELERY_LOADER"]="django" 
    os.environ["CELERY_CHDIR"]="." 
