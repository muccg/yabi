#!/bin/sh
#
# Script to control Yabi for quickstart
#

# break on error
set -e 

EASY_INSTALL="http://s3-ap-southeast-2.amazonaws.com/http-syd/python/centos/6/noarch/index.html"
YABI_ADMIN_EGG="yabiadmin==0.2"
YABI_BE_EGG="yabibe==0.2"

ARGV="$@"

function stopyabiadmin() {
    if test -e yabiadmin-quickstart.pid; then
        echo "Stopping yabiadmin"
        kill `cat yabiadmin-quickstart.pid`
        return
    fi
    echo "no pid file for yabiadmin"
}

function stopceleryd() {
    if test -e celeryd-quickstart.pid; then
        echo "Stopping celeryd"
        kill `cat celeryd-quickstart.pid`
        return
    fi
    echo "no pid file for celeryd"
}

function stopyabibe() {
    if test -e yabibe-quickstart.pid; then
        echo "Stopping yabibe"
        kill `cat yabibe-quickstart.pid`
        sleep 3
        return
    fi
    echo "no pid file for yabibe"
}

function stop() {
    stopyabiadmin
    stopceleryd
    stopyabibe
}

function install() {
    # check requirements
    which virtualenv >/dev/null

    export PYTHONPATH=`pwd`

    echo "Install yabiadmin"
    virtualenv --system-site-packages virt_quickstart
    virt_quickstart/bin/easy_install -f $EASY_INSTALL $YABI_ADMIN_EGG

    echo "Install yabibe"
    virt_quickstart/bin/easy_install -f $EASY_INSTALL $YABI_BE_EGG
}

function startyabiadmin() {
    if test -e yabiadmin-quickstart.pid; then
        echo "pid file exists for yabiadmin"
        return
    fi

    echo "Launch yabiadmin (frontend) http://localhost:8080"
    mkdir -p ~/yabi_data_dir
    export DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
    virt_quickstart/bin/django-admin.py syncdb --noinput --settings=yabiadmin.quickstartsettings 1> syncdb-quickstart.log
    virt_quickstart/bin/django-admin.py migrate --settings=yabiadmin.quickstartsettings 1> migrate-quickstart.log
    virt_quickstart/bin/django-admin.py collectstatic --noinput --settings=yabiadmin.quickstartsettings 1> collectstatic-quickstart.log
    virt_quickstart/bin/gunicorn_django -b 0.0.0.0:8080 --pid=yabiadmin-quickstart.pid --log-file=yabiadmin-quickstart.log --daemon --settings=yabiadmin.quickstartsettings -t 300 -w 5
}

function startceleryd() {
    if test -e celeryd-quickstart.pid; then
        echo "pid file exists for celeryd"
        return
    fi

    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="quickstartsettings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="--logfile=celeryd-quickstart.log --pidfile=celeryd-quickstart.pid"
    CELERY_LOADER="django"
    DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
    DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
    PROJECT_DIRECTORY="$CELERYD_CHDIR"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    virt_quickstart/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &
}

function startyabibe() {
    if test -e yabibe-quickstart.pid; then
        echo "pid file exists for yabibe"
        return
    fi

    echo "Launch yabibe (backend)"
    mkdir -p /tmp/yabibe-quickstart/run/backend/certificates
    mkdir -p /tmp/yabibe-quickstart/run/backend/fifos
    mkdir -p /tmp/yabibe-quickstart/run/backend/tasklets
    mkdir -p /tmp/yabibe-quickstart/run/backend/temp
    unset YABICONF
    export QUICKSTART="1" 
    virt_quickstart/bin/yabibe --pidfile=yabibe-quickstart.pid
}

function start() {
    startyabiadmin
    startceleryd
    startyabibe
}

function status() {
    if test -e yabibe-quickstart.pid; then
        ps -f -p `cat yabibe-quickstart.pid`
    else 
        echo "No pid file for yabibe"
    fi
    if test -e yabiadmin-quickstart.pid; then
        ps -f -p `cat yabiadmin-quickstart.pid`
    else 
        echo "No pid file for yabiadmin"
    fi
    if test -e celeryd-quickstart.pid; then
        ps -f -p `cat celeryd-quickstart.pid`
    else 
        echo "No pid file for celeryd"
    fi
}

function clean() {
    echo "Removing Yabi virtual python and SQLite database"
    rm -rf virt_quickstart
    rm -f yabiadmin_quickstart.sqlite3

    echo "Removing /tmp/yabibe-quickstart"
    rm -rf /tmp/yabibe-quickstart

    echo "Vitual python directories and SQLite database for quickstart removed."
}


case $ARGV in
stop)
    stop
    ;;
start)
    start
    ;;
status)
    status
    ;;
install)
    stop
    install
    ;;
clean)
    stop
    clean
    ;;
*)
    echo "Usage ./quickstart.sh (status|start|stop|install|clean)"
esac

