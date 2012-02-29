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

env.gunicorn_listening_on = "127.0.0.1:8001"

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

def migrate():
    """
    Runs the DB migrations
    """
    local("python manage.py migrate")


def runserver(bg=False):
    """
    Runs the gunicorn server for local development
    """
    cmd = "gunicorn_django -b "+ env.gunicorn_listening_on
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

def _celery_env(): 
    os.environ["DJANGO_SETTINGS_MODULE"]="settings" 
    os.environ["DJANGO_PROJECT_DIR"]="." 
    os.environ["CELERY_LOADER"]="django" 
    os.environ["CELERY_CHDIR"]="." 
    os.environ["PROJECT_DIRECTORY"] = "." 
    os.environ["PYTHONPATH"] = ".:.."
