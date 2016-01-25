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
# this prevents race conditions using docker-compose
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
    if [[ "$WAIT_FOR_RUNSERVER" ]] ; then
        dockerwait $RUNSERVER $RUNSERVERPORT
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
    : ${DOCKER_HOST:=$(/sbin/ip route|awk '/default/ { print $3 }')}
    : ${RUNSERVER="web"}
    : ${RUNSERVERPORT="8000"}
    : ${CACHESERVER="cache"}
    : ${CACHEPORT="11211"}
    : ${MEMCACHE="${CACHESERVER}:${CACHEPORT}"}
    : ${SSHSERVER="ssh"}
    : ${SSHPORT="22"}
    : ${S3SERVER="s3"}
    : ${S3PORT="4569"}
    : ${KERBEROSSERVER="krb5"}
    : ${KERBEROSPORT="88"}
    : ${LDAPSERVER="ldap"}
    : ${LDAPPORT="389"}
    : ${YABIURL="http://$DOCKER_HOST:$RUNSERVERPORT/"}

    : ${DBUSER="webapp"}
    : ${DBNAME="${DBUSER}"}
    : ${DBPASS="${DBUSER}"}

    export DBSERVER DBPORT DBUSER DBNAME DBPASS DOCKER_HOST YABIURL
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
    echo "DEPLOYMENT is ${DEPLOYMENT}"
    echo "PRODUCTION is ${PRODUCTION}"
    echo "DEBUG is ${DEBUG}"
    echo "MEMCACHE is ${MEMCACHE}"
    echo "WRITABLE_DIRECTORY is ${WRITABLE_DIRECTORY}"
    echo "STATIC_ROOT is ${STATIC_ROOT}"
    echo "MEDIA_ROOT is ${MEDIA_ROOT}"
    echo "LOG_DIRECTORY is ${LOG_DIRECTORY}"
    echo "DJANGO_SETTINGS_MODULE is ${DJANGO_SETTINGS_MODULE}"
}


echo "HOME is ${HOME}"
echo "WHOAMI is `whoami`"

defaults
django_defaults
wait_for_services

# prepare a tarball of build
if [ "$1" = 'tarball' ]; then
    echo "[Run] Preparing a tarball of build"
    configure_base_href

    DEPS="/env /app/uwsgi /app/docker-entrypoint.sh /app/yabi"
    cd /data
    exec tar -cpvzf yabi-${GIT_TAG}.tar.gz ${DEPS}
fi

# celery entrypoint
if [ "$1" = 'celery' ]; then
    echo "[Run] Starting celery"

    celery_defaults

    if [ "$2" = 'restart' ]; then
        python /app/pool_restart.py
        exit $?
    fi

    exec celery worker ${CELERY_OPTS}
fi

# uwsgi entrypoint
if [ "$1" = 'uwsgi' ]; then
    echo "[Run] Starting uwsgi"

    : ${UWSGI_OPTS="/app/uwsgi/docker.ini"}
    echo "UWSGI_OPTS is ${UWSGI_OPTS}"

    django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-collectstatic.log
    django-admin.py migrate --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-migrate.log
    exec uwsgi --die-on-term --ini ${UWSGI_OPTS}
fi

# runserver entrypoint
if [ "$1" = 'runserver' ]; then
    echo "[Run] Starting runserver"

    celery_defaults

    : ${RUNSERVER_OPTS="runserver_plus 0.0.0.0:${RUNSERVERPORT} --settings=${DJANGO_SETTINGS_MODULE}"}
    echo "RUNSERVER_OPTS is ${RUNSERVER_OPTS}"

    django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/runserver-collectstatic.log
    django-admin.py migrate --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/runserver-migrate.log
    exec django-admin.py ${RUNSERVER_OPTS}
fi

# runtests entrypoint
if [ "$1" = 'runtests' ]; then
    echo "[Run] Starting tests"

    XUNIT_OPTS="--with-xunit --xunit-file=tests.xml"
    NOSETESTS="nosetests -v --logging-clear-handlers --with-setup-django ${XUNIT_OPTS}"
    IGNORES="-a !external_service"

    # Setting TEST_CASES in docker-compose file allows you to choose tests
    : ${TEST_CASES="/app/tests /app/yabi/yabi"}

    echo ${NOSETESTS} ${IGNORES} ${TEST_CASES}
    exec ${NOSETESTS} ${IGNORES} ${TEST_CASES}
fi

# lettuce entrypoint
if [ "$1" = 'lettuce' ]; then
    echo "[Run] Starting lettuce"

    echo "YABIURL is ${YABIURL}"
    exec django-admin.py run_lettuce --with-xunit --xunit-file=/data/tests.xml
fi

echo "[RUN]: Builtin command not provided [lettuce|runtests|runserver|celery|uwsgi]"
echo "[RUN]: $@"

exec "$@"
