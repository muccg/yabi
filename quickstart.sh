#!/bin/bash

#
# Quickstart script to setup yabi with a simple sqlite database
# and the relevant other pieces
#

# handle the stop instruction to tear down the quickstart environment
if [ "x$1" == "xstop" ]
then
    echo "stopping quickstart servers"
    killall gunicorn_django
    killall celeryd
    exit 0
fi

# break on error
set -e

# check requirements
which virtualenv >/dev/null

export PYTHONPATH=`pwd`

# additional URLs to search for eggs during install
EASY_INSTALL="-f https://s3-ap-southeast-1.amazonaws.com/http-sing/python/centos/6/noarch/index.html"

# boostrap vp's
for DIR in yabibe yabiadmin
do
    echo "setting up $DIR..."
    pushd $DIR
    virtualenv vp
    echo vp/bin/easy_install $EASY_INSTALL .
    vp/bin/easy_install $EASY_INSTALL .
    popd
done

# migrate sqlitedb
pushd yabiadmin
export DJANGO_SETTINGS_MODULE="quickstartsettings"
vp/bin/python vp/lib/python2.6/site-packages/yabiadmin-*.egg/yabiadmin/manage.py syncdb --noinput
vp/bin/python vp/lib/python2.6/site-packages/yabiadmin-*.egg/yabiadmin/manage.py migrate

# collect static
vp/bin/python vp/lib/python2.6/site-packages/yabiadmin-*.egg/yabiadmin/manage.py collectstatic --noinput

# use gunicorn to fire up yabiadmin
vp/bin/pip install gunicorn

# launch yabiadmin via gunicorn
vp/bin/gunicorn_django --log-file=gunicorn.log --daemon .quickstartsettings

# fire up celeryd
CELERY_CONFIG_MODULE="quickstartsettings"
CELERYD_CHDIR=`pwd`
CELERYD_OPTS="-E -B --schedule=$CELERYD_CHDIR/logs/celerybeat-schedule"
CELERYD_PID_FILE="$CELERYD_CHDIR/logs/celeryd.pid"
CELERYD_LOG_FILE="$CELERYD_CHDIR/logs/celeryd.log"
CELERYD_LOG_LEVEL="INFO"
CELERYD="python -m celery.bin.celeryd_detach"
CELERYD_USER="apache"
CELERYD_GROUP="apache"
CELERY_LOADER="django"

VIRTUALENV="$CELERYD_CHDIR/vp"
PYTHONPATH=$CELERYD_CHDIR
DJANGO_SETTINGS_MODULE="quickstartsettings"
DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
PROJECT_DIRECTORY="$CELERYD_CHDIR"

export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PYTHONPATH PROJECT_DIRECTORY CELERYD_CHDIR
export

# run celeryd
vp/bin/celeryd $CELERYD_OPTS &



