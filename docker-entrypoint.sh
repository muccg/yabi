#!/bin/bash


# wait for a given host:port to become available
#
# $1 host
# $2 port
function dockerwait {
    while ! exec 6<>/dev/tcp/$1/$2; do
        echo "$(date) - waiting to connect $1 $2"
        sleep 5
    done
    echo "$(date) - connected to $1 $2"

    exec 6>&-
    exec 6<&-
}


# wait for services to become available
# this prevents race conditions using fig
function wait_for_services {
    if [[ "$WAIT_FOR_QUEUE" ]] ; then
        dockerwait $QUEUESERVER $QUEUEPORT
    fi
    if [[ "$WAIT_FOR_DB" ]] ; then
        dockerwait $DBSERVER $DBPORT
    fi
    if [[ "$WAIT_FOR_CACHE" ]] ; then
        dockerwait $CACHESERVER $CACHEPORT
    fi
    if [[ "$WAIT_FOR_WEB" ]] ; then
        dockerwait $WEBSERVER $WEBPORT
    fi
    if [[ "$WAIT_FOR_SSH" ]] ; then
        dockerwait $SSHSERVER $SSHPORT
    fi
    if [[ "$WAIT_FOR_S3" ]] ; then
        dockerwait $S3SERVER $S3PORT
    fi
    if [[ "$WAIT_FOR_KERBEROS" ]] ; then
        dockerwait $KERBEROSSERVER $KERBEROSPORT
    fi
    if [[ "$WAIT_FOR_LDAP" ]] ; then
        dockerwait $LDAPSERVER $LDAPPORT
    fi
}


function defaults {
    : ${QUEUESERVER:="mq"}
    : ${QUEUEPORT:="5672"}
    : ${DBSERVER:="db"}
    : ${DBPORT:="5432"}
    : ${WEBSERVER="web"}
    : ${WEBPORT="8000"}
    : ${CACHESERVER="cache"}
    : ${CACHEPORT="11211"}
    : ${SSHSERVER="ssh"}
    : ${SSHPORT="22"}
    : ${S3SERVER="s3"}
    : ${S3PORT="4569"}
    : ${KERBEROSSERVER="krb5"}
    : ${KERBEROSPORT="88"}
    : ${LDAPSERVER="ldap"}
    : ${LDAPPORT="389"}

    : ${DBUSER="webapp"}
    : ${DBNAME="${DBUSER}"}
    : ${DBPASS="${DBUSER}"}
    export DBSERVER DBPORT DBUSER DBNAME DBPASS
}


function celery_defaults {
    : ${CELERY_CONFIG_MODULE="settings"}
    : ${CELERYD_CHDIR=`pwd`}
    : ${CELERY_BROKER="amqp://guest:guest@${QUEUESERVER}:${QUEUEPORT}//"}
    : ${CELERY_APP="app.celerytasks"}
    : ${CELERY_LOGLEVEL="DEBUG"}
    : ${CELERY_OPTIMIZATION="fair"}
    if [[ -z "$CELERY_AUTORELOAD" ]] ; then
        CELERY_AUTORELOAD=""
    else
        CELERY_AUTORELOAD="--autoreload"
    fi
    : ${CELERY_OPTS="-A ${CELERY_APP} -E --loglevel=${CELERY_LOGLEVEL} -O${CELERY_OPTIMIZATION} -b ${CELERY_BROKER} ${CELERY_AUTORELOAD}"}
    : ${DJANGO_PROJECT_DIR="${CELERYD_CHDIR}"}
    : ${PROJECT_DIRECTORY="${CELERYD_CHDIR}"}

    echo "CELERY_CONFIG_MODULE is ${CELERY_CONFIG_MODULE}"
    echo "CELERYD_CHDIR is ${CELERYD_CHDIR}"
    echo "CELERY_BROKER is ${CELERY_BROKER}"
    echo "CELERY_APP is ${CELERY_APP}"
    echo "CELERY_LOGLEVEL is ${CELERY_LOGLEVEL}"
    echo "CELERY_OPTIMIZATION is ${CELERY_OPTIMIZATION}"
    echo "CELERY_AUTORELOAD is ${CELERY_AUTORELOAD}"
    echo "CELERY_OPTS is ${CELERY_OPTS}"
    echo "DJANGO_PROJECT_DIR is ${DJANGO_PROJECT_DIR}"
    echo "PROJECT_DIRECTORY is ${PROJECT_DIRECTORY}"

    export CELERY_CONFIG_MODULE CELERYD_CHDIR CELERY_BROKER CELERY_APP CELERY_LOGLEVEL CELERY_OPTIMIZATION CELERY_AUTORELOAD CELERY_OPTS DJANGO_PROJECT_DIR PROJECT_DIRECTORY
}


