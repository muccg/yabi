#!/bin/bash
#
# Quickstart script to setup yabi with a simple sqlite database
#

# break on error
set -e 

# additional URLs to search for eggs during install
EASY_INSTALL_INDEX="https://s3-ap-southeast-2.amazonaws.com/http-syd/python/centos/6/noarch/index.html"

# Eggs for this installation of quickstart
YABI_ADMIN_EGG="yabiadmin==0.2"
YABI_BE_EGG="yabibe==0.2"

# handle the stop instruction to tear down the quickstart environment
if [ "x$1" == "xstop" ]
then
    echo "Stopping quickstart servers"
    set +e
    killall gunicorn_django
    killall celeryd
    kill `cat yabibe-quickstart.pid` 

    # delay to allow file handles to free
    sleep 3

    exit 0
fi

# start backend, celery and frontend
if [ "x$1" == "xstart" ]
then

    echo "Launch yabiadmin (frontend) http://localhost:8000"
    virt_quickstart_yabiadmin/bin/gunicorn_django -b 0.0.0.0:8000 --log-file=yabiadmin-quickstart.log --daemon yabiadmin.quickstartsettings -t 300 -w 5

    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="quickstartsettings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="--logfile=celeryd-quickstart.log --pidfile=celeryd-quickstart.pid"
    CELERY_LOADER="django"
    PYTHONPATH=$CELERYD_CHDIR
    DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
    DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
    PROJECT_DIRECTORY="$CELERYD_CHDIR"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PYTHONPATH PROJECT_DIRECTORY CELERYD_CHDIR
    virt_quickstart_yabiadmin/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &

    echo "Launch yabibe (backend)"
    mkdir -p /tmp/run/backend/certificates
    mkdir -p /tmp/run/backend/fifos
    mkdir -p /tmp/run/backend/tasklets
    mkdir -p /tmp/run/backend/temp

    # TODO pull from egg
    unset YABICONF
    export QUICKSTART="1" 
    virt_quickstart_yabibe/bin/yabibe --pidfile=yabibe-quickstart.pid

    echo "To stop servers, run './quickstart.sh stop'"

    exit 0
fi

# install
if [ "x$1" == "xinstall" ]
then

    # check requirements
    which virtualenv >/dev/null

    export PYTHONPATH=`pwd`

    echo "Install yabiadmin ($YABI_ADMIN_EGG) from $EASY_INSTALL_INDEX"
    virtualenv virt_quickstart_yabiadmin
    virt_quickstart_yabiadmin/bin/easy_install -f $EASY_INSTALL_INDEX $YABI_ADMIN_EGG

    # use gunicorn to fire up yabiadmin
    virt_quickstart_yabiadmin/bin/pip install gunicorn

    # database migrations
    export DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
    virt_quickstart_yabiadmin/bin/django-admin.py syncdb --noinput
    virt_quickstart_yabiadmin/bin/django-admin.py migrate

    # collect static
    virt_quickstart_yabiadmin/bin/django-admin.py collectstatic --noinput 1> collectstatic.log

    echo "Install yabibe ($YABI_BE_EGG) from $EASY_INSTALL_INDEX"
    virtualenv virt_quickstart_yabibe
    virt_quickstart_yabibe/bin/easy_install -f $EASY_INSTALL_INDEX $YABI_BE_EGG

    echo "To run servers, type './quickstart.sh start'"

    exit 0
fi

# clean
if [ "x$1" == "xclean" ]
then
    echo "Removing YabiAdmin virtual python and SQLite database"
    rm -rf virt_quickstart_yabiadmin
    rm -f yabiadmin_quickstart.sqlite3

    echo "Removing YabiBe virtual python and /tmp/run"
    rm -rf virt_quickstart_yabibe
    rm -rf /tmp/run

    echo "Vitual python directories and SQLite database for quickstart removed."

    exit 0
fi


echo "Usage ./quickstart.sh (install|clean|start|stop)"
