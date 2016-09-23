#!/bin/bash

trap exit SIGHUP SIGINT SIGTERM
env | grep -iv PASS | sort

# prepare a tarball of build
if [ "$1" = 'releasetarball' ]; then
    echo "[Run] Preparing a release tarball"

    set -e
    cd /app
    rm -rf /app/*
    echo $GIT_TAG
    set -x
    git clone --depth=1 --branch=${GIT_TAG} ${PROJECT_SOURCE} .
    git ls-remote ${PROJECT_SOURCE} ${GIT_TAG} > .version

    # Note: Environment vars are used to control the behaviour of pip (use local devpi for instance)
    pip install ${PIP_OPTS} --upgrade -r yabi/runtime-requirements.txt
    pip install -e ${PROJECT_NAME}
    pip install ${PIP_OPTS} --upgrade -r yabish/requirements.txt
    pip install -e yabish
    set +x

    # create release tarball
    DEPS="/env /app/uwsgi /app/docker-entrypoint.sh /app/${PROJECT_NAME} /app/yabish"
    cd /data
    exec tar -cpzf ${PROJECT_NAME}-${GIT_TAG}.tar.gz ${DEPS}
fi

echo "[RUN]: Builtin command not provided [releasetarball]"
echo "[RUN]: $@"

exec "$@"
