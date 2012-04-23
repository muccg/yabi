Database Setup
==============

By default when running a :ref:`quickstart` installation of Yabi the database used is SQLite.
However, for production systems we reccomend using Postgres or MySQL.

The Yabi codebase employs `South <http://south.aeracode.org/>`_ to manage schema and data migrations. Because of this when initially setting
up your database you need only create an empty data base called yabi_live and grant access.
From there the install process will create the schema, insert setup data, create 
initial users etc.

To change the database that Yabi points at you will need to alter the DATABASES section
in the Django settings file. For more details see :ref:`settings`.