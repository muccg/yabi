import os, subprocess

ADMIN = {
    "dir": "yabiadmin/yabiadmin",
    "virtenvdir": "virt_yabiadmin"
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


def clean():
    '''Clean all virtual environment directories'''
    for proj in(ADMIN, BE, YABISH, TESTS):
        virtenvdir = os.path.join(proj['dir'], proj['virtenvdir'])
        local("rm -rf %s" % virtenvdir)

def admin_bootstrap():
    '''Bootstrap the yabiadmin project'''
    with lcd(ADMIN['dir']):
        local("sh ../../bootstrap.sh -r quickstart.txt")

def admin_require(requirements_file):
    '''Install additional requirements into the yabiadmin project'''
    _virtualenv(ADMIN, 'fab require:%s' % requirements_file)

def admin_initdb():
    '''Initialise the DB of Yabiadmin'''
    _virtualenv(ADMIN, 'fab initdb')

def admin_createdb():
    '''Create the DB of Yabiadmin'''
    _virtualenv(ADMIN, 'fab createdb')

def admin_dropdb():
    '''Drop the DB of Yabiadmin'''
    _virtualenv(ADMIN, 'fab dropdb')

def admin_recreatedb():
    '''Recreate (drop then create) the DB of Yabiadmin'''
    _virtualenv(ADMIN, 'fab recreatedb')

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

def admin_tests():
    '''Runs all the tests in the Yabiadmin project'''

    _virtualenv(ADMIN, "fab tests")

def admin_jslint():
    '''Runs Google Closure Linter on JavaScript in Yabiadmin project'''

    _virtualenv(ADMIN, "fab jslint")

def be_bootstrap():
    '''Bootstrap the yabibe project'''
    with lcd(BE['dir']):
        local("sh ../../bootstrap.sh -r requirements.txt")

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
    '''Quickstart the whole YABI stack (admin, be, yabish, tests)'''
    admin_quickstart(bg=True)
    admin_runcelery(bg=True)
    be_quickstart(bg=True)
    yabish_bootstrap()
    tests_bootstrap()

def runservers():
    '''Run all servers in the YABI stack for local dev in the background (admin, be)'''
    admin_runserver(bg=True)
    admin_runcelery(bg=True)
    be_runserver(bg=True)

def killservers():
    '''Kills all the local development servers in the YABI stack (admin, be)'''
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

def admin_select_test_config(config=None):
    '''Select the passed in config to be used when running tests'''

    cmd = "fab select_test_config"
    if config is not None:
        cmd += ":" + config
    _virtualenv(ADMIN, cmd)

def _no_test_config_selected():
    # unfortunately the errors displayed by a nested fab aren't displayed
    try:
       _virtualenv(ADMIN, "fab assert_test_config_is_selected")
    except:
        return False
    return True

def runtests(config=None):
    '''Run all the YABI tests'''
    admin_jslint()
    if config is None and not _no_test_config_selected():
        config = "sqlite_test"
    if config is not None:
        admin_select_test_config(config)
    killservers()
    admin_activate_config('testdb')
    admin_recreatedb()
    admin_initdb()
    runservers()
    admin_tests()
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
        print command
        local("source ../%s/bin/activate && %s" % (project['virtenvdir'], command))


# Run a command emulating fabric's local()
def local(command):
    subprocess.call(command, stderr=subprocess.STDOUT, shell=True)

# Context manager to switch to a directory like fab's lcd()
class lcd():
    def __init__(self, local_directory):
        self.local_directory = local_directory
    def __enter__(self):
        self.return_directory = os.getcwd()
        os.chdir(self.local_directory)
    def __exit__(self, type, value, traceback):
        os.chdir(self.return_directory)  

# Make this module runnable and behave as if it was run via fabric
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2: sys.exit(1)
    operation = sys.argv[1]
    kwargs = {}
    if ':' in sys.argv[1]:
        (operation, args) = operation.split(':')
        kwargs = dict(item.split("=") if '=' in item else (item,True) for item in args.split(","))
        print "Running:", operation, kwargs
        locals()[operation](kwargs)
    else:
        print "Running:", operation
        locals()[operation]()
    
    