from fabric.api import env, local
from ccgfab.base import *
import os

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

# /usr/local/python26/ccgapps/yabiadmin/ahunter/yabiadmin/virtualpython/bin/celeryd
env.celeryd = env.app_root + 'yabiadmin/ahunter/yabiadmin/virtualpython/bin/celeryd'
env.celeryd_options = " -l debug"
#env.celeryd_options = " -h"
env.django_project_dir = env.app_root + 'yabiadmin/ahunter/yabiadmin/'
env.django_parent_dir = env.app_root + 'yabiadmin/ahunter/'
env.virtual_python="/usr/local/python26/ccgapps/yabiadmin/ahunter/yabiadmin/virtualpython/bin/python"

def deploy():
    """
    Make a user deployment
    """
    _ccg_deploy_user()

    print "**********************************************************"
    print "* Dont forget your celeryd!"
    print "* Usage: ./init_scripts/centos/celeryd {start|stop|restart|}"
    print "**********************************************************"

def snapshot():
    """
    Make a snapshot deployment
    """
    _ccg_deploy_snapshot()

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
    #os.environ["DJANGO_SETTINGS_MODULE"]="yabiadmin.settings"
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=env.django_project_dir
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=env.django_project_dir
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + env.django_project_dir + ":" + env.django_parent_dir
    os.environ["PROJECT_DIRECTORY"] = "/usr/local/python/ccgapps/yabiadmin/ahunter/yabiadmin/"

    print local(env.virtual_python + " " + env.celeryd + env.celeryd_options, capture=False)

def syncdb():
    _manage("syncdb")

def _manage(opt=help):
    #os.environ["DJANGO_SETTINGS_MODULE"]="yabiadmin.settings"
    os.environ["DJANGO_SETTINGS_MODULE"]="settings"
    os.environ["DJANGO_PROJECT_DIR"]=env.django_project_dir
    os.environ["CELERY_LOADER"]="django"
    os.environ["CELERY_CHDIR"]=env.django_project_dir
    os.environ["PYTHONPATH"] = "/usr/local/etc/ccgapps/:" + env.django_project_dir + ":" + env.django_parent_dir
    os.environ["PROJECT_DIRECTORY"] = "/usr/local/python/ccgapps/yabiadmin/ahunter/yabiadmin/"

    print local(env.virtual_python + " " + env.django_project_dir + "/manage.py " + opt, capture=False)



"""
export DJANGODEV=1
export DJANGO_SETTINGS_MODULE="yabiadmin.settings"
export DJANGO_PROJECT_DIR="/usr/local/python/ccgapps/yabiadmin/ahunter/"
export PROJECT_DIRECTORY="/usr/local/python/ccgapps/yabiadmin/ahunter/"
export CELERYD_CHDIR="/usr/local/python/ccgapps/yabiadmin/ahunter/"
export PYTHONPATH="/usr/local/python/ccgapps/yabiadmin/ahunter/"
export PYTHONPATH=$PYTHONPATH:/usr/local/etc/ccgapps/
export CELERY_LOADER="django"

"""

