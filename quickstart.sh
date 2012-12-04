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
    kill `cat yabibe/yabibe-quickstart.pid` && rm yabibe/yabibe-quickstart.pid

    # delay to allow file handles to free
    sleep 3

    exit 0
fi

# break on error
set -e

# check requirements
which virtualenv >/dev/null

export PYTHONPATH=`pwd`

# additional URLs to search for eggs during install
EASY_INSTALL="-f https://s3-ap-southeast-2.amazonaws.com/http-syd/python/centos/6/noarch/index.html"

# boostrap yabiadmin
echo "setting up yabiadmin..."
pushd yabiadmin
virtualenv vp
echo vp/bin/easy_install $EASY_INSTALL yabiadmin==0.2
vp/bin/easy_install $EASY_INSTALL yabiadmin==0.2
popd

# boostrap yabibe
echo "setting up yabibe..."
pushd yabibe
virtualenv vp
echo vp/bin/easy_install $EASY_INSTALL yabibe==0.2
vp/bin/easy_install $EASY_INSTALL yabibe==0.2
popd

#
# gunicorn serving up yabiadmin
#
pushd yabiadmin

export DJANGO_SETTINGS_MODULE="yabiadmin.quickstartsettings"
vp/bin/django-admin.py syncdb --noinput
vp/bin/django-admin.py migrate

# collect static
vp/bin/django-admin.py collectstatic --noinput 1> collectstatic.log

# use gunicorn to fire up yabiadmin
vp/bin/pip install gunicorn

# launch yabiadmin via gunicorn
vp/bin/gunicorn_django -b 0.0.0.0:8000 --log-file=gunicorn.log --daemon yabiadmin.quickstartsettings -t 300 -w 5

# 
# celeryd
#
CELERY_CONFIG_MODULE="quickstartsettings"
CELERYD_CHDIR=`pwd`
CELERYD_OPTS="--logfile=celeryd-quickstart.log --pidfile=celeryd-quickstart.pid"
CELERY_LOADER="django"
PYTHONPATH=$CELERYD_CHDIR
DJANGO_SETTINGS_MODULE="quickstartsettings"
DJANGO_PROJECT_DIR="$CELERYD_CHDIR"
PROJECT_DIRECTORY="$CELERYD_CHDIR"

export CELERY_CONFIG_MODULE DJANGO_SETTINGS_MODULE DJANGO_PROJECT_DIR CELERY_LOADER CELERY_CHDIR PYTHONPATH PROJECT_DIRECTORY CELERYD_CHDIR
# export

# run celeryd
vp/bin/celeryd $CELERYD_OPTS 1>/dev/null 2>/dev/null &

popd

#
# yabibe 
#
pushd yabibe

# start yabibe server in the background
vp/bin/yabibe -l yabibe-quickstart.log --pidfile=yabibe-quickstart.pid

popd


