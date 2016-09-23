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
    : ${DOCKER_ROUTE:=$(/sbin/ip route|awk '/default/ { print $3 }')}
    : ${RUNSERVER:="web"}
    : ${RUNSERVERPORT:="8000"}
    : ${CACHESERVER:="cache"}
    : ${CACHEPORT:="11211"}
    : ${MEMCACHE:="${CACHESERVER}:${CACHEPORT}"}
    : ${SSHSERVER:="ssh"}
    : ${SSHPORT:="22"}
    : ${S3SERVER:="s3"}
    : ${S3PORT:="4569"}
    : ${KERBEROSSERVER:="krb5"}
    : ${KERBEROSPORT:="88"}
    : ${LDAPSERVER:="ldap"}
    : ${LDAPPORT:="389"}
    : ${YABIURL:="http://$DOCKER_ROUTE:$RUNSERVERPORT/"}

    : ${DBUSER:="webapp"}
    : ${DBNAME:="${DBUSER}"}
    : ${DBPASS:="${DBUSER}"}

    export DBSERVER DBPORT DBUSER DBNAME DBPASS MEMCACHE DOCKER_ROUTE 
    export YABIURL
}


function celery_defaults {
    : ${CELERY_CHDIR:=`pwd`}
    # Nodes:  yabi-node yabi-node-fsops yabi-node-provisioning"}
    # Queues: celery    file_operations provisioning"}
    : ${CELERY_NODE:="yabi-node"}
    : ${CELERY_QUEUES:="celery,file_operations,provisioning"}

    : ${CELERY_CONFIG_MODULE:="settings"}
    : ${CELERY_BROKER:="amqp://guest:guest@${QUEUESERVER}:${QUEUEPORT}//"}
    : ${CELERY_APP:="yabi.backend.celerytasks"}
    : ${CELERY_LOG_FILE:="${CELERY_CHDIR}/${CELERY_NODE}.log"}
    : ${CELERY_LOGLEVEL:="DEBUG"}
    : ${CELERY_OPTIMIZATION:="fair"}
    : ${CELERY_CONCURRENCY:="4"}
    if [[ -z "$CELERY_AUTORELOAD" ]] ; then
        CELERY_AUTORELOAD=""
    else
        CELERY_AUTORELOAD="--autoreload"
    fi
    : ${DJANGO_PROJECT_DIR:="${CELERY_CHDIR}"}
    : ${PROJECT_DIRECTORY:="${CELERY_CHDIR}"}

    export CELERY_CHDIR CELERY_NODE CELERY_QUEUES CELERY_CONFIG_MODULE CELERY_BROKER CELERY_APP
    export CELERY_LOGLEVEL CELERY_LOG_FILE
    export CELERY_OPTIMIZATION CELERY_CONCURRENCY CELERY_AUTORELOAD
    export DJANGO_PROJECT_DIR PROJECT_DIRECTORY
}


function _django_check_deploy {
    echo "running check --deploy"
    django-admin.py check --deploy --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-check.log
}


function _django_migrate {
    echo "running migrate"
    django-admin.py migrate --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-migrate.log
}


function _django_collectstatic {
    echo "running collectstatic"
    django-admin.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} 2>&1 | tee /data/uwsgi-collectstatic.log
}


trap exit SIGHUP SIGINT SIGTERM
defaults
env | grep -iv PASS | sort
wait_for_services

# celery entrypoint
if [ "$1" = 'celery' ]; then
    echo "[Run] Starting celery"

    celery_defaults

    if [ "$2" = 'restart' ]; then
        python /app/pool_restart.py
        exit $?
    fi

    exec celery worker \
         --app=${CELERY_APP} \
         --broker ${CELERY_BROKER} \
         --events \
         --concurrency=${CELERY_CONCURRENCY} \
         --executable=celery \
         --hostname ${CELERY_NODE}@${HOSTNAME} \
         --loglevel=${CELERY_LOGLEVEL} \
         --workdir=${CELERY_CHDIR} \
         ${CELERY_AUTORELOAD} \
         --logfile=/dev/stdout \
         -O${CELERY_OPTIMIZATION} \
         --queues ${CELERY_QUEUES} 2>&1 | tee ${CELERY_LOG_FILE}
fi

# uwsgi entrypoint
if [ "$1" = 'uwsgi' ]; then
    echo "[Run] Starting uwsgi"

    : ${UWSGI_OPTS="/app/uwsgi/docker.ini"}
    echo "UWSGI_OPTS is ${UWSGI_OPTS}"

    _django_collectstatic
    _django_migrate
    _django_check_deploy

    exec uwsgi --die-on-term --ini ${UWSGI_OPTS}
fi

# runserver entrypoint
if [ "$1" = 'runserver' ]; then
    echo "[Run] Starting runserver"

    celery_defaults

    : ${RUNSERVER_OPTS="runserver_plus 0.0.0.0:${RUNSERVERPORT} --settings=${DJANGO_SETTINGS_MODULE}"}
    echo "RUNSERVER_OPTS is ${RUNSERVER_OPTS}"

    _django_collectstatic
    _django_migrate
    
    echo "running runserver ${RUNSERVER_OPTS}"
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
    exec django-admin.py run_lettuce --with-xunit --xunit-file=/data/tests.xml $@
fi

echo "[RUN]: Builtin command not provided [lettuce|runtests|runserver|celery|uwsgi]"
echo "[RUN]: $@"

exec "$@"
