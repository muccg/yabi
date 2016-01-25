#!/bin/sh
#
# Script to control Yabi in dev and test
#

TOPDIR=$(cd `dirname $0`; pwd)

# break on error
set -e

ACTION="$1"

DATE=`date +%Y.%m.%d`
PROJECT_NAME='yabi'
VIRTUALENV="${TOPDIR}/virt_${PROJECT_NAME}"
AWS_STAGING_INSTANCE='ccg_syd_nginx_staging'
AWS_RPM_INSTANCE='aws_syd_yabi_staging'

: ${DOCKER_BUILD_OPTIONS:="--pull=true"}
: ${DOCKER_COMPOSE_BUILD_OPTIONS:="--pull"}

usage() {
    echo ""
    echo "Usage ./develop.sh (start|start_full|runtests|lettuce)"
    echo "Usage ./develop.sh (build)"
    echo "Usage ./develop.sh (buildtarball|starttarball)"
    echo "Usage ./develop.sh (pythonlint|jslint)"
    echo "Usage ./develop.sh (ci_docker_staging|docker_staging_lettuce|ci_rpm_staging|docker_rpm_staging_lettuce)"
    echo "Usage ./develop.sh (dockerbuild)"
    echo "Usage ./develop.sh (rpmbuild|rpm_publish)"
    echo ""
    exit 1
}


# ssh setup, make sure our ccg commands can run in an automated environment
ci_ssh_agent() {
    ssh-agent > /tmp/agent.env.sh
    . /tmp/agent.env.sh
    ssh-add ${CI_SSH_KEY}
}


buildtarball() {
    mkdir -p build
    chmod o+rwx build

    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-tarball.yml build ${DOCKER_COMPOSE_BUILD_OPTIONS}
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-tarball.yml up
    set +x
}


starttarball() {
    mkdir -p data/build
    chmod o+rwx data/build

    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-tarball-release.yml build ${DOCKER_COMPOSE_BUILD_OPTIONS}
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-tarball-release.yml up
    set +x
}




start() {
    mkdir -p data/dev
    chmod o+rwx data/dev

    make_virtualenv

    if [ "full" = "$1" ]; then
        set -x
        docker-compose --project-name ${PROJECT_NAME} -f docker-compose-full.yml build ${DOCKER_COMPOSE_BUILD_OPTIONS}
        docker-compose --project-name ${PROJECT_NAME} -f docker-compose-full.yml up
        set +x
    else
        set -x
        docker-compose --project-name ${PROJECT_NAME} up
        set +x
    fi

}

start_full() {
    start full
}

build() {
    make_virtualenv

    set -x
    docker-compose --project-name ${PROJECT_NAME} build ${DOCKER_COMPOSE_BUILD_OPTIONS}
    set +x
}

# build RPMs
rpmbuild() {
    mkdir -p data/rpmbuild
    chmod o+rwx data/rpmbuild

    make_virtualenv

    set -x
    docker-compose ${DOCKER_COMPOSE_OPTIONS} --project-name ${PROJECT_NAME} -f docker-compose-rpmbuild.yml up
    set +x

}


ci_docker_login() {
    if [ -n "$bamboo_DOCKER_USERNAME" ] && [ -n "$bamboo_DOCKER_EMAIL" ] && [ -n "$bamboo_DOCKER_PASSWORD" ]; then
        docker login  -e "${bamboo_DOCKER_EMAIL}" -u ${bamboo_DOCKER_USERNAME} --password="${bamboo_DOCKER_PASSWORD}"
    else
        echo "Docker vars not set, not logging in to docker registry"
    fi
}


# docker build and push in CI
dockerbuild() {
    make_virtualenv

    image="muccg/${PROJECT_NAME}"
    gittag=`git describe --abbrev=0 --tags 2> /dev/null`
    gitbranch=`git rev-parse --abbrev-ref HEAD 2> /dev/null`

    # only use tags when on master (release) branch
    if [ $gitbranch != "master" ]; then
        echo "Ignoring tags, not on master branch"
        gittag=$gitbranch
    fi

    # if no git tag, then use branch name
    if [ -z ${gittag+x} ]; then
        echo "No git tag set, using branch name"
        gittag=$gitbranch
    fi

    # create .version file for invalidating cache in Dockerfile
    # we hit remote as the Dockerfile clones remote
    git ls-remote https://github.com/muccg/yabi.git ${gittag} > .version
    cat .version

    echo "############################################################# ${PROJECT_NAME} ${gittag}"

    # attempt to warm up docker cache
    docker pull ${image}:${gittag} || true

    for tag in "${image}:${gittag}" "${image}:${gittag}-${DATE}"; do
        echo "############################################################# ${PROJECT_NAME} ${tag}"
        set -x
        docker build ${DOCKER_BUILD_OPTIONS} --build-arg GIT_TAG=${gittag} -t ${tag} -f Dockerfile-release .
        docker push ${tag}
        set +x
    done

    rm -f .version || true
}