function django_defaults {
    : ${DEPLOYMENT="dev"}
    : ${PRODUCTION=0}
    : ${DEBUG=1}
    : ${MEMCACHE="${CACHESERVER}:${CACHEPORT}"}
    : ${WRITABLE_DIRECTORY="/data/scratch"}
    : ${STATIC_ROOT="/data/static"}
    : ${MEDIA_ROOT="/data/static/media"}
    : ${LOG_DIRECTORY="/data/log"}
    : ${DJANGO_SETTINGS_MODULE="django.settings"}

    echo "DEPLOYMENT is ${DEPLOYMENT}"
    echo "PRODUCTION is ${PRODUCTION}"
    echo "DEBUG is ${DEBUG}"
    echo "MEMCACHE is ${MEMCACHE}"
    echo "WRITABLE_DIRECTORY is ${WRITABLE_DIRECTORY}"
    echo "STATIC_ROOT is ${STATIC_ROOT}"
    echo "MEDIA_ROOT is ${MEDIA_ROOT}"
    echo "LOG_DIRECTORY is ${LOG_DIRECTORY}"
    echo "DJANGO_SETTINGS_MODULE is ${DJANGO_SETTINGS_MODULE}"
    
    export DEPLOYMENT PRODUCTION DEBUG DBSERVER MEMCACHE WRITABLE_DIRECTORY STATIC_ROOT MEDIA_ROOT LOG_DIRECTORY DJANGO_SETTINGS_MODULE
}


echo "HOME is ${HOME}"
echo "WHOAMI is `whoami`"

defaults
django_defaults
wait_for_services

# celery entrypoint
if [ "$1" = 'celery' ]; then
    echo "[Run] Starting celery"

    celery_defaults

    if [ "$2" = 'restart' ]; then
        python /app/pool_restart.py
        exit $?
    fi

    celery worker ${CELERY_OPTS} 2>&1 | tee /data/celery.log
    exit $?
fi

# uwsgi entrypoint
if [ "$1" = 'uwsgi' ]; then
    echo "[Run] Starting uwsgi"

    : ${UWSGI_OPTS="/app/uwsgi/docker.ini"}
    echo "UWSGI_OPTS is ${UWSGI_OPTS}"

    django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-collectstatic.log
    django-admin.py syncdb --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-syncdb.log
    django-admin.py migrate --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-migrate.log
    uwsgi ${UWSGI_OPTS} 2>&1 | tee /data/uwsgi.log
    exit $?
fi

# runserver entrypoint
if [ "$1" = 'runserver' ]; then
    echo "[Run] Starting runserver"

    celery_defaults

    : ${RUNSERVER_OPTS="runserver_plus 0.0.0.0:${WEBPORT} --settings=${DJANGO_SETTINGS_MODULE}"}
    echo "RUNSERVER_OPTS is ${RUNSERVER_OPTS}"

    django-admin.py syncdb --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/runserver-syncdb.log
    django-admin.py migrate --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/runserver-migrate.log
    django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/runserver-collectstatic.log
    django-admin.py ${RUNSERVER_OPTS} 2>&1 | tee /data/runserver.log
    exit $?
fi

# runtests entrypoint
if [ "$1" = 'runtests' ]; then
    echo "[Run] Starting tests"

    XUNIT_OPTS="--with-xunit --xunit-file=tests.xml"
    NOSETESTS="nosetests -v --logging-clear-handlers ${XUNIT_OPTS}"
    IGNORES="-I sshtorque_tests.py -I torque_tests.py -I sshpbspro_tests.py -a !external_service"

    # Setting TEST_CASES in fig file allows you to choose tests
    : ${TEST_CASES="/app/tests /app/yabi/yabi"}

    # tests want to import module tests
    export PYTHONPATH=/app

    echo ${NOSETESTS} ${IGNORES} ${TEST_CASES}
    ${NOSETESTS} ${IGNORES} ${TEST_CASES} 2>&1 | tee /data/nosetests.log

    exit $?
fi

# lettuce entrypoint
if [ "$1" = 'lettuce' ]; then
    echo "[Run] Starting lettuce"

    django-admin.py run_lettuce --with-xunit --xunit-file=/data/tests.xml 2>&1 | tee /data/lettuce.log
    exit $?
fi

echo "[RUN]: Builtin command not provided [lettuce|runtests|runserver|celery|uwsgi]"
echo "[RUN]: $@"

exec "$@"
