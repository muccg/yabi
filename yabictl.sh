#!/bin/sh
#
# Script to control Yabi in dev and test
#

# break on error
set -e 

EASY_INSTALL="https://s3-ap-southeast-1.amazonaws.com/http-sing/python/centos/6/noarch/index.html"

ARGV="$@"

function stopyabiadmin() {
    kill `cat yabiadmin-yabictl.pid`
}

function stopceleryd() {
    kill `cat celeryd-yabictl.pid`
}

function stopyabibe() {
    kill `cat yabibe-yabictl.pid`
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
    virtualenv virt_yabiadmin
    virt_yabiadmin/bin/easy_install -f $EASY_INSTALL yabiadmin/

    echo "Install yabibe"
    virt_yabiadmin/bin/easy_install -f $EASY_INSTALL yabibe/

    echo "Install yabish"
    virt_yabiadmin/bin/easy_install -f $EASY_INSTALL yabish/
}

function startyabiadmin() {
    echo "Launch yabiadmin (frontend) http://localhost:8000"
    export PYTHON_PATH=yabiadmin
    mkdir -p ~/yabi_data_dir
    virt_yabiadmin/bin/django-admin.py syncdb --noinput --settings=yabiadmin.settings 1> syncdb-yabictl.log
    virt_yabiadmin/bin/django-admin.py migrate --settings=yabiadmin.settings 1> migrate-yabictl.log
    virt_yabiadmin/bin/django-admin.py collectstatic --noinput --settings=yabiadmin.settings 1> collectstatic-yabictl.log
    virt_yabiadmin/bin/gunicorn_django -b 0.0.0.0:8000 --pid=yabiadmin-yabictl.pid --log-file=yabiadmin-yabictl.log --daemon yabiadmin.settings -t 300 -w 5
}

function startceleryd() {
    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="settings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="--logfile=celeryd-yabictl.log --pidfile=celeryd-yabictl.pid"
    CELERY_LOADER="django"
    DJANGO_SETTINGS_MODULE="yabiadmin.settings"
    DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
    PROJECT_DIRECTORY="$CELERYD_CHDIR"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    virt_yabiadmin/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &
}

function startyabibe() {
    echo "Launch yabibe (backend)"
    mkdir -p ~/.yabi/run/backend/certificates
    mkdir -p ~/.yabi/run/backend/fifos
    mkdir -p ~/.yabi/run/backend/tasklets
    mkdir -p ~/.yabi/run/backend/temp

    export PYTHON_PATH=yabibe
    export YABICONF="~/.yabi/yabi.conf"
    virt_yabiadmin/bin/yabibe --pidfile=yabibe-yabictl.pid
}

function start() {
    startyabiadmin
    startceleryd
    startyabibe
}

function status() {
    echo "TODO"
}

case $ARGV in
stopyabiadmin)
    stopyabiadmin
    ;;
stopyabibe)
    stopyabibe
    ;;
stopceleryd)
    stopceleryd
    ;;
stop)
    stop
    ;;
startyabiadmin)
    startyabiadmin
    ;;
startyabibe)
    startyabibe
    ;;
startceleryd)
    startceleryd
    ;;
start)
    start
    ;;
status)
    status
    ;;
*)
    echo "Usage ./yabictl.sh (status|start|startyabibe|startyabiadmin|startceleryd|stop|stopyabibe|stopyabiadmin|stopceleryd)"
esac

