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


def deploy(auto_confirm_purge = False):
    """
    Make a user deployment
    """
    env.auto_confirm_purge = auto_confirm_purge
    _ccg_deploy_user()
    _munge_settings()

def snapshot(auto_confirm_purge=False):
    """
    Make a snapshot deployment
    """
    env.auto_confirm_purge=auto_confirm_purge
    _ccg_deploy_snapshot()
    localPaths.target="snapshot"
    _munge_settings(debug_logging='logging.WARNING', sentry=True) #pass string for warning, not actual logging.WARNING

def release(*args):
    """
    Make a release deployment
    """
    env.auto_confirm=False
    if len(args):
        _ccg_deploy_release(tag=args[0])
    else:
        _ccg_deploy_release()
        
def testrelease(*args):
    """
    Make a release deployment using the dev settings file
    """
    env.auto_confirm=False
    if len(args):
        _ccg_deploy_release(devrelease=True, tag=args[0])
    else:
        _ccg_deploy_release(devrelease=True)

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

def _munge_settings(**kwargs):
    print local("sed -i -r -e 's/<CCG_TARGET_NAME>/%s/g' %s"  % (localPaths.target, localPaths.getSettings()))
    if kwargs.get('sentry'):
        print local("sed -i -r -e 's/SENTRY_TESTING = False/SENTRY_TESTING = True/g' %s"  % (localPaths.getSettings()))
    if kwargs.get('debug_logging'):
        print local("sed -i -r -e 's/LOGGING_LEVEL = logging.DEBUG/LOGGING_LEVEL = %s/g' %s"  % (kwargs.get('debug_logging'),localPaths.getSettings()))

def _celeryd():
    #_django_env()
    #os.environ["PYTHON_EGG_CACHE"] = localPaths.getCeleryEggCacheDir()
    #print local(localPaths.getVirtualPython() + " " + localPaths.getCeleryd() + env.celeryd_options, capture=False)
    print local("python -m celery.bin.celery " + env.celeryd_options, capture=False)

def _django_env():
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=localPaths.getProjectDir()
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=localPaths.getProjectDir()
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + localPaths.getProjectDir() + ":" + localPaths.getParentDir()
    os.environ["PROJECT_DIRECTORY"] = localPaths.getProjectDir()
