from fabric.api import env, local
from ccgfab.base import *
import os

env.username = os.environ["USER"]
env.app_root = '/usr/local/python/ccgapps/'
env.app_name = 'yabibe'
env.app_install_names = ['yabibe'] # use app_name or list of names for each install
env.vc = 'svn'
env.git_trunk_url = ""
env.svn_trunk_url = "svn+ssh://store.localdomain/store/techsvn/ccg/yabi/yabi-be-twisted/trunk/"
env.svn_tags_url = "svn+ssh://store.localdomain/store/techsvn/ccg/yabi/yabi-be-twisted/tags/"

env.writeable_dirs.extend([]) # add directories you wish to have created and made writeable
env.content_excludes.extend([]) # add quoted patterns here for extra rsync excludes
env.content_includes.extend([]) # add quoted patterns here for extra rsync includes

env.celeryd_options = " -l debug"

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

def backend():
    """
    run the twisted backend on the terminal without forking
    """
    print local("/usr/local/stackless/bin/twistd -noy server.py", capture=False)

def start():
    """
    start the twistd server as a daemon
    """
    print local("./init_scripts/centos/yabibe start")

def stop():
    """
    stop the twistd server
    """
    print local("./init_scripts/centos/yabibe stop")

def restart():
    """
    restart the twistd server
    """
    print local("./init_scripts/centos/yabibe restart")