_test_stack_up() {
    mkdir -p data/tests
    chmod o+rwx data/tests

    make_virtualenv

    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml rm --force
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml build ${DOCKER_COMPOSE_BUILD_OPTIONS}
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml up -d
    set +x
}


_test_stack_down() {
    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml stop
    set +x
}


runtests() {
    _test_stack_up

    set +e
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-unittests.yml rm --force
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-unittests.yml build ${DOCKER_COMPOSE_BUILD_OPTIONS}
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-unittests.yml up
    rval=$?
    set -e

    _test_stack_down

    return $rval
}


# publish rpms to testing repo
rpm_publish() {
    time ccg publish_testing_rpm:data/rpmbuild/RPMS/x86_64/yabi*.rpm,release=6
}


# build a docker image and start stack on staging using docker-compose
ci_docker_staging() {
    ssh ubuntu@staging.ccgapps.com.au << EOF
      mkdir -p ${PROJECT_NAME}/data
      chmod o+w ${PROJECT_NAME}/data
EOF

    scp docker-compose-*.yml ubuntu@staging.ccgapps.com.au:${PROJECT_NAME}/

    # TODO This doesn't actually do a whole lot, some tests should be run against the staging stack
    ssh ubuntu@staging.ccgapps.com.au << EOF
      cd ${PROJECT_NAME}
      docker-compose -f docker-compose-staging.yml stop
      docker-compose -f docker-compose-staging.yml kill
      docker-compose -f docker-compose-staging.yml rm --force -v
      docker-compose -f docker-compose-staging.yml up -d
EOF
}


# puppet up staging which will install the latest rpm
ci_rpm_staging() {
    ccg ${AWS_RPM_INSTANCE} boot
    ccg ${AWS_RPM_INSTANCE} puppet
    ccg ${AWS_RPM_INSTANCE} shutdown:120
}


_selenium_stack_up() {
    mkdir -p data/selenium
    chmod o+rwx data/selenium

    make_virtualenv

    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-selenium.yml up -d
    set +x
}


_selenium_stack_down() {
    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-selenium.yml stop
    set +x
}


lettuce() {
    _selenium_stack_up
    _test_stack_up

    set -x
    set +e
    ( docker-compose --project-name ${PROJECT_NAME} -f docker-compose-lettuce.yml rm --force || exit 0 )
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-lettuce.yml build
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-lettuce.yml up
    rval=$?
    set -e
    set +x

    _test_stack_down
    _selenium_stack_down

    exit $rval
}


docker_staging_lettuce() {
    _selenium_stack_up

    set -x
    set +e
    ( docker-compose --project-name ${PROJECT_NAME} -f docker-compose-staging-lettuce.yml rm --force || exit 0 )
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-staging-lettuce.yml build
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-staging-lettuce.yml up
    rval=$?
    set -e
    set +x

    _selenium_stack_down

    exit $rval
}


docker_rpm_staging_lettuce() {
    _selenium_stack_up

    set -x
    set +e
    ( docker-compose --project-name ${PROJECT_NAME} -f docker-compose-staging-rpm-lettuce.yml rm --force || exit 0 )
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-staging-rpm-lettuce.yml build
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-staging-rpm-lettuce.yml up
    rval=$?
    set -e
    set +x

    _selenium_stack_down

    exit $rval
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
    if ! which virtualenv > /dev/null; then
      echo "virtualenv is required by develop.sh but it isn't installed."
      exit 1
    fi
    if [ ! -e ${VIRTUALENV} ]; then
        virtualenv ${VIRTUALENV}
    fi
    . ${VIRTUALENV}/bin/activate

    if ! which docker-compose > /dev/null; then
      pip install 'docker-compose<1.6' --upgrade || true
    fi
    docker-compose --version
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
build)
    build
    ;;
buildtarball)
    buildtarball
    ;;
starttarball)
    starttarball
    ;;
rpmbuild)
    rpmbuild
    ;;
dockerbuild)
    ci_docker_login
    dockerbuild
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
docker_staging_lettuce)
    docker_staging_lettuce
    ;;
docker_rpm_staging_lettuce)
    docker_rpm_staging_lettuce
    ;;
lettuce)
    lettuce
    ;;
*)
    usage
    ;;
esac
