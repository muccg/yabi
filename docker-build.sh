#!/bin/bash

BUILD_HOST=`netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'`

echo "BUILD_HOST is ${BUILD_HOST}"
echo "APP_RELEASE is ${APP_RELEASE}"

# TODO check to see if CONTAINER_HOST has devpi or squid running

# install yabi
cd /app/yabiadmin
pip install --process-dependency-links .

# install yabi shell
cd /app/yabish
pip install --process-dependency-links .

# save docker-entry-point.sh prior to cleanup
cp /app/docker-entrypoint.sh /
chmod +x /docker-entrypoint.sh

# save uwsgi config prior to cleanup
mv /app/uwsgi /

# cleanup
rm -rf /app
mkdir /app

# restore uwsgi config
mv /uwsgi /app/
