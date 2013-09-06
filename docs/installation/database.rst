.. index::
    pair: database; postgres
    pair: database; mysql
    pair: database; sqlite

Database Setup
==============

The Yabi codebase employs `South <http://south.aeracode.org/>`_ to manage schema and data migrations. Because of this when initially setting
up your database you need only create an empty data base called yabi_live and grant access.
From there the install process will create the schema, insert setup data, create 
initial users etc.

To change the database that Yabi points at you will need to alter the DATABASES section
in the Django settings file. For more details see :ref:`settings`.

.. index::
   single: mysql

MySQL
^^^^^
Ensure service is started:

 $ /etc/init.d/mysqld start

Create databases required:

 $ mysql -uroot -e "create database yabi_live default charset=UTF8;"


 Initialise Yabi database:
 $ export PYTHONPATH=/usr/local/webapps/yabiadmin:/usr/local/webapps/yabiadmin/lib/:$PYTHONPATH
 $ export DJANGO_SETTINGS_MODULE=defaultsettings.yabiadmin
 $ /usr/local/webapps/yabiadmin/bin/django-admin.py syncdb
Do not create users at this point.
 $ /usr/local/webapps/yabiadmin/bin/django-admin.py migrate
