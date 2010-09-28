from fabric.api import env, local
from ccgfab.base import *
import os

env.username = os.environ["USER"]
env.app_root = '/usr/local/python/ccgapps/'
env.app_name = 'yabife'
env.app_install_names = ['yabife'] # use app_name or list of names for each install
env.vc = 'svn'
env.git_trunk_url = ""
env.svn_trunk_url = "svn+ssh://store.localdomain/store/techsvn/ccg/yabi/yabife/trunk"
env.svn_tags_url = "svn+ssh://store.localdomain/store/techsvn/ccg/yabi/yabife/tags"

env.writeable_dirs.extend([]) # add directories you wish to have created and made writeable
env.content_excludes.extend([]) # add quoted patterns here for extra rsync excludes
env.content_includes.extend([]) # add quoted patterns here for extra rsync includes

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


localPaths = LocalPaths()


def deploy():
    """
    Make a user deployment
    """
    _ccg_deploy_user()
    env.settings_file = env.app_root + env.app_name + "/" + os.environ["USER"] + "/" + env.app_name + "/settings.py"
    print local("sed -i.bak -r -e 's/<CCG_TARGET_NAME>/%s/g' %s"  % (os.environ["USER"], env.settings_file))

def snapshot():
    """
    Make a snapshot deployment
    """
    _ccg_deploy_snapshot()
    env.settings_file = env.app_root + env.app_name + "/snapshot/" + env.app_name + "/settings.py"
    print local("sed -i.bak -r -e 's/<CCG_TARGET_NAME>/%s/g' %s"  % ("snapshot", env.settings_file))

def release():
    """
    Make a release deployment
    """
    _ccg_deploy_release()

def testrelease():
    """
    Make a release deployment using the dev settings file
    """
    _ccg_deploy_release(devrelease=True)

def purge():
    """
    Remove the user deployment
    """
    _ccg_purge_user()

def purge_snapshot():
    """
    Remove the snapshot deployment
    """
    _ccg_purge_snapshot()

def syncdb():
    """
    syncdb using your deployment of yabi admin
    """
    manage("syncdb")

def manage(opt="help"):
    _django_env()
    print local(localPaths.getVirtualPython() + " " + localPaths.getProjectDir() + "/manage.py " + opt, capture=False)


def _django_env():
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=localPaths.getProjectDir()
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=localPaths.getProjectDir()
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + localPaths.getProjectDir() + ":" + localPaths.getParentDir()
    os.environ["PROJECT_DIRECTORY"] = localPaths.getProjectDir()

