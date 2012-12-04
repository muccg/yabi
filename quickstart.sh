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
    kill `cat yabibe/yabibe-quickstart.pid` && rm yabibe/yabibe-quickstart.pid

    # delay to allow file handles to free
    sleep 3

    exit 0
fi

# start backend, celery and frontend
if [ "x$1" == "xstart" ]
then

    echo "Launch yabiadmin (frontend) http://localhost:8000"
    pushd yabiadmin
    vp/bin/gunicorn_django -b 0.0.0.0:8000 --log-file=gunicorn.log --daemon yabiadmin.quickstartsettings -t 300 -w 5

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
    vp/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &
    popd

    echo "Launch yabibe (backend)"
    pushd yabibe
    vp/bin/yabibe -l yabibe-quickstart.log --pidfile=yabibe-quickstart.pid
    popd

    echo "To stop servers, run './quickstart stop'"

    exit 0
fi

# install
if [ "x$1" == "xinstall" ]
then

    # check requirements
    which virtualenv >/dev/null

    export PYTHONPATH=`pwd`

    echo "Install yabiadmin ($YABI_ADMIN_EGG) from $EASY_INSTALL_INDEX"
    pushd yabiadmin
    virtualenv vp
    vp/bin/easy_install -f $EASY_INSTALL_INDEX $YABI_ADMIN_EGG

    # use gunicorn to fire up yabiadmin
    vp/bin/pip install gunicorn

    # database migrations
    export DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
    vp/bin/django-admin.py syncdb --noinput
    vp/bin/django-admin.py migrate

    # collect static
    vp/bin/django-admin.py collectstatic --noinput 1> collectstatic.log
    popd

    echo "Install yabibe ($YABI_BE_EGG) from $EASY_INSTALL_INDEX"
    pushd yabibe
    virtualenv vp
    vp/bin/easy_install -f $EASY_INSTALL_INDEX $YABI_BE_EGG
    popd

    echo "To run servers, type './quickstart start'"

    exit 0
fi

# clean
if [ "x$1" == "xclean" ]
then
    echo "Removing YabiAdmin virtual python and SQLite database"
    pushd yabiadmin 
    rm -rf vp
    rm -f yabiadmin_quickstart.sqlite3
    popd

    echo "Removing YabiBe virtual python"
    pushd yabibe
    rm -rf vp
    popd

    echo "Vitual python directories and SQLite database for quickstart removed."

    exit 0
fi


echo "Usage ./quickstart (install|clean|start|stop)"
