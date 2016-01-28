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

: ${DOCKER_BUILD_PULL:="--pull=true"}
: ${DOCKER_BUILD_PROXY:="--build-arg http_proxy"}
: ${DOCKER_COMPOSE_BUILD_PULL:="--pull"}
: ${DOCKER_USE_HUB:="1"}
: ${DOCKER_IMAGE:="muccg/${PROJECT_NAME}"}
: ${SET_HTTP_PROXY:="1"}


usage() {
    echo ""
    echo "Environment:"
    echo " Pull during docker build       DOCKER_BUILD_PULL           ${DOCKER_BUILD_PULL} "
    echo " Use proxy during builds        DOCKER_BUILD_PROXY          ${DOCKER_BUILD_PROXY}"
    echo " docker-compose pulls           DOCKER_COMPOSE_BUILD_PULL   ${DOCKER_COMPOSE_BUILD_PULL}"
    echo " Push/pull from docker hub      DOCKER_USE_HUB              ${DOCKER_USE_HUB}"
    echo " Release docker image           DOCKER_IMAGE                ${DOCKER_IMAGE}"
    echo " Use a http proxy               SET_HTTP_PROXY              ${SET_HTTP_PROXY}"
    echo ""
    echo "Usage:"
    echo " ./develop.sh (build|start|start_full|runtests|lettuce)"
    echo " ./develop.sh (baseimage|buildimage|devimage|releasetarball|releaseimage)"
    echo " ./develop.sh (start_release)"
    echo " ./develop.sh (pythonlint|jslint)"
    echo " ./develop.sh (ci_docker_staging|docker_staging_lettuce|ci_rpm_staging|docker_rpm_staging_lettuce)"
    echo " ./develop.sh (ci_dockerbuild)"
    echo " ./develop.sh (rpmbuild|rpm_publish)"
    echo ""
    exit 1
}


info () {
  printf "\r  [ \033[00;34mINFO\033[0m ] $1\n"
}

success () {
  printf "\r\033[2K  [ \033[00;32m OK \033[0m ] $1\n"
}


fail () {
  printf "\r\033[2K  [\033[0;31mFAIL\033[0m] $1\n"
  echo ''
  exit 1
}


_http_proxy() {
    info 'http proxy'

    if [ ${SET_HTTP_PROXY} = "1" ]; then
        local docker_route=$(ip -4 addr show docker0 | grep -Po 'inet \K[\d.]+')
        success "Docker ip $docker_route"
        http_proxy="http://${docker_route}:3128"
        success "Proxy $http_proxy"
    else
        info 'Not setting http_proxy'
    fi
}


# ssh setup for ci
_ci_ssh_agent() {
    info 'ci ssh config'

    # if no _ci_ssh_agent then bomb
    if [ -z ${_ci_ssh_agent+x} ]; then
        fail '_ci_ssh_agent not set'
        exit 1
    fi

    ssh-agent > /tmp/agent.env.sh
    . /tmp/agent.env.sh
    ssh-add ${CI_SSH_KEY}

    success 'activated ssh agent'
}


# figure out what branch/tag we are on, write out .version file
_github_revision() {
    info 'git revision'

    gittag=`git describe --abbrev=0 --tags 2> /dev/null`
    gitbranch=`git rev-parse --abbrev-ref HEAD 2> /dev/null`

    # only use tags when on master (release) branch
    if [ $gitbranch != "master" ]; then
        info 'Ignoring tags, not on master branch'
        gittag=$gitbranch
    fi

    # if no git tag, then use branch name
    if [ -z ${gittag+x} ]; then
        info 'No git tag set, using branch name'
        gittag=$gitbranch
    fi

    # create .version file for invalidating cache in Dockerfile
    # we hit remote as the Dockerfile clones remote
    git ls-remote https://github.com/muccg/${PROJECT_NAME}.git ${gittag} > .version

    success "$(cat .version)"
    success "git tag: ${gittag}"
}


create_release_image() {
    info 'create release image'
    # assumes that base image and release tarball have been created
    _docker_release_build Dockerfile-release ${DOCKER_IMAGE}
    success "$(docker images | grep ${DOCKER_IMAGE} | grep ${gittag}-${DATE} | sed 's/  */ /g')"
}


