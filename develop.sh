#!/bin/bash
#
# Script to control Yabi in dev and test
#

# break on error
set -e 

ACTION="$1"
PROJECT="$2"

PORT='8000'

PROJECT_NAME='yabi'
AWS_BUILD_INSTANCE='aws_rpmbuild_centos6'
AWS_TEST_INSTANCE='aws_yabi_test'
TARGET_DIR="/usr/local/src/${PROJECT_NAME}"
CLOSURE="/usr/local/closure/compiler.jar"
MODULES="MySQL-python==1.2.3 psycopg2==2.4.6 Werkzeug flake8 requests==1.2.0 gunicorn django-nose nose==1.2.1"
PIP_OPTS='-v -M --download-cache ~/.pip/cache'


if [ "${YABI_CONFIG}" = "" ]; then
    YABI_CONFIG="dev_mysql"
fi


function usage() {
    echo ""
    echo "Usage ./develop.sh (status|test_mysql|test_postgresql|test_yabiadmin|lint|jslint|dropdb|start|stop|install|clean|purge|pipfreeze|pythonversion|ci_remote_build|ci_remote_test|ci_rpm_publish|ci_remote_destroy|ci_authorized_keys) (yabiadmin|celery|yabish)"
    echo ""
}


function project_needed() {
    if ! test ${PROJECT}; then
        usage
        exit 1
    fi
}


function settings() {
    case ${YABI_CONFIG} in
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

    echo "Config: ${YABI_CONFIG}"
}


# ssh setup, make sure our ccg commands can run in an automated environment
function ci_ssh_agent() {
    ssh-agent > /tmp/agent.env.sh
    source /tmp/agent.env.sh
    ssh-add ~/.ssh/ccg-syd-staging.pem
}


# build RPMs on a remote host from ci environment
function ci_remote_build() {
    time ccg ${AWS_BUILD_INSTANCE} boot
    time ccg ${AWS_BUILD_INSTANCE} puppet
    time ccg ${AWS_BUILD_INSTANCE} shutdown:50

    EXCLUDES="('bootstrap'\, '.hg'\, 'virt*'\, '*.log'\, '*.rpm'\, 'screenshots'\, 'docs')"
    SSH_OPTS="-o StrictHostKeyChecking\=no"
    RSYNC_OPTS="-l"
    time ccg ${AWS_BUILD_INSTANCE} rsync_project:local_dir=./,remote_dir=${TARGET_DIR}/,ssh_opts="${SSH_OPTS}",extra_opts="${RSYNC_OPTS}",exclude="${EXCLUDES}",delete=True
    time ccg ${AWS_BUILD_INSTANCE} build_rpm:centos/yabi.spec,src=${TARGET_DIR}

    mkdir -p build
    ccg ${AWS_BUILD_INSTANCE} getfile:rpmbuild/RPMS/x86_64/yabi*.rpm,build/
}

# run tests on a remote host from ci environment
function ci_remote_test() {
    time ccg ${AWS_TEST_INSTANCE} boot
    time ccg ${AWS_TEST_INSTANCE} puppet
    time ccg ${AWS_TEST_INSTANCE} shutdown:60

    EXCLUDES="('bootstrap'\, '.hg'\, 'virt*'\, '*.log'\, '*.rpm'\, 'screenshots'\, 'docs'\, '*.pyc')"
    SSH_OPTS="-o StrictHostKeyChecking\=no"
    RSYNC_OPTS="-l"
    time ccg ${AWS_TEST_INSTANCE} rsync_project:local_dir=./,remote_dir=${TARGET_DIR}/,ssh_opts="${SSH_OPTS}",extra_opts="${RSYNC_OPTS}",exclude="${EXCLUDES}",delete=True
    time ccg ${AWS_TEST_INSTANCE} drun:"cd ${TARGET_DIR} && ./develop.sh purge"
    time ccg ${AWS_TEST_INSTANCE} drun:"cd ${TARGET_DIR} && ./develop.sh install"
    time ccg ${AWS_TEST_INSTANCE} drun:"cd ${TARGET_DIR} && ./develop.sh test_mysql"
}


# publish rpms 
function ci_rpm_publish() {
    time ccg ${AWS_BUILD_INSTANCE} publish_rpm:build/yabi*.rpm,release=6
}


# destroy our ci build server
function ci_remote_destroy() {
    ccg ${AWS_BUILD_INSTANCE} destroy
}


# we need authorized keys setup for ssh tests
function ci_authorized_keys() {
    cat tests/test_data/yabitests.pub >> ~/.ssh/authorized_keys
}


# lint using flake8
function lint() {
    project_needed
    virt_yabiadmin/bin/flake8 ${PROJECT} --ignore=E501 --count
}


# lint js, assumes closure compiler
function jslint() {
    JSFILES="yabiadmin/yabiadmin/yabifeapp/static/javascript/*.js yabiadmin/yabiadmin/yabifeapp/static/javascript/account/*.js"
    for JS in $JSFILES
    do
        java -jar ${CLOSURE} --js $JS --js_output_file output.js --warning_level DEFAULT --summary_detail_level 3
    done
}


