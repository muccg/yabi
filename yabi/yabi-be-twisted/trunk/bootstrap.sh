#!/bin/bash

#
# Its a sample script, tested only to the point of running manage.py runserver_plus
#
# You need to have python dev header files installed for mx.DateTime to install

BASE_PYTHON='/usr/local/stackless/bin/python'
VPYTHON_DIR='mypython'
VIRTUALENV='virtualenv-1.6.1'
VIRTUALENV_TARBALL='virtualenv-1.6.1.tar.gz'
EGG_DOWNLOAD_FILE='eggs/Downloads.txt'

# only install if we dont already exist
if [ ! -d $VPYTHON_DIR ]
then
    echo -e '\n\nNo virtual python dir, lets create one\n\n'

    # only install virtual env if its not hanging around
    if [ ! -d $VIRTUALENV ]
    then
        echo -e '\n\nNo virtual env, creating\n\n'
  
        # only download the tarball if needed
        if [ ! -f $VIRTUALENV_TARBALL ]
        then
            wget http://pypi.python.org/packages/source/v/virtualenv/$VIRTUALENV_TARBALL
        fi

        # build virtualenv
        tar zxvf $VIRTUALENV_TARBALL
        cd $VIRTUALENV
        $BASE_PYTHON setup.py build
        cd ..

    fi
       
    # create a virtual python in the current directory
    $BASE_PYTHON $VIRTUALENV/build/lib*/virtualenv.py --no-site-packages $VPYTHON_DIR

    # install all the eggs in this app
    for EGG in eggs/*
    do
        if [ "$EGG" != $EGG_DOWNLOAD_FILE ]
        then
            ./$VPYTHON_DIR/bin/easy_install  --allow-hosts=None  $EGG
        fi
    done
    
    # install the Downloads.txt eggs
#     for EGG in `cat $EGG_DOWNLOAD_FILE`
#     do
#         ./$VPYTHON_DIR/bin/easy_install $EGG
#     done
    
    # install

fi


# tell the (l)user how to activate this python install
echo -e "\n\nTo activate this python install, type the following at the prompt:\n\nsource $VPYTHON_DIR/bin/activate\n\n"
