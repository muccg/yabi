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

env.app_root = '/usr/local/python/ccgapps/'
env.app_name = 'yabife'
env.repo_path = 'yabife'
env.app_install_names = ['yabife'] # use app_name or list of names for each install
env.vc = 'mercurial'

env.writeable_dirs.extend([]) # add directories you wish to have created and made writeable
env.content_excludes.extend([]) # add quoted patterns here for extra rsync excludes
env.content_includes.extend([]) # add quoted patterns here for extra rsync includes
env.auto_confirm_purge = False #controls whether the confirmation prompt for purge is used

env.ccg_pip_options = "--download-cache=/tmp --use-mirrors --no-index --mirrors=http://c.pypi.python.org/ --mirrors=http://d.pypi.python.org/ --mirrors=http://e.pypi.python.org/"

env.gunicorn_listening_on = "127.0.0.1:8000"

def deploy(auto_confirm_purge=False, migration=True):
    """
    Make a user deployment
    """
    env.auto_confirm_purge = auto_confirm_purge
    _ccg_deploy_user(migration=migration)

def snapshot(auto_confirm_purge=False, migration=True):
    """
    Make a snapshot deployment
    """
    env.auto_confirm_purge=auto_confirm_purge
    _ccg_deploy_snapshot(migration=migration)

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
    cmd = "gunicorn_django -w 5 -b "+ env.gunicorn_listening_on
    if bg:
        cmd += " -D"
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

