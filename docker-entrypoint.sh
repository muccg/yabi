#!/bin/bash
set -x

# start up a celery instance
if [ "$1" = 'celery' ]; then
    echo "[Run] Starting celery"

    chown -R celery:celery /app

    # TODO expose these as env vars to allow them to be set

    # Environment taken from develop.sh
    DJANGO_SETTINGS_MODULE="yabiadmin.settings"
    CELERY_CONFIG_MODULE="settings"
    #CELERYD_OPTS="-A yabiadmin.backend.celerytasks -E --loglevel=DEBUG -Ofair -b amqp://guest:**@mq:5672//"
    #CELERYD_OPTS="-A yabiadmin.backend.celerytasks -E --loglevel=DEBUG -Ofair -b amqp://guest@mq:5672//"
    CELERYD_OPTS="-A yabiadmin.backend.celerytasks -E --loglevel=DEBUG -Ofair -b amqp://admin:admin@mq:5672//"
    DJANGO_PROJECT_DIR="${CELERYD_CHDIR}"
    PROJECT_DIRECTORY="${CELERYD_CHDIR}"

    export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PROJECT_DIRECTORY CELERYD_CHDIR

    # TODO once again these need to be env vars, hard coded while we get it running

    DEPLOYMENT=dev
    PRODUCTION=0
    DEBUG=1
    DBSERVER=db
    MEMCACHE=cache:11211
    
    export DEPLOYMENT PRODUCTION DEBUG DBSERVER MEMCACHE

    gosu celery /usr/local/bin/celery worker ${CELERYD_OPTS}
    exit $?
fi

# start up a uwsgi instance
if [ "$1" = 'uwsgi' ]; then
    echo "[Run] Starting uwsgi"
    UWSGI_OPTS="/app/uwsgi/docker.ini"
    /usr/local/bin/uwsgi ${UWSGI_OPTS}
    exit $?
fi

echo "FATAL: Command not provided [celery|uwsgi]"