create_build_image() {
    info 'create build image'
    _github_revision

    set -x
    docker build ${DOCKER_BUILD_PROXY} --build-arg ARG_GIT_TAG=${gittag} -t muccg/${PROJECT_NAME}-build -f Dockerfile-build .
    set +x
    success "$(docker images | grep muccg/${PROJECT_NAME}-build | sed 's/  */ /g')"
}


create_base_image() {
    info 'create base image'
    set -x
    docker build ${DOCKER_BUILD_PROXY} ${DOCKER_BUILD_PULL} -t muccg/${PROJECT_NAME}-base -f Dockerfile-base .
    set +x
    success "$(docker images | grep muccg/${PROJECT_NAME}-base | sed 's/  */ /g')"
}


create_release_tarball() {
    info 'create release tarball'
    mkdir -p build
    chmod o+rwx build

    # don't use docker-compose to build as it doesn't support build args
    create_build_image

    set -x
    #docker-compose --project-name ${PROJECT_NAME} -f docker-compose-build.yml up
    local volume=$(readlink -f ./build/)
    docker run --rm -v ${volume}:/data muccg/${PROJECT_NAME}-build tarball
    set +x
    success "$(ls -lh build/*)"
}


start_release() {
    info 'start release'
    mkdir -p data/release
    chmod o+rwx data/release

    create_base_image
    create_build_image
    create_release_tarball
    create_release_image

    # Now fire up release stack
    info 'starting release using docker-compose'
    set -x
    GIT_TAG=${gittag} docker-compose --project-name ${PROJECT_NAME} -f docker-compose-release.yml rm --force
    GIT_TAG=${gittag} docker-compose --project-name ${PROJECT_NAME} -f docker-compose-release.yml up
    set +x
}


build_dev() {
    info 'build dev'
    set -x
    docker-compose --project-name ${PROJECT_NAME} build
    set +x
}


start_dev() {
    info 'start dev'
    mkdir -p data/dev
    chmod o+rwx data/dev
    set -x
    docker-compose --project-name ${PROJECT_NAME} up
    set +x
}


start_dev_full() {
    info 'start dev full'
    mkdir -p data/dev
    chmod o+rwx data/dev
    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-full.yml build
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-full.yml up
    set +x
}


# build RPMs
rpm_build() {
    info 'rpm build'
    mkdir -p data/rpmbuild
    chmod o+rwx data/rpmbuild
    set -x
    docker-compose ${DOCKER_COMPOSE_OPTIONS} --project-name ${PROJECT_NAME} -f docker-compose-rpmbuild.yml pull
    docker-compose ${DOCKER_COMPOSE_OPTIONS} --project-name ${PROJECT_NAME} -f docker-compose-rpmbuild.yml up
    set +x
    success "$(ls -lht data/rpmbuild/RPMS/x86_64/*shell* | head -1)"
    success "$(ls -lht data/rpmbuild/RPMS/x86_64/*admin* | head -1)"
}


_ci_docker_login() {
    info 'Docker login'

    if [ -z ${bamboo_DOCKER_EMAIL+x} ]; then
        fail 'bamboo_DOCKER_EMAIL not set'
    fi
    if [ -z ${bamboo_DOCKER_USERNAME+x} ]; then
        fail 'bamboo_DOCKER_USERNAME not set'
    fi
    if [ -z ${bamboo_DOCKER_PASSWORD+x} ]; then
        fail 'bamboo_DOCKER_PASSWORD not set'
    fi

    docker login  -e "${bamboo_DOCKER_EMAIL}" -u ${bamboo_DOCKER_USERNAME} --password="${bamboo_DOCKER_PASSWORD}"
    success "Docker login"
}


_docker_release_build() {
    info 'docker release build'

    local dockerfile='Dockerfile-release'
    local dockerimage=${DOCKER_IMAGE}

    _github_revision

    # attempt to warm up docker cache
    if [ ${DOCKER_USE_HUB} = "1" ]; then
        docker pull ${dockerimage}:${gittag} || true
    fi

    for tag in "${dockerimage}:${gittag}" "${dockerimage}:${gittag}-${DATE}"; do
        info "Building ${PROJECT_NAME} ${tag}"
        set -x
        docker build ${DOCKER_BUILD_PROXY} --build-arg ARG_GIT_TAG=${gittag} -t ${tag} -f ${dockerfile} .
	success "built ${tag}"

        if [ ${DOCKER_USE_HUB} = "1" ]; then
            docker push ${tag}
	    success "pushed ${tag}"
        fi
        set +x
    done

    rm -f .version || true
    success 'docker release build'
}


