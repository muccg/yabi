#!/bin/sh
#
# Script to control Yabi in dev and test
#

# break on error
set -e 

#EASY_INSTALL_64="-f http://http-syd.s3.amazonaws.com/python/centos/6/x86_64/index.html" 
#EASY_INSTALL_NOARCH="-f http://s3-ap-southeast-2.amazonaws.com/http-syd/python/centos/6/noarch/index.html"

ARGV="$@"

if [ "$YABI_CONFIG" = "" ]; then
    YABI_CONFIG="dev_mysql"
fi

case $YABI_CONFIG in
dev_mysql)
    export DJANGO_SETTINGS_MODULE="yabiadmin.settings"
    ;;
dev_postgres)
    export DJANGO_SETTINGS_MODULE="yabiadmin.postgresqlsettings"
    ;;
quickstart)
    echo "Can't use yabictl.sh with quickstart"
    exit 1
    ;;
*)
    echo "No YABI_CONFIG set, exiting"
    exit 1
esac

echo "Config: $YABI_CONFIG"
echo 

function stopyabiadmin() {
    if test -e yabiadmin-yabictl.pid; then
        while test -e yabiadmin-yabictl.pid
        do
            set +e
            kill `cat yabiadmin-yabictl.pid`
            echo "Stopping yabiadmin"
            sleep 1    
       done 
    else
        echo "No pid file for yabiadmin"
    fi
}

function stopceleryd() {
    if test -e celeryd-yabictl.pid; then
        echo "Stopping celeryd"
        set +e
        kill `cat celeryd-yabictl.pid`
        sleep 2

        # I've seen it hang around after a kill
        if test -e celeryd-yabictl.pid; then
            kill -9 `cat celeryd-yabictl.pid`
            rm -f celeryd-yabictl.pid
            echo "Killed celery with kill -9"
        fi
        return
    fi
    echo "no pid file for celeryd"
}

function stopyabibe() {
    if test -e yabibe-yabictl.pid; then
        echo "Stopping yabibe"
        set +e
        kill `cat yabibe-yabictl.pid`
        sleep 3
        return
    fi
    echo "no pid file for yabibe"
}

function stop() {
    stopyabibe
    stopceleryd
    stopyabiadmin
}

function install() {
    # check requirements
    which virtualenv >/dev/null

    export PYTHONPATH=`pwd`

    echo "Install yabiadmin"
    virtualenv --system-site-packages virt_yabiadmin
    virt_yabiadmin/bin/easy_install yabiadmin/
    virt_yabiadmin/bin/easy_install MySQL-python==1.2.3
    virt_yabiadmin/bin/easy_install psycopg2==2.0.8

    echo "Install yabibe"
    virt_yabiadmin/bin/easy_install yabibe/

    echo "Install yabish"
    virt_yabiadmin/bin/easy_install yabish/
}

function startyabiadmin() {
    if test -e yabiadmin-yabictl.pid; then
        echo "pid file exists for yabiadmin"
        return
    fi

    echo "Launch yabiadmin (frontend) http://localhost:8000"
    export PYTHONPATH=yabiadmin
    mkdir -p ~/yabi_data_dir
    virt_yabiadmin/bin/django-admin.py syncdb --noinput --settings=$DJANGO_SETTINGS_MODULE 1> syncdb-yabictl.log
    virt_yabiadmin/bin/django-admin.py migrate --settings=$DJANGO_SETTINGS_MODULE 1> migrate-yabictl.log
    virt_yabiadmin/bin/django-admin.py collectstatic --noinput --settings=$DJANGO_SETTINGS_MODULE 1> collectstatic-yabictl.log
    virt_yabiadmin/bin/gunicorn_django -b 0.0.0.0:8000 --pid=yabiadmin-yabictl.pid --log-file=yabiadmin-yabictl.log --daemon $DJANGO_SETTINGS_MODULE -t 300 -w 5
}

function startceleryd() {
    if test -e celeryd-yabictl.pid; then
        echo "pid file exists for celeryd"
        return
    fi

    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="settings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="--logfile=celeryd-yabictl.log --pidfile=celeryd-yabictl.pid"
    CELERY_LOADER="django"
    DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
    PROJECT_DIRECTORY="$CELERYD_CHDIR"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    virt_yabiadmin/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &
}

function startyabibe() {
    if test -e yabibe-yabictl.pid; then
        echo "pid file exists for yabibe"
        return
    fi

    echo "Launch yabibe (backend)"
    mkdir -p ~/.yabi/run/backend/certificates
    mkdir -p ~/.yabi/run/backend/fifos
    mkdir -p ~/.yabi/run/backend/tasklets
    mkdir -p ~/.yabi/run/backend/temp

    export PYTHONPATH=yabibe/yabibe
    export YABICONF="~/.yabi/yabi.conf"
    virt_yabiadmin/bin/yabibe --pidfile=yabibe-yabictl.pid
}

function start() {
    startyabiadmin
    startceleryd
    startyabibe
}

function status() {
    set +e
    if test -e yabibe-yabictl.pid; then
        ps -f -p `cat yabibe-yabictl.pid`
    else 
        echo "No pid file for yabibe"
    fi
    if test -e yabiadmin-yabictl.pid; then
        ps -f -p `cat yabiadmin-yabictl.pid`
    else 
        echo "No pid file for yabiadmin"
    fi
    if test -e celeryd-yabictl.pid; then
        ps -f -p `cat celeryd-yabictl.pid`
    else 
        echo "No pid file for celeryd"
    fi
}

function clean() {
    echo "rm -rf ~/.yabi/run/backend"
    rm -rf ~/.yabi/run/backend
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
install)
    stop
    install
    ;;
clean)
    stop
    clean 
    ;;
*)
    echo "Usage ./yabictl.sh (status|start|startyabibe|startyabiadmin|startceleryd|stop|stopyabibe|stopyabiadmin|stopceleryd|install|clean)"
esac

