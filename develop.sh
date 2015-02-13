#!/bin/bash
#
# Script to control Yabi in dev and test
#

TOPDIR=$(cd `dirname $0`; pwd)

# break on error
set -e

ACTION="$1"

# yabiadmin is legacy, but occurs in many many places in code/config
PROJECT_NAME='yabiadmin'
AWS_STAGING_INSTANCE='ccg_syd_nginx_staging'
TESTING_MODULES="pyvirtualdisplay nose selenium lettuce lettuce_webdriver"
PIP5_OPTS="--process-dependency-links"
VIRTUALENV="${TOPDIR}/virt_${PROJECT_NAME}"


usage() {
    echo ""
    echo "Usage ./develop.sh (pythonlint|jslint|rpmbuild|rpm_publish|ci_runtests|ci_staging)"
    echo ""
}


# ssh setup, make sure our ccg commands can run in an automated environment
ci_ssh_agent() {
    ssh-agent > /tmp/agent.env.sh
    . /tmp/agent.env.sh
    ssh-add ~/.ssh/ccg-syd-staging-2014.pem
}


# build RPMs
rpmbuild() {
    mkdir -p data/rpmbuild
    chmod o+rwx data/rpmbuild

    make_virtualenv
    . ${VIRTUALENV}/bin/activate
    pip install fig

    fig --project-name yabi -f fig-rpmbuild.yml up
}


# run tests in our ci environment
ci_runtests() {
    mkdir -p data/tmp
    chmod o+rwx data
    chmod o+rwx data/tmp

    make_virtualenv
    . ${VIRTUALENV}/bin/activate
    pip install fig

    docker-kill-all
    docker-clean

    fig --project-name yabi build web
    fig --project-name yabi -f fig-test.yml up
}


# publish rpms to testing repo
rpm_publish() {
    time ccg publish_testing_rpm:data/rpmbuild/RPMS/x86_64/yabi*.rpm,release=6
}


# puppet up staging which will install the latest rpm
ci_staging() {
    ccg ${AWS_STAGING_INSTANCE} drun:'mkdir -p yabi/docker/unstable'
    ccg ${AWS_STAGING_INSTANCE} drun:'mkdir -p yabi/data'
    ccg ${AWS_STAGING_INSTANCE} drun:'chown o+w yabi/data'
    ccg ${AWS_STAGING_INSTANCE} putfile:fig-staging.yml,yabi/fig-staging.yml
    ccg ${AWS_STAGING_INSTANCE} putfile:docker/unstable/Dockerfile,yabi/docker/unstable/Dockerfile

    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml kill'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml rm --force -v'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml build webstaging'
    ccg ${AWS_STAGING_INSTANCE} drun:'cd yabi && fig -f fig-staging.yml up -d'
    ccg ${AWS_STAGING_INSTANCE} drun:'docker-untagged'
}


# lint using flake8
pythonlint() {
    make_virtualenv
    ${VIRTUALENV}/bin/pip install 'flake8>=2.0,<2.1'
    ${VIRTUALENV}/bin/flake8 yabiadmin/yabiadmin yabish/yabishell --count
}


# lint js, assumes closure compiler
jslint() {
    make_virtualenv
    ${VIRTUALENV}/bin/pip install 'closure-linter==2.3.13'
    JSFILES="yabiadmin/yabiadmin/yabifeapp/static/javascript/*.js yabiadmin/yabiadmin/yabifeapp/static/javascript/account/*.js"
    for JS in $JSFILES
    do
        ${VIRTUALENV}/bin/gjslint --disable 0131 --max_line_length 100 --nojsdoc $JS
    done
}


make_virtualenv() {
    # check requirements
    which virtualenv > /dev/null
    virtualenv ${VIRTUALENV}
}


case $ACTION in
pythonlint)
    pythonlint
    ;;
jslint)
    jslint
    ;;
rpmbuild)
    rpmbuild
    ;;
rpm_publish)
    ci_ssh_agent
    rpm_publish
    ;;
ci_runtests)
    ci_runtests
    ;;
ci_staging)
    ci_ssh_agent
    ci_staging
    ;;
ci_staging_tests)
    ci_ssh_agent
    ci_staging_tests
    ;;
ci_staging_selenium)
    ci_ssh_agent
    ci_staging_selenium
    ;;
*)
    usage
    ;;
esac
