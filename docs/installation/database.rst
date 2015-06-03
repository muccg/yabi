.. _database-setup:

Database Setup
==============

The Yabi codebase employs `South <http://south.aeracode.org/>`_ to manage schema and data migrations. Because of this when initially setting
up your database you need only create an empty database (recommended name yabi_prod) and change settings so that Yabi will point to it.
From there the install process will create the schema, insert setup data, create 
initial users etc.

To change the database that Yabi points at you will need to alter your database settings
in the Django settings file. For more details see :ref:`settings`.

