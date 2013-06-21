A guide to getting Yabi running for developers

Dependencies
------------

    o python (we are currently using 2.6)
    o python include headers
    o Memcached running on the local machine (or change the yabi settings to point at your memcached server)
    o sqlite3 
    o libevent
    o libevent dev package
    o openssl
    o openssl dev package
    o libxml2
    o libxml2 dev package
    o libxslt dev package


Running Yabi
------------

To run Yabi you need to start Yabi Admin, Yabi Backend and the Yabi Admin Celery server.

All this components can be controlled from the top level directory using 'develop.sh'.

    $ ./develop.sh 

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
    o These require mysql and postgresql to be installed and running. 
    o For the Torque tests you will need a working Torque installation
    o For the PBS Pro tests you will need a working PBS Pro installation
    o For the ssh tests, add tests/test_data/yabitests.pub to ~/.ssh/authorized_keys

    $ ./develop.sh test_mysql|test_postgresql


