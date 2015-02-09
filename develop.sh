#!/bin/bash
#
# Script to control Yabi in dev and test
#

TOPDIR=$(cd `dirname $0`; pwd)

# break on error
set -e

ACTION="$1"
PROJECT="$2"

PORT='8000'

# yabiadmin is legacy, but occurs in many many places in code/config
PROJECT_NAME='yabiadmin'
AWS_BUILD_INSTANCE='aws_rpmbuild_centos6'
AWS_TEST_INSTANCE='aws_yabi_test'
AWS_STAGING_INSTANCE='aws_syd_yabi_staging'
TARGET_DIR="/usr/local/src/${PROJECT_NAME}"
STAGING_PIP="/usr/local/webapps/yabiadmin/bin/pip2.7"
TESTING_MODULES="pyvirtualdisplay nose selenium lettuce lettuce_webdriver"
PIP5_OPTS="--process-dependency-links"

# Default config
YABI_CONFIG="dev_postgresql"

VIRTUALENV="${TOPDIR}/virt_${PROJECT_NAME}"


usage() {
    echo ""
    echo "Usage ./develop.sh (status|test|lint|jslint|dropdb|start|stop|install|clean|purge|pipfreeze|pythonversion|syncmigrate|ci_runtests|ci_build|ci_rpm_publish|ci_staging|ci_staging_tests|ci_staging_selenium|ci_authorized_keys|ci_lint)"
    echo ""
}


# ssh setup, make sure our ccg commands can run in an automated environment
ci_ssh_agent() {
    ssh-agent > /tmp/agent.env.sh
    . /tmp/agent.env.sh
    ssh-add ~/.ssh/ccg-syd-staging-2014.pem
}


# build RPMs on ci environment
ci_build() {
    mkdir -p data
    chmod o+rwx data

    make_virtualenv
    . ${VIRTUALENV}/bin/activate
    pip install fig

    fig --project-name -f fig-rpmbuild.yml up
}


# run tests in our ci environment
ci_runtests() {
    mkdir -p data/tmp
    chmod o+rwx data
    chmod o+rwx data/tmp

    make_virtualenv
    . ${VIRTUALENV}/bin/activate
    pip install fig

    docker-kill-all
    docker-clean

    fig --project-name yabi build web
    fig --project-name yabi -f fig-test.yml up
}


# publish rpms to testing repo
ci_rpm_publish() {
    time ccg publish_testing_rpm:data/rpmbuild/RPMS/x86_64/yabi*.rpm,release=6
}


# puppet up staging which will install the latest rpm
ci_staging() {
    ccg ${AWS_STAGING_INSTANCE} boot
    ccg ${AWS_STAGING_INSTANCE} puppet
    ccg ${AWS_STAGING_INSTANCE} shutdown:120
}


# run tests on staging
ci_staging_tests() {
    # Try running syncdb -- if setup is wrong this won't work
    ccg ${AWS_STAGING_INSTANCE} dsudo:"yabiadmin syncdb --noinput"

    # Get the login page -- will find major config problems with the rpm
    STAGING_URL="https://localhost/yabi/"
    ccg ${AWS_STAGING_INSTANCE} drun:"curl --insecure -f -o /dev/null -D /dev/stdout ${STAGING_URL}"
}


# staging selenium test
ci_staging_selenium() {
    ccg ${AWS_STAGING_INSTANCE} dsudo:"${STAGING_PIP} install ${TESTING_MODULES}"
    ccg ${AWS_STAGING_INSTANCE} dsudo:'dbus-uuidgen --ensure'
    ccg ${AWS_STAGING_INSTANCE} dsudo:'chown apache:apache /var/www'
    ccg ${AWS_STAGING_INSTANCE} dsudo:'service httpd restart'
    ccg ${AWS_STAGING_INSTANCE} drunbg:"Xvfb -ac \:0"
    ccg ${AWS_STAGING_INSTANCE} dsudo:'mkdir -p lettuce && chmod o+w lettuce'
    ccg ${AWS_STAGING_INSTANCE} dsudo:"cd lettuce && DISPLAY\=\:0 YABIURL\=https\://localhost/yabi/ yabiadmin run_lettuce --with-xunit --xunit-file\=/tmp/tests.xml --app-name\=yabiadmin --traceback || true"
    ccg ${AWS_STAGING_INSTANCE} getfile:/tmp/tests.xml,./
}

# we need authorized keys setup for ssh tests
ci_authorized_keys() {
    cat tests/test_data/yabitests.pub >> ~/.ssh/authorized_keys
}


# lint using flake8
lint() {
    ${VIRTUALENV}/bin/flake8 yabiadmin/yabiadmin yabish/yabishell --count
}


# lint js, assumes closure compiler
jslint() {
    JSFILES="yabiadmin/yabiadmin/yabifeapp/static/javascript/*.js yabiadmin/yabiadmin/yabifeapp/static/javascript/account/*.js"
    for JS in $JSFILES
    do
        ${VIRTUALENV}/bin/gjslint --disable 0131 --max_line_length 100 --nojsdoc $JS
    done
}