function nosetests() {
    source virt_yabiadmin/bin/activate

    # Runs the end-to-end tests in the Yabitests project
    virt_yabiadmin/bin/nosetests --with-xunit --xunit-file=tests.xml -I sshtorque_tests.py -I torque_tests.py -I sshpbspro_tests.py -v -w tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.simple_tool_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.s3_connection_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.ssh_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.sshpbspro_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.sshtorque_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.backend_execution_restriction_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.localfs_connection_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.rewalk_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.file_transfer_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.ssh_tests
    #virt_yabiadmin/bin/nosetests -v -w tests tests.idempotency_tests
}

function noseidempotency() {
    source virt_yabiadmin/bin/activate
    virt_yabiadmin/bin/nosetests --nocapture --with-xunit --xunit-file=tests.xml -w tests tests.idempotency_tests -v
}

function nosestatuschange() {
    source virt_yabiadmin/bin/activate
    virt_yabiadmin/bin/nosetests --with-xunit --xunit-file=tests.xml -w tests tests.status_tests -v 
}

function noseyabiadmin() {
    source virt_yabiadmin/bin/activate
    # Runs the unit tests in the Yabiadmin project
    virt_yabiadmin/bin/nosetests --with-xunit --xunit-file=yabiadmin.xml -v -w yabiadmin/yabiadmin 
}


function nose_collect() {
    source virt_yabiadmin/bin/activate
    virt_yabiadmin/bin/nosetests -v -w tests --collect-only
}


function dropdb() {

    case ${YABI_CONFIG} in
    test_mysql)
        mysql -v -uroot -e "drop database test_yabi;" || true
        mysql -v -uroot -e "create database test_yabi default charset=UTF8;" || true
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
    if ! test -e $1; then
        echo "PID file '$1' doesn't exist"
        return
    fi
    local pid=`cat $1`
    local pgrpid=""
    if test "kill_process_group" == "$2"; then
        pgrpid=$(ps -o pgrp= --pid $pid | tr -d ' ')
    fi
    
    if test -z $pgrpid; then
        kill $pid
    else
        kill -- -$pgrpid
    fi
    
    for I in {1..30} 
    do
        if ps --pid $pid > /dev/null; then
            sleep 1
        else
            break
        fi
    done

    if ps --pid $pid > /dev/null; then
        if test -z $pgrpid; then
            kill -9 $pid
        else
            kill -9 -- -$pgrpid
        fi
        echo "Forced stop"
    fi

    if test -e $1; then
        rm -f $1
    fi
    set -e
}


function stopyabiadmin() {
    echo "Stopping Yabi admin"
    stopprocess yabiadmin-develop.pid "kill_process_group"
}


function stopceleryd() {
    echo "Stopping celeryd"
    stopprocess celeryd-develop.pid
}


function stopyabi() {
    case ${PROJECT} in
    'yabiadmin')
        stopyabiadmin
        stopceleryd
        ;;
    'celery')
        stopceleryd
        ;;
    '')
        stopyabiadmin
        stopceleryd
        ;;
    *)
        echo "Cannot stop ${PROJECT}"
        usage
        exit 1
        ;;
    esac
}


function installyabi() {
    # check requirements
    which virtualenv >/dev/null

    echo "Install yabiadmin"
    virtualenv virt_yabiadmin
    pushd yabiadmin
    ../virt_yabiadmin/bin/pip install ${PIP_OPTS} pip-crate
    ../virt_yabiadmin/bin/pip-crate install ${PIP_OPTS} -e .
    popd
    virt_yabiadmin/bin/pip-crate install ${PIP_OPTS} ${MODULES}

    echo "Install yabish"
    pushd yabish
    ../virt_yabiadmin/bin/pip-crate install ${PIP_OPTS} -e .
    popd
}


function startyabiadmin() {
    if test -e yabiadmin-develop.pid; then
        echo "pid file exists for yabiadmin"
        return
    fi

    echo "Launch yabiadmin (frontend) http://localhost:${PORT}"
    mkdir -p ~/yabi_data_dir
    . virt_yabiadmin/bin/activate
    virt_yabiadmin/bin/django-admin.py syncdb --noinput --settings=${DJANGO_SETTINGS_MODULE} 1> syncdb-develop.log
    virt_yabiadmin/bin/django-admin.py migrate --settings=${DJANGO_SETTINGS_MODULE} 1> migrate-develop.log
    virt_yabiadmin/bin/django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 1> collectstatic-develop.log
    case ${YABI_CONFIG} in
    test_*)
        virt_yabiadmin/bin/gunicorn_django -b 0.0.0.0:${PORT} --pid=yabiadmin-develop.pid --log-file=yabiadmin-develop.log --daemon ${DJANGO_SETTINGS_MODULE} -t 300 -w 5
        ;;
    *)
        virt_yabiadmin/bin/django-admin.py runserver_plus 0.0.0.0:${PORT} --settings=${DJANGO_SETTINGS_MODULE} > yabiadmin-develop.log 2>&1 &
        echo $! > yabiadmin-develop.pid
    esac
}


