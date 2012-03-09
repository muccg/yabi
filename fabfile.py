from fabric.api import local, lcd, run, prefix
import os

ADMIN = {
    "dir": "yabiadmin/yabiadmin",
    "virtenvdir": "virt_yabiadmin"
}
FE = {
    "dir": "yabife/yabife",
    "virtenvdir": "virt_yabife"
}
BE = {
    "dir": "yabibe/yabibe",
    "virtenvdir": "virt_yabibe"
}
YABISH = {
    "dir": "yabish",
    "virtenvdir": "virt_yabish"
}
TESTS = {
    "dir": "yabitests",
    "virtenvdir": "virt_yabitests"
}

STACKLESS_PYTHON = '/usr/local/bin/spython'

def clean():
    '''Clean all virtual environment directories'''
    for proj in(FE, ADMIN, BE, YABISH, TESTS):
        virtenvdir = os.path.join(proj['dir'], proj['virtenvdir'])
        local("rm -rf %s" % virtenvdir)

def admin_bootstrap():
    '''Bootstrap the yabiadmin project'''
    with lcd(ADMIN['dir']):
        local("sh ../../bootstrap.sh -r quickstart.txt")

def admin_initdb():
    '''Initialise the DB of Yabiadmin'''
    _virtualenv(ADMIN, 'fab initdb')

def admin_runserver(bg=False):
    '''Run the yabiadmin server for local dev (:bg for background)'''
    cmd = "fab runserver"
    if bg:
        cmd += ":bg"
    _virtualenv(ADMIN, cmd)

def admin_runcelery(bg=False):
    '''Run the yabiadmin celery server for local dev (:bg for background)'''
    cmd = "fab celeryd_quickstart"
    if bg:
        cmd += ":bg"
    _virtualenv(ADMIN, cmd)

def admin_killserver():
    '''Kill the yabiadmin local server'''
    _virtualenv(ADMIN, "fab killserver")

def admin_killcelery():
    '''Kill the yabiadmin celery server'''
    _virtualenv(ADMIN, "fab killcelery")

def admin_quickstart(bg=False):
    '''Quickstart the yabiadmin project (bootstrap, initdb, runserver)'''
    admin_bootstrap()
    admin_initdb()
    admin_runserver(bg)

def fe_bootstrap():
    '''Bootstrap the yabife project'''
    with lcd(FE['dir']):
        local("sh ../../bootstrap.sh -r quickstart.txt")

def fe_initdb():
    '''Initialise the DB of Yabife'''
    _virtualenv(FE, 'fab initdb')

def fe_runserver(bg=False):
    '''Run the yabife server for local dev (:bg for background)'''
    cmd = "fab runserver"
    if bg:
        cmd += ":bg"
    _virtualenv(FE, cmd)

def fe_killserver():
    '''Kill the yabife local server'''
    _virtualenv(FE, "fab killserver")

def fe_quickstart(bg=False):
    '''Quickstart the yabife project (bootstrap, initdb, runserver)'''
    fe_bootstrap()
    fe_initdb()
    fe_runserver(bg)


def be_bootstrap():
    '''Bootstrap the yabibe project'''
    with lcd(BE['dir']):
        local("sh ../../bootstrap.sh -p %s -r requirements.txt" % STACKLESS_PYTHON)

def be_createdirs():
    '''Creates necessary directories for the yabibe project'''
    _virtualenv(BE, "fab createdirs")

def be_runserver(bg=False):
    '''Run the yabibe server for local dev (:bg for background)'''
    cmd = "fab backend"
    if bg:
        cmd += ":bg"
    _virtualenv(BE, cmd)

def be_killserver():
    '''Kill the yabibe local server'''
    _virtualenv(BE, "fab killbackend")

def be_quickstart(bg=False):
    '''Quickstart the yabibe project (bootstrap, createdirs, runserver)'''
    be_bootstrap()
    be_createdirs()
    be_runserver(bg)

def yabish_bootstrap():
    '''Bootstrap the yabish project'''
    with lcd(YABISH['dir']):
        local("sh ../bootstrap.sh")

def tests_bootstrap():
    '''Bootstrap the yabi tests project'''
    with lcd(TESTS['dir']):
        local("sh ../bootstrap.sh")

def quickstart():
    '''Quickstart the whole YABI stack (fe, admin, be, yabish, tests)'''
    fe_quickstart(bg=True)
    admin_quickstart(bg=True)
    admin_runcelery(bg=True)
    be_quickstart(bg=True)
    yabish_bootstrap()
    tests_bootstrap()

def runservers():
    '''Run all servers in the YABI stack for local dev in the background (fe, admin, be)'''
    fe_runserver(bg=True)
    admin_runserver(bg=True)
    admin_runcelery(bg=True)
    be_runserver(bg=True)

def killservers():
    '''Kills all the local development servers in the YABI stack (fe, admin, be)'''
    fe_killserver()
    admin_killserver()
    admin_killcelery()
    be_killserver()

def admin_list_configs():
    '''Displays available configs for Yabi Admin'''

    _virtualenv(ADMIN, "fab list_configs")

def admin_active_config():
    '''Displays the active Yabi Admin config'''

    _virtualenv(ADMIN, "fab active_config")

def admin_activate_config(config):
    '''Activate the passed in Yabi admin config'''

    _virtualenv(ADMIN, "fab activate_config:%s" % config)

def admin_deactivate_config():
    '''Deactivates the active Yabi Admin config'''

    _virtualenv(ADMIN, "fab deactivate_config")

def admin_selected_test_config():
    '''Displays the configuration used for running tests'''

    _virtualenv(ADMIN, "fab selected_test_config")

def admin_select_test_config(config):
    '''Select the passed in config to be used when running tests'''

    _virtualenv(ADMIN, "fab select_test_config:%s" % config)

def _assert_test_config_is_selected():
    # unfortunately the errors displayed by a nested fab aren't displayed
    print _virtualenv(ADMIN, "fab assert_test_config_is_selected")

def runtests():
    '''Run end to end YABI tests in the yabitests project'''
    _assert_test_config_is_selected() 
    killservers()
    admin_activate_config('testdb')
    runservers()
    tests()
    killservers()
    admin_deactivate_config()

def tests(dryrun=False):
    '''Run end to end YABI tests in the yabitests project'''
    cmd = "nosetests -v"
    if dryrun:
        cmd += " --collect-only"
    _virtualenv(TESTS, cmd)

def _virtualenv(project, command):
    with lcd(project['dir']):
        local(". %s/bin/activate && %s" % (project['virtenvdir'], command))
   
