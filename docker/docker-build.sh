#!/bin/bash

function defaults {
    : ${BUILD_HOST:=`netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'`}
    : ${DEVPI_HOST:="${BUILD_HOST}"}
    : ${DEVPI_PORT:="3141"}

    PIP_OPTS="--process-dependency-links"
    if [ exec 6<>/dev/tcp/${DEVPI_HOST}/${DEVPI_PORT} ] ; then
        PIP_OPTS="-i http://${DEVPI_HOST}:${DEVPI_PORT}/root/pypi/ --process-dependency-links"
    fi

    echo "BUILD_HOST is ${BUILD_HOST}"
    echo "DEVPI_HOST is ${DEVPI_HOST}"
    echo "DEVPI_PORT is ${DEVPI_PORT}"
    echo "PIP_OPTS is ${PIP_OPTS}"
    echo "APP_RELEASE is ${APP_RELEASE}"
}

defaults

# install yabi
cd /app/yabiadmin
pip install ${PIP_OPTS} .

# install yabi shell
cd /app/yabish
pip install ${PIP_OPTS} .

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
