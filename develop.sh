#!/bin/sh
#
# Script to control Yabi in dev and test
#

TOPDIR=$(cd `dirname $0`; pwd)

# break on error
set -e

ACTION="$1"

PROJECT_NAME='yabi'
VIRTUALENV="${TOPDIR}/virt_${PROJECT_NAME}"
AWS_STAGING_INSTANCE='ccg_syd_nginx_staging'
AWS_RPM_INSTANCE='aws_syd_yabi_staging'


usage() {
    echo ""
    echo "Usage ./develop.sh (start|start_full|runtests|selenium)"
    echo "Usage ./develop.sh (pythonlint|jslint)"
    echo "Usage ./develop.sh (ci_docker_staging|docker_staging_selenium|ci_rpm_staging|docker_rpm_staging_selenium)"
    echo "Usage ./develop.sh (dockerbuild_unstable)"
    echo "Usage ./develop.sh (rpmbuild|rpm_publish)"
    echo ""
}


# ssh setup, make sure our ccg commands can run in an automated environment
ci_ssh_agent() {
    ssh-agent > /tmp/agent.env.sh
    . /tmp/agent.env.sh
    ssh-add ~/.ssh/ccg-syd-staging-2014.pem
}


start() {
    mkdir -p data/dev
    chmod o+rwx data/dev

    make_virtualenv

    figfile="fig.yml"
    if [ "$1" = "full" ]; then
      figfile="fig-full.yml"
    fi
    docker-compose --project-name yabi -f $figfile up
}

start_full() {
    start full
}


# build RPMs
rpmbuild() {
    mkdir -p data/rpmbuild
    chmod o+rwx data/rpmbuild

    make_virtualenv

    docker-compose --project-name yabi -f fig-rpmbuild.yml up
}


dockerbuild_unstable() {
    cd docker/unstable
    docker build -t muccg/yabi:unstable .
    cd ../../
}


runtests() {
    mkdir -p data/tests
    chmod o+rwx data/tests

    make_virtualenv

    # clean up containers from past runs
    ( docker-compose --project-name yabi -f fig-test.yml rm --force || exit 0 )
    docker-compose --project-name yabi -f fig-test.yml build --no-cache
    docker-compose --project-name yabi -f fig-test.yml up
}


# publish rpms to testing repo
rpm_publish() {
    time ccg publish_testing_rpm:data/rpmbuild/RPMS/x86_64/yabi*.rpm,release=6
}


# build a docker image and start stack on staging using docker-compose
ci_docker_staging() {
    ccg ${AWS_STAGING_INSTANCE} drun:'mkdir -p yabi/docker/unstable'
    ccg ${AWS_STAGING_INSTANCE} drun:'mkdir -p yabi/data'
    ccg ${AWS_STAGING_INSTANCE} drun:'chmod o+w yabi/data'
    ccg ${AWS_STAGING_INSTANCE} putfile:fig-staging.yml,yabi/fig-staging.yml
    ccg ${AWS_STAGING_INSTANCE} putfile:docker/unstable/Dockerfile,yabi/docker/unstable/Dockerfile

    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml stop'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml kill'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml rm --force -v'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml build --no-cache webstaging'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml up -d'
    ccg ${AWS_STAGING_INSTANCE} drun:'docker-clean || true'
}


# puppet up staging which will install the latest rpm
ci_rpm_staging() {
    ccg ${AWS_RPM_INSTANCE} boot
    ccg ${AWS_RPM_INSTANCE} puppet
    ccg ${AWS_RPM_INSTANCE} shutdown:120
}


selenium() {
    mkdir -p data/selenium
    chmod o+rwx data/selenium

    make_virtualenv

    ( docker-compose --project-name yabi -f fig-selenium.yml rm --force || exit 0 )
    docker-compose --project-name yabi -f fig-selenium.yml build
    docker-compose --project-name yabi -f fig-selenium.yml up
}


docker_staging_selenium() {
    mkdir -p data/selenium
    chmod o+rwx data/selenium

    make_virtualenv

    ( docker-compose --project-name yabi -f fig-staging-selenium.yml rm --force || exit 0 )
    docker-compose --project-name yabi -f fig-staging-selenium.yml build
    docker-compose --project-name yabi -f fig-staging-selenium.yml up
}


docker_rpm_staging_selenium() {
    mkdir -p data/selenium
    chmod o+rwx data/selenium

    make_virtualenv

    ( docker-compose --project-name yabi -f fig-staging-rpm-selenium.yml rm --force || exit 0 )
    docker-compose --project-name yabi -f fig-staging-rpm-selenium.yml build
    docker-compose --project-name yabi -f fig-staging-rpm-selenium.yml up
}


# lint using flake8
pythonlint() {
    make_virtualenv
    pip install 'flake8>=2.0,<2.1'
    flake8 yabi/yabi yabish/yabishell --count
}


# lint js, assumes closure compiler
jslint() {
    make_virtualenv
    pip install 'closure-linter==2.3.13'
    JSFILES="yabi/yabi/yabifeapp/static/javascript/*.js yabi/yabi/yabifeapp/static/javascript/account/*.js"
    for JS in $JSFILES
    do
        gjslint --disable 0131 --max_line_length 100 --nojsdoc $JS
    done
}


make_virtualenv() {
    # check requirements
    which virtualenv > /dev/null
    if [ ! -e ${VIRTUALENV} ]; then
        virtualenv ${VIRTUALENV}
    fi
    . ${VIRTUALENV}/bin/activate
    pip install docker-compose
}


case $ACTION in
pythonlint)
    pythonlint
    ;;
jslint)
    jslint
    ;;
start)
    start
    ;;
start_full)
    start_full
    ;;
rpmbuild)
    rpmbuild
    ;;
dockerbuild_unstable)
    dockerbuild_unstable
    ;;
rpm_publish)
    ci_ssh_agent
    rpm_publish
    ;;
runtests)
    runtests
    ;;
ci_docker_staging)
    ci_ssh_agent
    ci_docker_staging
    ;;
ci_rpm_staging)
    ci_ssh_agent
    ci_rpm_staging
    ;;
docker_staging_selenium)
    docker_staging_selenium
    ;;
docker_rpm_staging_selenium)
    docker_rpm_staging_selenium
    ;;
selenium)
    selenium
    ;;
*)
    usage
    ;;
esac
