### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
from fabric.api import env, local
from ccgfab.base import *

import os

env.username = os.environ["USER"]
env.app_root = '/usr/local/python/ccgapps/'
env.app_name = 'yabiadmin'
env.app_install_names = ['yabiadmin'] # use app_name or list of names for each install
env.vc = 'svn'
env.git_trunk_url = ""
env.svn_trunk_url = "svn+ssh://store.localdomain/store/techsvn/ccg/yabi/yabiadmin/trunk/"
env.svn_tags_url = "svn+ssh://store.localdomain/store/techsvn/ccg/yabi/yabiadmin/tags/"

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

    def getEggCacheDir(self):
        return os.path.join(self.getProjectDir(), 'scratch', 'egg-cache')

    def getCeleryEggCacheDir(self):
        return os.path.join(self.getProjectDir(), 'scratch', 'egg-cache-celery')



localPaths = LocalPaths()


def deploy():
    """
    Make a user deployment
    """
    _ccg_deploy_user()
    _munge_settings()

def snapshot():
    """
    Make a snapshot deployment
    """
    _ccg_deploy_snapshot()
    localPaths.target="snapshot"
    _munge_settings(debug_logging='logging.WARNING', sentry=True) #pass string for warning, not actual logging.WARNING

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
    _django_env()
    os.environ["PYTHON_EGG_CACHE"] = localPaths.getCeleryEggCacheDir()    
    print local(localPaths.getVirtualPython() + " " + localPaths.getCeleryd() + env.celeryd_options, capture=False)

def _django_env():
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=localPaths.getProjectDir()
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=localPaths.getProjectDir()
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + localPaths.getProjectDir() + ":" + localPaths.getParentDir()
    os.environ["PROJECT_DIRECTORY"] = localPaths.getProjectDir()

def manage_release(*args):
    from ccgfab.vc.svn import ccg_checkout_tag, ccg_checkout_trunk
    release = ccg_checkout_tag()
    localPaths.target = release
    _django_env()

    print local(localPaths.getVirtualPython() + " " + localPaths.getProjectDir() + "/manage.py " + " ".join(args), capture=False)

    
        
