#!/bin/bash
#
# Devstack script to setup yabi
#

# break on error
set -e 

if [ "x$1" == "xstop" ]
then
    echo "Stopping devstack servers"
    set +e
    kill `cat yabiadmin-devstack.pid`
    kill `cat celeryd-quickstart.pid`
    kill `cat yabibe-devstack.pid` 

    # delay to allow file handles to free
    sleep 3

    exit 0
fi

# start backend, celery and frontend
if [ "x$1" == "xstart" ]
then

    echo "Launch yabiadmin (frontend) http://localhost:8000"
    export PYTHON_PATH=yabiadmin
    virt_yabiadmin/bin/gunicorn_django -b 0.0.0.0:8000 --pid=yabiadmin-devstack.pid --log-file=yabiadmin-devstack.log --daemon yabiadmin.settings -t 300 -w 5

    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="settings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="--logfile=celeryd-devstack.log --pidfile=celeryd-devstack.pid"
    CELERY_LOADER="django"
    DJANGO_SETTINGS_MODULE="yabiadmin.settings"
    DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
    PROJECT_DIRECTORY="$CELERYD_CHDIR"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    virt_yabiadmin/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &

    echo "Launch yabibe (backend)"
    mkdir -p /tmp/run/backend/certificates
    mkdir -p /tmp/run/backend/fifos
    mkdir -p /tmp/run/backend/tasklets
    mkdir -p /tmp/run/backend/temp

    export PYTHON_PATH=yabibe
    export YABICONF="~/.yabi/yabi.conf"
    virt_yabibe/bin/yabibe --pidfile=yabibe-devstack.pid

    echo "To stop servers, run './devstack.sh stop'"

    exit 0
fi

echo "Usage ./devstack.sh (start|stop)"
