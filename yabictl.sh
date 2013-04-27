#!/bin/bash
#
# Script to control Yabi in dev and test
#

# break on error
set -e 

ARGV="$@"

if [ "$YABI_CONFIG" = "" ]; then
    YABI_CONFIG="dev_mysql"
fi

function settings() {
    case $YABI_CONFIG in
    test_mysql)
        export DJANGO_SETTINGS_MODULE="yabiadmin.testmysqlsettings"
        ;;
    test_postgresql)
        export DJANGO_SETTINGS_MODULE="yabiadmin.testpostgresqlsettings"
        ;;
    dev_mysql)
        export DJANGO_SETTINGS_MODULE="yabiadmin.settings"
        ;;
    dev_postgresql)
        export DJANGO_SETTINGS_MODULE="yabiadmin.postgresqlsettings"
        ;;
    *)
        echo "No YABI_CONFIG set, exiting"
        exit 1
    esac

    echo "Config: $YABI_CONFIG"
}

function nose() {
    source virt_yabiadmin/bin/activate
    # Runs the end-to-end tests in the Yabitests project
    virt_yabiadmin/bin/nosetests -v -w yabitests
    #virt_yabiadmin/bin/nosetests -v -w yabitests yabitests.backend_restart_tests

    # Runs the unit tests in the Yabiadmin project
    virt_yabiadmin/bin/nosetests -v -w yabiadmin/yabiadmin 
}

function nose_collect() {
    virt_yabiadmin/bin/nosetests -v -w yabitests --collect-only
}

function dropdb() {

    case $YABI_CONFIG in
    test_mysql)
        mysql -v -uroot -e "drop database test_yabi; create database test_yabi default charset=UTF8;"
        ;;
    test_postgresql)
        psql -aeE -U postgres -c "SELECT pg_terminate_backend(pg_stat_activity.procpid) FROM pg_stat_activity where pg_stat_activity.datname = 'test_yabi'" && psql -aeE -U postgres -c "alter user yabminapp createdb;" template1 && psql -aeE -U postgres -c "alter database test_yabi owner to yabminapp" template1 && psql -aeE -U yabminapp -c "drop database test_yabi" template1 && psql -aeE -U yabminapp -c "create database test_yabi;" template1
        ;;
    dev_mysql)
	echo "Drop the dev database manually:"
        echo "mysql -uroot -e \"drop database dev_yabi; create database dev_yabi default charset=UTF8;\""
        exit 1
        ;;
    dev_postgresql)
	echo "Drop the dev database manually:"
        echo "psql -aeE -U postgres -c \"SELECT pg_terminate_backend(pg_stat_activity.procpid) FROM pg_stat_activity where pg_stat_activity.datname = 'dev_yabi'\" && psql -aeE -U postgres -c \"alter user yabminapp createdb;\" template1 && psql -aeE -U yabminapp -c \"drop database dev_yabi\" template1 && psql -aeE -U yabminapp -c \"create database dev_yabi;\" template1"
        exit 1
        ;;
    *)
        echo "No YABI_CONFIG set, exiting"
        exit 1
    esac
}

function stopprocess() {
    set +e
    if test -e $1; then
        kill `cat $1`
    fi
    
    for I in {1..10} 
    do
        if test -e $1; then
            sleep 1
        else
            break
        fi
    done

    if test -e $1; then
        kill -9 `cat $1`
        rm -f $1
        echo "Forced stop"
    fi
}

function stopyabiadmin() {
    echo "Stopping Yabi admin"
    stopprocess yabiadmin-yabictl.pid
}

function stopceleryd() {
    echo "Stopping celeryd"
    stopprocess celeryd-yabictl.pid
}

function stopyabibe() {
    echo "Stopping Yabi backend"
    stopprocess yabibe-yabictl.pid
}

function stopall() {
    stopyabiadmin
    stopceleryd
    stopyabibe
}

function yabiinstall() {
    # check requirements
    which virtualenv >/dev/null

    echo "Install yabiadmin"
    virtualenv --system-site-packages virt_yabiadmin
    pushd yabiadmin
    ../virt_yabiadmin/bin/python setup.py develop
    popd
    virt_yabiadmin/bin/easy_install MySQL-python==1.2.3
    virt_yabiadmin/bin/easy_install psycopg2==2.0.8

    echo "Install yabibe"
    virtualenv --system-site-packages virt_yabibe
    pushd yabibe
    ../virt_yabibe/bin/python setup.py develop
    popd

    echo "Install yabish"
    pushd yabish
    ../virt_yabiadmin/bin/python setup.py develop
    popd
}

function startyabiadmin() {
    if test -e yabiadmin-yabictl.pid; then
        echo "pid file exists for yabiadmin"
        return
    fi

    echo "Launch yabiadmin (frontend) http://localhost:8000"
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

    virt_yabibe/bin/yabibe --pidfile=yabibe-yabictl.pid
}

function startall() {
    startyabiadmin
    startceleryd
    startyabibe
}

function yabistatus() {
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

function yabiclean() {
    echo "rm -rf ~/.yabi/run/backend"
    rm -rf ~/.yabi/run/backend
    find yabibe -name "*.pyc" -exec rm -rf {} \;
    find yabiadmin -name "*.pyc" -exec rm -rf {} \;
    find yabish -name "*.pyc" -exec rm -rf {} \;
    find yabitests -name "*.pyc" -exec rm -rf {} \;
}

function yabitest() {
    settings
    stopall
    dropdb
    startall
    nose
    stopall
}

case $ARGV in
test_mysql)
    YABI_CONFIG="test_mysql"
    yabitest
    ;;
test_postgresql)
    YABI_CONFIG="test_postgresql"
    yabitest
    ;;
dropdb)
    settings
    dropdb
    ;;
stopyabiadmin)
    settings
    stopyabiadmin
    ;;
stopyabibe)
    settings
    stopyabibe
    ;;
stopceleryd)
    settings
    stopceleryd
    ;;
stopall)
    settings
    stopall
    ;;
startyabiadmin)
    settings
    startyabiadmin
    ;;
startyabibe)
    settings
    startyabibe
    ;;
startceleryd)
    settings
    startceleryd
    ;;
startall)
    settings
    startall
    ;;
status)
    yabistatus
    ;;
install)
    settings
    stopall
    yabiinstall
    ;;
clean)
    settings
    stopall
    yabiclean 
    ;;
*)
    echo "Usage ./yabictl.sh (status|test_mysql|test_postgresql|dropdb|startall|startyabibe|startyabiadmin|startceleryd|stopall|stopyabibe|stopyabiadmin|stopceleryd|install|clean)"
esac

