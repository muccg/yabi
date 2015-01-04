A guide to getting Yabi running for developers
==============================================

Our main target deployment platform is the latest version of CentOS (currently 6.4).
That's why we also develop on the same OS.
Developing on other Linux distributions or other versions shouldn't be a problem, but
if you don't have other preferences, developing on the latest CentOS is a good
practical default (ie. doing so and following this documentation would probably
mean things will just work).

All our Yabi installation are using the Postgresql database. We do recommend it as
a first choice over MySQL or other databases.

Dependencies
------------

    o python (we are currently using 2.7.6)
    o GCC
    o Virtualenv (for Python 2.7)
    o Postgresql
    o libxslt-devel, libxml2-devel
    o RabbitMQ (and Erlang)


To install the dependencies on CentOS (tested on 6.4):

  o Python 2.7 is required. Typically we install that using packages from https://iuscommunity.org/.

  o For uwsgi dependencies:

    $ sudo yum install pcre pcre-devel

  o For all the other dependencies but RabbitMQ, with the EPEL repository enabled:

    # sudo yum install gcc mercurial python-virtualenv postgresql-devel mysql-server mysql mysql-devel MySQL-python libxslt-devel libxml2-devel

  o To install RabbitMQ follow the instructions at:

    http://www.rabbitmq.com/install-rpm.html


To install the dependencies on Ubuntu (tested on 14.04):


  o Python is installed by default.

  o Build chain:

    $ sudo apt-get install build-essential

  o For uwsgi dependencies:

    $ sudo apt-get install libpcre3 libpcre3-dev

  o For all the other dependencies but RabbitMQ:

    $ sudo apt-get install gcc mercurial python-dev python-virtualenv libpq-dev mysql-server mysql-client libxml2-dev libxslt-dev python-mysqldb libmysqlclient-dev postgresql

  o To install RabbitMQ follow the instructions at:

    http://www.rabbitmq.com/install-debian.html


After you've installed all dependencies, make sure you start Postgresql and RabbitMQ

    # service postgresql start

    # service rabbitmq-server start

Create the user yabiapp with password yabiapp in Postgres. Make sure you can connect using this user and password with psql.
Creating Postgres users is explained in the Postgres documentation at: http://www.postgresql.org/docs/9.3/static/database-roles.html .

Create a development and a test database for Yabi using the yabiapp user you've just created. Your commands should be similar to:

    $ psql -aeE -U yabiapp -c "create database dev_yabi;" template1
    $ psql -aeE -U yabiapp -c "create database test_yabi;" template1


Running Yabi
------------

To run Yabi you need to start Yabi Admin and the Yabi Admin Celery server.

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

    For admin access: use username:admin password:admin

    NB: Logging into Admin as the admin user will log you out as the demo user.


Running Tests
-------------

Yabi has an end to end test suite for testing the full Yabi stack.
    o For the Torque tests you will need a working Torque installation
    o For the PBS Pro tests you will need a working PBS Pro installation
    o For the ssh tests, add tests/test_data/yabitests.pub to ~/.ssh/authorized_keys

    $ ./develop.sh test_postgresql


