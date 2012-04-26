
.. _quickstart:

Quickstart
==========
Yabi can be run from the top level directory (i.e. the directory you cloned https://code.google.com/p/yabi/ to) using Fabric (fab) commands.

In order to use the top level fab commands you will have to bootstrap at the top level.

    $ sh bootstrap.sh

This will create a virtual python environment and will install the right version of Fabric. Please activate the virtual environment as instructed by the bootstrap script.

To test that everything worked properly you should be able to run

    $ fab -l

And the output should be similar to:

::

    Available commands:

    admin_bootstrap     Bootstrap the yabiadmin project
    admin_initdb        Initialise the DB of Yabiadmin
    admin_killcelery    Kill the yabiadmin celery server
    admin_killserver    Kill the yabiadmin local server
    admin_quickstart    Quickstart the yabiadmin project (bootstrap, initdb
    admin_runcelery     Run the yabiadmin celery server for local dev
    admin_runserver     Run the yabiadmin server for local dev (:bg for
    be_bootstrap        Bootstrap the yabibe project
    be_createdirs       Creates necessary directories for the yabibe project
    ...

As you can see, we have commands that control all components (admin commands for Yabi Admin, be commands for Yabi Backend).


Running Yabi servers in the background
--------------------------------------

In this setup you will run each Yabi server in the background.

    $ fab quickstart

This will set up all Yabi components (Yabi Admin, Yabi Admin Celery, Yabi Backend) and run them in the background.

The servers can be stopped by:

    $ fab killservers

or individually by:

    $ fab admin_killserver
    $ fab admin_killcelery
    $ fab be_killserver

To start up the servers again without going through the setup phase (bootstrap, database creation etc.) just

    $ fab runservers

Accessing Yabi
--------------
http://127.0.0.1:8000/ - username:demo password:demo

http://127.0.0.1:8000/admin/ - username:admin password:admin

NB: Logging into Admin as the admin user will log you out as the demo user.


Logging
-------
Logs will be written to each component's directory (ie. yabiadmin/yabiadmin/yabiadmin.log for Yabi Admin etc.)


Running Yabi servers in separate terminals
------------------------------------------

If you want to you can run each component of Yabi in the foreground in a separate terminal.
Make sure you have run the 'fab quickstart' command above to build the project.

Start up a terminal, activate the virtual environment and run:

    $ fab admin_runserver

In a new terminal run, after activating the virtual environment, run:

    $ fab be_runserver

In a new terminal run, after activating the virtual environment, run:

    $ fab admin_runcelery
