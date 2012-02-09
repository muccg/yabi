from fabric.api import local, lcd, run, prefix

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
STACKLESS_PYTHON = '/usr/local/bin/spython'

def admin_bootstrap():
    with lcd(ADMIN['dir']):
        local("sh ../../bootstrap.sh -r quickstart.txt")

def admin_initdb():
    _virtualenv(ADMIN, 'fab initdb')

def admin_runserver():
    _virtualenv(ADMIN, "fab runserver")

def admin_killserver():
    _virtualenv(ADMIN, "fab killserver")

def admin_quickstart():
    admin_bootstrap()
    admin_initdb()
    admin_runserver()


def fe_bootstrap():
    with lcd(FE['dir']):
        local("sh ../../bootstrap.sh -r quickstart.txt")

def fe_initdb():
    _virtualenv(FE, 'fab initdb')

def fe_runserver():
    _virtualenv(FE, "fab runserver")

def fe_killserver():
    _virtualenv(FE, "fab killserver")

def fe_quickstart():
    fe_bootstrap()
    fe_initdb()
    fe_runserver()


def be_bootstrap():
    with lcd(BE['dir']):
        local("sh ../../bootstrap.sh -p %s -r requirements.txt" % STACKLESS_PYTHON)

def be_createdirs():
    _virtualenv(BE, "fab createdirs")

def be_runserver():
    _virtualenv(BE, "fab backend")

def be_quickstart():
    be_bootstrap()
    be_createdirs()
    be_runserver()

def _virtualenv(project, command):
    with lcd(project['dir']):
        local(". %s/bin/activate && %s" % (project['virtenvdir'], command))
   