# docker build and push in CI
ci_dockerbuild() {
    info 'ci docker build'
    _ci_docker_login
    create_base_image
    create_build_image
    create_release_tarball
    _docker_release_build
    success 'ci docker build'
}


_test_stack_up() {
    info 'test stack up'
    mkdir -p data/tests
    chmod o+rwx data/tests

    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml rm --force
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml build
    success 'test stack built'
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml up -d
    set +x
    success 'test stack up'
}


_test_stack_down() {
    info 'test stack down'
    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-teststack.yml stop
    set +x
    success 'test stack down'
}


run_unit_tests() {
    info 'run unit tests'
    _test_stack_up

    set +e
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-unittests.yml rm --force
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-unittests.yml build
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-unittests.yml up
    rval=$?
    set -e

    _test_stack_down

    return $rval
}


# publish rpms to testing repo
rpm_publish() {
    info 'rpm publish'
    time ccg publish_testing_rpm:data/rpmbuild/RPMS/x86_64/yabi*.rpm,release=6
    success 'rpm publish'
}


# build a docker image and start stack on staging using docker-compose
ci_docker_staging() {
    info 'ci docker staging'
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
    info 'selenium stack up'
    mkdir -p data/selenium
    chmod o+rwx data/selenium

    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-selenium.yml up -d
    set +x
    success 'selenium stack up'
}


_selenium_stack_down() {
    info 'selenium stack down'
    set -x
    docker-compose --project-name ${PROJECT_NAME} -f docker-compose-selenium.yml stop
    set +x
    success 'selenium stack down'
}


lettuce() {
    info 'lettuce'
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
python_lint() {
    info "python lint"
    pip install 'flake8>=2.0,<2.1'
    flake8 yabi/yabi yabish/yabishell --count
    success "python lint"
}


# lint js, assumes closure compiler
js_lint() {
    info "js lint"
    pip install 'closure-linter==2.3.13'
    JSFILES="yabi/yabi/yabifeapp/static/javascript/*.js yabi/yabi/yabifeapp/static/javascript/account/*.js"
    for JS in $JSFILES
    do
        gjslint --disable 0131 --max_line_length 100 --nojsdoc $JS
    done
    success "js lint"
}


make_virtualenv() {
    info "make virtualenv"
    # check requirements
    if ! which virtualenv > /dev/null; then
      fail "virtualenv is required by develop.sh but it isn't installed."
    fi
    if [ ! -e ${VIRTUALENV} ]; then
        virtualenv ${VIRTUALENV}
    fi
    . ${VIRTUALENV}/bin/activate

    if ! which docker-compose > /dev/null; then
      pip install 'docker-compose<1.6' --upgrade || true
    fi
    success "$(docker-compose --version)"
}


echo ''
info "$0 $@"
make_virtualenv

if [ ${SET_HTTP_PROXY} = "1" ]; then
    _http_proxy
else
    info 'Not setting http_proxy'
fi

case $ACTION in
pythonlint)
    python_lint
    ;;
jslint)
    js_lint
    ;;
start)
    start_dev
    ;;
start_full)
    start_dev_full
    ;;
build)
    build_dev
    ;;
releasetarball)
    create_release_tarball
    ;;
start_release)
    start_release
    ;;
rpmbuild)
    rpm_build
    ;;
baseimage)
    create_base_image
    ;;
buildimage)
    create_build_image
    ;;
releaseimage)
    create_release_image
    ;;
devimage)
    build_dev
    ;;
ci_dockerbuild)
    ci_dockerbuild
    ;;
rpm_publish)
    _ci_ssh_agent
    rpm_publish
    ;;
runtests)
    run_unit_tests
    ;;
ci_docker_staging)
    _ci_ssh_agent
    ci_docker_staging
    ;;
ci_rpm_staging)
    _ci_ssh_agent
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
