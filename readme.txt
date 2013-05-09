A guide to getting Yabi running for developers

Dependencies
------------

    python (we are currently using 2.6)
    python include headers
    Memcached running on the local machine (or change the yabi settings to point at your memcached server)
    sqlite3 
    libevent
    libevent include headers ( 'libevent-dev' package on many distributions )


Running Yabi
------------

To run Yabi you need to start Yabi Admin, Yabi Backend and the Yabi Admin Celery server.

All this components can be controlled from the top level directory using 'develop.sh'.

    $ ./develop.sh 
Usage ./develop.sh (status|test_mysql|test_postgresql|dropdb|startall|startyabibe|startyabiadmin|startceleryd|stopall|stopyabibe|stopyabiadmin|stopceleryd|install|clean)

To create virtual pythons for running a local development stack:

    $ ./develop.sh install

To start:

    $ ./develop.sh start

To stop:

    $ ./develop.sh stop

Access
------
    http://127.0.0.1:8000/ - username:demo password:demo

    http://127.0.0.1:8000/admin/ - username:admin password:admin

    NB: Logging into Admin as the admin user will log you out as the demo user.

Running Tests
-------------

Yabi has an end to end test suite for testing the full Yabi stack. 

    $ ./develop.sh test_mysql|test_postgresql