# lint both Python and JS on CI server
ci_lint() {
    make_virtualenv
    ${VIRTUALENV}/bin/pip install 'closure-linter==2.3.13' 'flake8>=2.0,<2.1'
    lint
    jslint
}



do_nosetests() {
    . ${VIRTUALENV}/bin/activate

    XUNIT_OPTS="--with-xunit --xunit-file=tests.xml"
    COVERAGE_OPTS="--with-coverage --cover-html --cover-erase --cover-package=yabiadmin"
    NOSETESTS="nosetests -v --logging-clear-handlers ${XUNIT_OPTS}"
    IGNORES="-I sshtorque_tests.py -I torque_tests.py -I sshpbspro_tests.py"
    TEST_CASES="tests yabiadmin/yabiadmin"
    TEST_CONFIG_FILE="${TARGET_DIR}/staging_tests.conf"

    # Some tests access external services defined in a config file.
    if [ -f "${TEST_CONFIG_FILE}" ]; then
        export TEST_CONFIG_FILE
    else
        IGNORES="${IGNORES} -a !external_service"
    fi

    # Runs the end-to-end tests in the Yabitests project
    echo ${NOSETESTS} ${IGNORES} ${TEST_CASES}
    ${NOSETESTS} ${IGNORES} ${TEST_CASES}

    # ${NOSETESTS} tests.file_transfer_tests
    # ${NOSETESTS} tests.fsbackend_tests
    # ${NOSETESTS} tests.idempotency_tests
    # ${NOSETESTS} tests.localfs_connection_tests
    # ${NOSETESTS} tests.ls_tests
    # ${NOSETESTS} tests.no_setup_tests
    # ${NOSETESTS} tests.qbaseexec_command_tests
    # ${NOSETESTS} tests.rewalk_tests
    # ${NOSETESTS} tests.s3_connection_tests
    # ${NOSETESTS} tests.simple_tool_tests
    # ${NOSETESTS} tests.simple_tool_tests:LocalExecutionRedirectTest
    # ${NOSETESTS} tests.sshpbspro_tests
    # ${NOSETESTS} tests.ssh_tests
    # ${NOSETESTS} tests.sshtorque_tests
}


dropdb() {

    case ${YABI_CONFIG} in
    test_mysql)
        mysql -v -uroot -e "drop database test_yabi;" || true
        mysql -v -uroot -e "create database test_yabi default charset=UTF8 default collate utf8_bin;" || true
        ;;
    test_postgresql)
        psql -aeE -U postgres -c "alter user yabiapp createdb;" template1 && psql -aeE -U postgres -c "alter database test_yabi owner to yabiapp" template1 && psql -aeE -U yabiapp -c "drop database test_yabi" template1 && psql -aeE -U yabiapp -c "create database test_yabi;" template1
        ;;
    dev_mysql)
	echo "Drop the dev database manually:"
        echo "mysql -uroot -e \"drop database dev_yabi; create database dev_yabi default charset=UTF8 default collate utf8_bin;\""
        exit 1
        ;;
    dev_postgresql)
	echo "Drop the dev database manually:"
        echo "psql -aeE -U postgres -c \"alter user yabiapp createdb;\" template1 && psql -aeE -U yabiapp -c \"drop database dev_yabi\" template1 && psql -aeE -U yabiapp -c \"create database dev_yabi;\" template1"
        exit 1
        ;;
    *)
        echo "No YABI_CONFIG set, exiting"
        exit 1
    esac
}


