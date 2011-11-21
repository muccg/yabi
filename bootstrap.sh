#!/bin/bash

# You need to have:
#   python header files 

# if any subscript fails, fail the entire script so we immediately know
set -e

PROJECT_DIR=`pwd`
CACHE='/tmp'
PIP_DOWNLOAD_CACHE=${CACHE}
CONFIG_DIR=""
TARGET_PYTHON="python"
REQUIREMENTS=""
BUILD_REQUIREMENTS="build-requirements.txt"
BASE_DIR=`basename ${PWD}`
PRE="virt_"
VPYTHON_DIR="$PRE$BASE_DIR"
VIRTUALENV="virtualenv-1.6.4"
VIRTUALENV_TARBALL="${VIRTUALENV}.tar.gz"
PIP="./${VPYTHON_DIR}/bin/pip"
PIP_OPTS="--use-mirrors --no-index --mirrors=http://c.pypi.python.org/ --mirrors=http://d.pypi.python.org/ --mirrors=http://e.pypi.python.org/"

export PIP_DOWNLOAD_CACHE

help() {
    echo >&2 "Usage $0 [-p targetpython] [-r requirements]"
    echo >&2 "targetpython is the interpreter you want your virtual python to be based on"
    echo >&2 "requirements is pip requirements file to optionally install"
    exit 1;
}

if [ $# -eq 1 ]
then
    help;
fi

#parse command line options
while getopts p:r: opt
do case "$opt" in 
    p)      TARGET_PYTHON="$OPTARG";;
    r)      REQUIREMENTS="$OPTARG";;
    [?]|*)  help;; 
    esac
done

# we need a bootstrap file
if [ ! -f "${BUILD_REQUIREMENTS}" ]
then
    echo "No build requirements file found - ${BUILD_REQUIREMENTS}"
    exit 1;
fi

# only install if we dont already exist
if [ ! -d $VPYTHON_DIR ]
then
    echo -e '\n\nNo virtual python dir, lets create one\n\n'

    # only install virtual env if its not hanging around
    if [ ! -d "${CACHE}/${VIRTUALENV}" ]
    then
        echo -e '\n\nNo virtual env, creating\n\n'
  
        # only download the tarball if needed
        if [ ! -f "${CACHE}/${VIRTUALENV_TARBALL}" ]
        then
            wget -O "${CACHE}/${VIRTUALENV_TARBALL}" http://pypi.python.org/packages/source/v/virtualenv/${VIRTUALENV_TARBALL}
        fi

        # build virtualenv
        cd ${CACHE}
        tar zxvf $VIRTUALENV_TARBALL
        cd $VIRTUALENV
        $TARGET_PYTHON setup.py build
        cd ${PROJECT_DIR}

    fi
       
    # create a virtual python in the current directory
    $TARGET_PYTHON ${CACHE}/$VIRTUALENV/build/lib*/virtualenv.py --no-site-packages $VPYTHON_DIR

    ${PIP} install ${PIP_OPTS} -r ${BUILD_REQUIREMENTS}
    if [ -f "${REQUIREMENTS}" ]
    then
        if [ -f "pre-${REQUIREMENTS}" ]
        then 
            ${PIP} install ${PIP_OPTS} -r pre-${REQUIREMENTS}
        fi
        ${PIP} install ${PIP_OPTS} -r ${REQUIREMENTS}
        if [ -f "post-${REQUIREMENTS}" ]
        then 
            ${PIP} install ${PIP_OPTS} -r post-${REQUIREMENTS}
        fi
    fi

    # hack activate to set some environment we need
    echo "PROJECT_DIRECTORY=`pwd`;" >>  $VPYTHON_DIR/bin/activate
    echo "export PROJECT_DIRECTORY " >>  $VPYTHON_DIR/bin/activate
fi

# tell the user how to activate this python install
echo -e "\n\n What just happened?\n\n"
echo -e " * Python has been installed into $VPYTHON_DIR"
cat ${BUILD_REQUIREMENTS}
if [ -f "${REQUIREMENTS}" ]
then
    cat ${REQUIREMENTS}
fi
echo -e "\n\nTo activate this python install, type the following at the prompt:\n\nsource $VPYTHON_DIR/bin/activate\n"
echo -e "To exit your virtual python, simply type 'deactivate' at the shell prompt\n\n"
