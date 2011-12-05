from fabric.api import env, local
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
    env.auto_confirm=False
    if len(args):
        _ccg_deploy_release(tag=args[0],migration=migration)
    else:
        _ccg_deploy_release(migration=migration)

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

def celeryd_quickstart():
    """
    Foreground celeryd using your deployment of admin
    """
    _celeryd_quickstart()


def snapshot_celeryd():
    """
    Foreground celeryd using snapshot deployment of admin
    """
    localPaths.target = "snapshot"
    _celeryd()

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

def _celeryd():
    _django_env()
    print local("python -m celery.bin.celeryd " + env.celeryd_options, capture=False)

def _celeryd_quickstart():
    _celery_env()
    print local("python -m celery.bin.celeryd " + env.celeryd_options, capture=False)

def _django_env():
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=localPaths.getProjectDir()
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=localPaths.getProjectDir()
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + localPaths.getProjectDir() + ":" + localPaths.getParentDir()
    os.environ["PROJECT_DIRECTORY"] = localPaths.getProjectDir()

def _celery_env(): 
    os.environ["DJANGO_SETTINGS_MODULE"]="settings" 
    os.environ["DJANGO_PROJECT_DIR"]="." 
    os.environ["CELERY_LOADER"]="django" 
    os.environ["CELERY_CHDIR"]="." 
    os.environ["PROJECT_DIRECTORY"] = "." 
    os.environ["PYTHONPATH"] = ".:.."
