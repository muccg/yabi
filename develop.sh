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
AWS_STAGING_INSTANCE='aws_syd_yabi_staging'
STAGING_PIP="/usr/local/webapps/yabiadmin/bin/pip2.7"
TESTING_MODULES="pyvirtualdisplay nose selenium lettuce lettuce_webdriver"
PIP5_OPTS="--process-dependency-links"
VIRTUALENV="${TOPDIR}/virt_${PROJECT_NAME}"


usage() {
    echo ""
    echo "Usage ./develop.sh (pythonlint|jslint|rpmbuild|rpm_publish|ci_runtests|ci_staging|ci_staging_tests|ci_staging_selenium)"
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
    mkdir -p data
    chmod o+rwx data

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
    ccg ${AWS_STAGING_INSTANCE} boot
    ccg ${AWS_STAGING_INSTANCE} puppet
    ccg ${AWS_STAGING_INSTANCE} shutdown:120
}


# run tests on staging
ci_staging_tests() {
    # Try running syncdb -- if setup is wrong this won't work
    ccg ${AWS_STAGING_INSTANCE} dsudo:"yabiadmin syncdb --noinput"

    # Get the login page -- will find major config problems with the rpm
    STAGING_URL="https://localhost/yabi/"
    ccg ${AWS_STAGING_INSTANCE} drun:"curl --insecure -f -o /dev/null -D /dev/stdout ${STAGING_URL}"
}


# staging selenium test
ci_staging_selenium() {
    ccg ${AWS_STAGING_INSTANCE} dsudo:"${STAGING_PIP} install ${TESTING_MODULES}"
    ccg ${AWS_STAGING_INSTANCE} dsudo:'dbus-uuidgen --ensure'
    ccg ${AWS_STAGING_INSTANCE} dsudo:'chown apache:apache /var/www'
    ccg ${AWS_STAGING_INSTANCE} dsudo:'service httpd restart'
    ccg ${AWS_STAGING_INSTANCE} drunbg:"Xvfb -ac \:0"
    ccg ${AWS_STAGING_INSTANCE} dsudo:'mkdir -p lettuce && chmod o+w lettuce'
    ccg ${AWS_STAGING_INSTANCE} dsudo:"cd lettuce && DISPLAY\=\:0 YABIURL\=https\://localhost/yabi/ yabiadmin run_lettuce --with-xunit --xunit-file\=/tmp/tests.xml --app-name\=yabiadmin --traceback || true"
    ccg ${AWS_STAGING_INSTANCE} getfile:/tmp/tests.xml,./
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
