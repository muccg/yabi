A guide to getting Yabi running for developers

Dependencies
------------

    Python
    python include headers
    Stackless Python setup as per BuildingStacklessPython
    Memcached running on the local machine (or change the yabi settings to point at your memcached server)
    sqlite3 (or other database supported by Django)
    Mercurial


Checkout source code
--------------------

Yabi is stored in a mercurial repository. All three main components are in the same repository, so only one checkout is required.

    hg clone https://code.google.com/p/yabi/

Running Yabi
------------

To run Yabi you need to start Yabi Frontend, Yabi Admin Console and the Yabi Backend.

All this components can be controlled from the top level (the directory you cloned https://code.google.com/p/yabi/ to) using fab commands.

In order to use the top level fab commands you will have to bootstrap at the top level.

    $ sh bootstrap.sh

This will create a virtual python environment and will install the right version of fab. Please activate the virtual environment as instructed by the bootstrap script.

To test that everything worked properly you should be able to run

    $ fab -l

And the output should be similar to:

    Available commands:

    admin_bootstrap Bootstrap the yabiadmin project
    admin_initdb Initialise the DB of Yabiadmin
    admin_killcelery Kill the yabiadmin celery server
    admin_killserver Kill the yabiadmin local server
    admin_quickstart Quickstart the yabiadmin project (bootstrap, initdb
    admin_runcelery Run the yabiadmin celery server for local dev
    admin_runserver Run the yabiadmin server for local dev (:bg for
    be_bootstrap Bootstrap the yabibe project
    be_createdirs Creates necessary directories for the yabibe project
    ...

As you can see, we have commands that control all components (admin commands for Yabi Admin, fe commands for Yabi Frontend, be commands for Yabi Backend).

Running Yabi servers in separate terminals
------------------------------------------

In this setup you will be running each Yabi server in the foreground in a separate terminal.

Start up a terminal and run

    $ fab fe_quickstart

In a new terminal run

    $ fab admin_quickstart

In a new terminal run

Note: If you haven't followed the recommended way to install Stackless Python (BuildingStacklessPython) make sure that you edit fabfile.py at the top level and change the variable STACKLESS_PYTHON to point to your stackless python binary.

    $ fab be_quickstart

After fab admin_quickstart above finished in a new terminal run

    $ fab admin_runcelery


Running Yabi servers in the background
--------------------------------------

In this setup you will run each Yabi server in the background.

Logs will be written to each component's directory (ie. yabife/yabife/yabife.log for Yabi Frontend,yabiadmin/yabiadmin/yabiadmin.log for Yabi Admin etc.)

    $ fab quickstart

This will set up all Yabi components and run the four servers (Yabi Frontend, Yabi Admin, Yabi Admin Celery, Yabi Backend) in the background.

The servers can be stopped by

    $ fab killservers

or individually by: fab fe_killserver, fab admin_killserver, `fab admin_killcelery or fab be_killserver`.

To start up the servers again without going through the setup phase (bootstrap, database creation etc.) just

    $ fab runservers

Access
------
    http://127.0.0.1:8000/ - username:demo password:demo

    http://127.0.0.1:8001/admin/ - username:admin password:admin

Troubleshooting
---------------

If you wish to use a database other than sqlite then you will need to edit the yabife and yabiadmin settings.py files to point at the correct database.

Setting up Yabish
-----------------

Note: If you chose to run fab quickstart in one command (fab quickstart)
you can skip this step, as fab quickstart will set up Yabish as well.

If you would like to use yabish (the commad line interface to YABI) or
you want to run the automated end to end test suite that uses Yabish,
you will have to bootstrap it:

    $ fab yabish_bootstrap

Setting up Tests
----------------

Note: If you chose to run fab quickstart in one command (fab quickstart)
you can skip this step, as fab quickstart will set up the Tests as well.

    $ fab tests_bootstrap

Running Tests
-------------

Yabi has an end to end test suite for testing the full Yabi stack. 
In order for the tests to be run you have to have all the servers running as described in Running Yabi above.
If you followed the steps above and all the servers are running you can just run the tests by:

    $ fab tests

In case you stopped the servers or they aren't running currently you can:

    $ fab runservers tests

Or if you want to stop the servers after you ran the tests:

    $ fab runservers tests killservers