function startceleryd() {
    if test -e celeryd-develop.pid; then
        echo "pid file exists for celeryd"
        return
    fi

    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="settings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="-E --loglevel=INFO --logfile=celeryd-develop.log --pidfile=celeryd-develop.pid"
    CELERY_LOADER="django"
    DJANGO_PROJECT_DIR="${CELERYD_CHDIR}"
    PROJECT_DIRECTORY="${CELERYD_CHDIR}"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    setsid virt_yabiadmin/bin/celeryd ${CELERYD_OPTS} 1>/dev/null 2>/dev/null &
}


function celeryevents() {
    echo "Launch something to monitor celeryd (message queue)"
    echo "It will not work with database transports :/"
    DJANGO_PROJECT_DIR="${CELERYD_CHDIR}"
    PROJECT_DIRECTORY="${CELERYD_CHDIR}"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    echo ${DJANGO_SETTINGS_MODULE}

    # You need to be using rabbitMQ for this to work
    virt_yabiadmin/bin/django-admin.py celery flower --settings=${DJANGO_SETTINGS_MODULE}

    # other monitors I looked at
    #virt_yabiadmin/bin/django-admin.py celeryd --help --settings=${DJANGO_SETTINGS_MODULE}
    #virt_yabiadmin/bin/django-admin.py djcelerymon 9000 --settings=${DJANGO_SETTINGS_MODULE}
    #virt_yabiadmin/bin/django-admin.py celerycam --settings=${DJANGO_SETTINGS_MODULE}
    #virt_yabiadmin/bin/django-admin.py celery events --settings=${DJANGO_SETTINGS_MODULE}
}


function startyabi() {
    case ${PROJECT} in
    'yabiadmin')
        startyabiadmin
        startceleryd
        ;;
    'celery')
        startceleryd
        ;;
    '')
        startyabiadmin
        startceleryd
        ;;
    *)
        echo "Cannot start ${PROJECT}"
        usage
        exit 1
        ;;
    esac
}


function yabistatus() {
    set +e
    if test -e yabiadmin-develop.pid; then
        ps -f -p `cat yabiadmin-develop.pid`
    else 
        echo "No pid file for yabiadmin"
    fi
    if test -e celeryd-develop.pid; then
        ps -f -p `cat celeryd-develop.pid`
    else 
        echo "No pid file for celeryd"
    fi
    set -e
}


function pythonversion() {
    virt_yabiadmin/bin/python -V
}


function pipfreeze() {
    echo 'yabiadmin pip freeze'
    virt_yabiadmin/bin/pip freeze
}


function yabiclean() {
    echo "rm -rf ~/yabi_data_dir/*"
    rm -rf ~/yabi_data_dir/*
    rm -rf yabiadmin/scratch/*
    rm -rf yabiadmin/scratch/.uploads
    find yabiadmin -name "*.pyc" -exec rm -rf {} \;
    find yabish -name "*.pyc" -exec rm -rf {} \;
    find tests -name "*.pyc" -exec rm -rf {} \;
}


function yabipurge() {
    rm -rf virt_yabiadmin
    rm -f *.log
}


function dbtest() {
    stopyabi
    dropdb
    startyabi
    nosetests
    #noseidempotency
    #nosestatuschange
    stopyabi
}


function yabiadmintest() {
    stopyabi
    yabiclean
    dropdb
    startyabi
    noseyabiadmin
    stopyabi
}


case ${PROJECT} in
'yabiadmin' | 'celery' |  'yabish' | '')
    ;;
*)
    usage
    exit 1
    ;;
esac

case $ACTION in
pythonversion)
    pythonversion
    ;;
pipfreeze)
    pipfreeze
    ;;
test_mysql)
    YABI_CONFIG="test_mysql"
    settings
    dbtest
    ;;
test_postgresql)
    YABI_CONFIG="test_postgresql"
    settings
    dbtest
    ;;
test_yabiadmin_mysql)
    YABI_CONFIG="test_mysql"
    settings
    yabiadmintest
    ;;
lint)
    lint
    ;;
jslint)
    jslint
    ;;
dropdb)
    settings
    dropdb
    ;;
stop)
    settings
    stopyabi
    ;;
start)
    settings
    startyabi
    ;;
status)
    yabistatus
    ;;
install)
    settings
    stopyabi
    time installyabi
    ;;
celeryevents)
    settings
    celeryevents
    ;;
ci_remote_build)
    ci_ssh_agent
    ci_remote_build
    ;;
ci_remote_test)
    ci_ssh_agent
    ci_remote_test
    ;;
ci_remote_destroy)
    ci_ssh_agent
    ci_remote_destroy
    ;;
ci_rpm_publish)
    ci_ssh_agent
    ci_rpm_publish
    ;;
ci_authorized_keys)
    ci_authorized_keys
    ;;
clean)
    settings
    stopyabi
    yabiclean 
    ;;
purge)
    settings
    stopyabi
    yabiclean
    yabipurge
    ;;
*)
    usage
    ;;
esac
