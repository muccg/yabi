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

def admin_runserver(bg=False):
    cmd = "fab runserver"
    if bg:
        cmd += ":bg"
    _virtualenv(ADMIN, cmd)

def admin_killserver():
    _virtualenv(ADMIN, "fab killserver")

def admin_killcelery():
    _virtualenv(ADMIN, "fab killcelery")

def admin_runcelery(bg=False):
    cmd = "fab celeryd_quickstart"
    if bg:
        cmd += ":bg"
    _virtualenv(ADMIN, cmd)

def admin_quickstart(bg=False):
    admin_bootstrap()
    admin_initdb()
    admin_runserver(bg)


def fe_bootstrap():
    with lcd(FE['dir']):
        local("sh ../../bootstrap.sh -r quickstart.txt")

def fe_initdb():
    _virtualenv(FE, 'fab initdb')

def fe_runserver(bg=False):
    cmd = "fab runserver"
    if bg:
        cmd += ":bg"
    _virtualenv(FE, cmd)

def fe_killserver():
    _virtualenv(FE, "fab killserver")

def fe_quickstart(bg=False):
    fe_bootstrap()
    fe_initdb()
    fe_runserver(bg)


def be_bootstrap():
    with lcd(BE['dir']):
        local("sh ../../bootstrap.sh -p %s -r requirements.txt" % STACKLESS_PYTHON)

def be_createdirs():
    _virtualenv(BE, "fab createdirs")

def be_runserver(bg=False):
    cmd = "fab backend"
    if bg:
        cmd += ":bg"
    _virtualenv(BE, cmd)

def be_quickstart(bg=False):
    be_bootstrap()
    be_createdirs()
    be_runserver(bg)

def quickstart():
    fe_quickstart(bg=True)
    admin_quickstart(bg=True)
    admin_runcelery(bg=True)
    be_quickstart(bg=True)

def _virtualenv(project, command):
    with lcd(project['dir']):
        local(". %s/bin/activate && %s" % (project['virtenvdir'], command))
   