stopprocess() {
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


stopyabiadmin() {
    echo "Stopping Yabi admin"
    . ${VIRTUALENV}/bin/activate || true
    uwsgi --stop yabiadmin-develop.pid || true
    stopprocess yabiadmin-develop.pid
}


stopceleryd() {
    echo "Stopping celeryd"
    stopprocess celeryd-develop.pid
}


stopyabi() {
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

make_virtualenv() {
    # check requirements
    which virtualenv > /dev/null
    virtualenv ${VIRTUALENV}
}

installyabi() {
    echo "Install yabiadmin"
    if test -e /usr/pgsql-9.3/bin; then
        export PATH=/usr/pgsql-9.3/bin:$PATH
        echo $PATH
    fi
    pushd yabiadmin
    ${VIRTUALENV}/bin/pip install ${PIP5_OPTS} -e .[dev,mysql,postgresql,tests]
    popd

    echo "Install yabish"
    pushd yabish
    ${VIRTUALENV}/bin/pip install ${PIP5_OPTS} -e .
    popd
}


startyabiadmin() {
    if is_running yabiadmin-develop.pid; then
        echo "pid file exists for yabiadmin"
        return
    fi

    echo "Launch yabiadmin (frontend) http://localhost:${PORT}"
    mkdir -p ~/yabi_data_dir
    . ${VIRTUALENV}/bin/activate
    syncmigrate
    uwsgi uwsgi/emperor.ini
}


# django syncdb, migrate and collect static
syncmigrate() {
    echo "syncdb"
    ${VIRTUALENV}/bin/django-admin.py syncdb --noinput --settings=${DJANGO_SETTINGS_MODULE} 1> syncdb-develop.log
    echo "migrate"
    ${VIRTUALENV}/bin/django-admin.py migrate --settings=${DJANGO_SETTINGS_MODULE} 1> migrate-develop.log
    echo "collectstatic"
    ${VIRTUALENV}/bin/django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 1> collectstatic-develop.log
}


startceleryd() {
    if is_running celeryd-develop.pid; then
        echo "pid file exists for celeryd"
        return
    fi

    echo "Launch celeryd (message queue)"
    CELERY_CONFIG_MODULE="settings"
    CELERYD_CHDIR=`pwd`
    CELERYD_OPTS="-A yabiadmin.backend.celerytasks -E --loglevel=DEBUG --logfile=celeryd-develop.log --pidfile=celeryd-develop.pid -Ofair"
    # Do just provisioning (provision fs and ex backends and clean_up_dynamic backends)
    #CELERYD_OPTS="$CELERYD_OPTS -Q provisioning"
    # Do just file operations (stagein and stagout tasks)
    #CELERYD_OPTS="$CELERYD_OPTS -Q file_operations"
    # Do all tasks BUT provisioning and file operations
    #CELERYD_OPTS="$CELERYD_OPTS -Q celery"
    #CELERY_LOADER="django"
    DJANGO_PROJECT_DIR="${CELERYD_CHDIR}"
    PROJECT_DIRECTORY="${CELERYD_CHDIR}"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    setsid ${VIRTUALENV}/bin/celery worker ${CELERYD_OPTS} 1>/dev/null 2>/dev/null &
}


celeryevents() {
    echo "Launch something to monitor celeryd (message queue)"
    echo "It will not work with database transports :/"
    DJANGO_PROJECT_DIR="${CELERYD_CHDIR}"
    PROJECT_DIRECTORY="${CELERYD_CHDIR}"
    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR
    echo ${DJANGO_SETTINGS_MODULE}

    # You need to be using rabbitMQ for this to work
    ${VIRTUALENV}/bin/django-admin.py celery flower --settings=${DJANGO_SETTINGS_MODULE}

    # other monitors I looked at
    #${VIRTUALENV}/bin/django-admin.py celeryd --help --settings=${DJANGO_SETTINGS_MODULE}
    #${VIRTUALENV}/bin/django-admin.py djcelerymon 9000 --settings=${DJANGO_SETTINGS_MODULE}
    #${VIRTUALENV}/bin/django-admin.py celerycam --settings=${DJANGO_SETTINGS_MODULE}
    #${VIRTUALENV}/bin/django-admin.py celery events --settings=${DJANGO_SETTINGS_MODULE}
}


startyabi() {
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

is_running() {
    test -e $1 && test -x /proc/$(cat $1)
}

yabistatus() {
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


pythonversion() {
    ${VIRTUALENV}/bin/python -V
}


pipfreeze() {
    echo 'yabiadmin pip freeze'
    ${VIRTUALENV}/bin/pip freeze
}


yabiclean() {
    echo "rm -rf ~/yabi_data_dir/*"
    rm -rf ~/yabi_data_dir/*
    rm -rf yabiadmin/scratch/*
    rm -rf yabiadmin/scratch/.uploads
    find yabiadmin -name "*.pyc" -exec rm -rf {} \;
    find yabish -name "*.pyc" -exec rm -rf {} \;
    find tests -name "*.pyc" -exec rm -rf {} \;
}


yabipurge() {
    rm -rf ${VIRTUALENV}
    rm -f *.log
}


dbtest() {
    local noseretval
    stopyabi
    dropdb
    startyabi
    trap stopyabi EXIT SIGINT SIGTERM
    do_nosetests
    exit $?
}


case ${PROJECT} in
'yabiadmin' | 'celery' |  'yabish' | '')
    ;;
*)
    usage
    exit 1
    ;;
esac

if [ "${ACTION}" = "test" ]; then
    ACTION="test_postgresql"
fi

case $ACTION in
pythonversion)
    pythonversion
    ;;
pipfreeze)
    pipfreeze
    ;;
lint)
    lint
    ;;
jslint)
    jslint
    ;;
ci_lint)
    ci_lint
    ;;
dropdb)
    settings
    dropdb
    ;;
syncmigrate)
    settings
    syncmigrate
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
    make_virtualenv
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
ci_runtests)
    ci_runtests
    ;;
ci_rpm_publish)
    ci_ssh_agent
    ci_rpm_publish
    ;;
ci_authorized_keys)
    ci_authorized_keys
    ;;
ci_staging)
    ci_ssh_agent
    ci_staging
    ;;
ci_staging_tests)
    ci_ssh_agent
    ci_staging_tests
    ;;
ci_staging_selenium)
    ci_ssh_agent
    ci_staging_selenium
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
