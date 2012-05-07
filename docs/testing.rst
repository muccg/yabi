.. index::
   single: testing

Testing
=======

Setting up Tests
----------------

Note: If you chose to run fab quickstart in one command (fab quickstart)
you can skip this step, as fab quickstart will set up the Tests as well.

    $ fab tests_bootstrap

Running Tests
-------------

Yabi has an end to end test suite for testing the full Yabi stack. 
In order for the tests to be run you have to have all the servers running as described in :ref:`quickstart` above.
If you followed the steps above and all the servers are running you can just run the tests by:

    $ fab tests

In case you stopped the servers or they aren't running currently you can:

    $ fab runservers tests

Or if you want to stop the servers after you ran the tests:

    $ fab runservers tests killservers

Important Note:

By default the tests assume that you have a clean database - a database you have run fab admin_initdb on and you haven't modified any of the data.
One way to assure this is to always drop the yabiadmin database, create it again and run fab admin_initdb before you run the tests.
If you would like to keep the data in your local database, but run the tests, you could create another database just for testing.

YABI provides different configurations and top level fab commands to make this easier.

Look in yabiadmin/yabiadmin/appsettings_dir to see some of the pre-configured database configurations. You would probably see there directories for at least: sqlite_test, postgres and postgres_test.
For example if you would like to set up a local Postgres database for testing:
 
    - install Postgres
    - create a Postgres user ex. yabminapp
    - create a Postgres database owned by the user ex. test_yabi
    - make sure the the yabiadmin/yabiadmin/appsettings_dir/postgres_test/yabiadmin.py is set up with the DB setting (by default it uses the values above)

To activate the Postgres Test configuration use:

    $ fab admin_activate_config:postgres_test

Now

    $ fab admin_active_config 

will show the active configuration in this case postgres_test


The fab command admin_list_active_configs will display all available configurations.

To deactivate the active configuration (makes the default settings in setting.py active) use

    $ fab admin_deactivate_config


Running the tests automatically on a test database
--------------------------------------------------

If you would like to regularly run the tests on a test db, but then use the DB defined in your settings.py file, you could do the following.


Designate a test DB
^^^^^^^^^^^^^^^^^^^

Decide which configuration would you like to use as a test DB. For example postgres_test.
Select the designated config to run tests against:

    $ fab admin_select_test_config:postgres_test

If this worked the following command should display your chosen configuration:

    $ fab admin_selected_test_config


Running the tests against the designated test DB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the command 

    $ fab runtests

to run the tests.

The runtests command will:

    - run the Google Closure Linter against all the JavaScript in the project
    - kill all yabi servers (fab killservers)
    - switch the Yabiadmin configuration to the special testdb (fab admin_activate_config testdb)
    - recreate the test database from scratch
    - run all the yabi servers (fab runservers)
    - run all the tests (fab tests)
    - kill all yabi servers
    - deactivate the testdb configuration (ie. switches you back to your settings.py)

Designate a test DB and running all the tests in one step
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A quicker way to select a test DB and run all tests against it is to pass in the config as an argument to runtests:

    $ fab runtests:postgres_test

This will select postgres_test as your test DB and then run all the tests against it.

From then on you can just run

    $ fab runtests

as long as you would like to run the tests against the same DB.


Tasks used by runtests
----------------------

Some of the tasks used by the "fab runtests" command could be used on their during developement.

Drop/create database
^^^^^^^^^^^^^^^^^^^^

The following commands will try to create/drop the database defined in your settings file.
The commands issued are RDBMS specific, currently sqlite3, mysql and postgres are supported.

In order for this to work the user defined in your setting has to have rights to drop and create databases.

WARNING! This commands will operate on the currently active DB, so make sure that you know which DB you are running them against. Starting with

    $ fab admin_active_config

is probably good practice.

    $ fab admin_dropdb

will drop the currently active DB.

    $ fab admin_createdb

will create the currently active DB.

    $ fab admin_recreatedb

will drop and then create your active DB (same as "fab admin_dropdb admin_createdb")

When you recreate the DB it will have no schema and initial data so you would normally want to follow a recreation with

    $ fab admin_initdb

this will create the schema and import the initial data into the DB.


JSLint
^^^^^^

The tests will fail if our JavaScript isn't passing the Google Closure Linter tests. You can run the Linter against all our JavaScript by:

    $ fab admin_jslint

