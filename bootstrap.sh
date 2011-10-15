#!/bin/bash

# You need to have:
#   python header files 

PROJECT_DIR=`pwd`
CACHE='/tmp'
PIP_DOWNLOAD_CACHE=${CACHE}
EGGS_DIR='eggs/'
EGGS_PATTERN='*.*' #this ignores dirs, but means egg names must contain a .
INSTALL_EGGS=1 #if this is 1, we will install eggs from eggs/...
CONFIG_DIR=""
TARGET_PYTHON="python"

export PIP_DOWNLOAD_CACHE

help() {
    echo >&2 "Usage $0 [-p targetpython] [-c configname]"
            echo >&2 "target python is the interpreter you want your virtual python to be based on (default=python)"
            echo >&2 "configname is the name of a subdir of eggs containing custom eggs for your environment"
            exit 1;
    
}

if [ $# -eq 1 ]
then
    help;
fi

#parse command line options
while getopts p:c: opt
do case "$opt" in 
    p)      TARGET_PYTHON="$OPTARG";;
    c)      CONFIG_DIR="$OPTARG";;
    [?]|*)  help;; 
    esac
done

#First, lets check to see if the config dir exists
EGGS_PATH="$EGGS_DIR$CONFIG_DIR/$EGGS_PATTERN"
if [ ! -d $EGGS_DIR$CONFIG_DIR ]
then
    if [ "$CONFIG_DIR" != "" ]
    then
        echo "No such configuration path exists: $EGGS_PATH"
        if [ -d $EGGS_DIR ]
        then    
            echo "Perhaps try one of these:"
            cd $EGGS_DIR
            for arg in *
            do
                if [ -d $arg ]
                then
                    echo "$arg"
                fi
            done
        cd ..
        fi
        echo "Explicit config $CONFIG_DIR given but didn't exist - exiting"
        exit
    else
        echo "No eggs dir found, proceeding with bare install."
        INSTALL_EGGS=0
    fi
fi

if [ $INSTALL_EGGS -eq 1 ]
then
    echo "---+++---"
    echo "Building for eggs in $EGGS_PATH"
    if [ -f $EGGS_DIR$CONFIG_DIR/DEPENDENCIES ]
    then
        cat $EGGS_DIR$CONFIG_DIR/DEPENDENCIES
    fi    
    echo "---+++---"
fi

BASE_DIR=`basename ${PWD}`
PRE="virt_"
VPYTHON_DIR="$PRE$BASE_DIR"
VIRTUALENV="virtualenv-1.6.1"
VIRTUALENV_TARBALL="${VIRTUALENV}.tar.gz"
PIP="./${VPYTHON_DIR}/bin/pip"
PIP_OPTS="-I --use-mirrors --timeout=10"
YOPYPI="./${VPYTHON_DIR}/bin/yopypi-cli"

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

    ${PIP} install ${PIP_OPTS} yopypi
    ${YOPYPI} start
    ${PIP} install ${PIP_OPTS} -r requirements.txt
    ${YOPYPI} stop

    # hack activate to set some environment we need
    echo "PROJECT_DIRECTORY=`pwd`;" >>  $VPYTHON_DIR/bin/activate
    echo "export PROJECT_DIRECTORY " >>  $VPYTHON_DIR/bin/activate
    
    #if we have env stuff in an ENVIRONMENT file, source it. It should
    #be coded to hack more stuff onto the end of activate
    if [ -f $EGGS_DIR$CONFIG_DIR/ENVIRONMENT ]
    then
        source $EGGS_DIR$CONFIG_DIR/ENVIRONMENT
    fi
fi

echo -e "\n\n What just happened?\n\n"
echo -e " * Python has been installed into $VPYTHON_DIR"
cat requirements.txt
if [ $INSTALL_EGGS -eq 1 ]
then
    echo " * eggs from the eggs in this project ($EGGS_PATH) have been installed"
fi


# tell the user how to activate this python install
echo -e "\n\nTo activate this python install, type the following at the prompt:\n\nsource $VPYTHON_DIR/bin/activate\n"
echo -e "To exit your virtual python, simply type 'deactivate' at the shell prompt\n\n"
