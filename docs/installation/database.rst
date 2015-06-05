.. highlight:: console

.. _database-setup:

Database Setup
==============

We assume that you have a database server (preferably Postgres) installed, that is accessible from the server you're performing the Yabi installation on.

Create the Yabi database
------------------------

Please create a database (ex. ``yabi_prod``) that will be used by the Yabi application.
We recommend creating a user called ``yabiapp`` with no special privileges that will be the owner of the database.

Configure Yabi to use Yabi database
-----------------------------------

To change the database that Yabi points at you will need to alter the Yabi settings file.
Open up ``/etc/yabi/yabi.conf`` in your editor and make sure the variables in the *database options* section (``dbserver``, ``dbname``, ``dbuser`` etc.) are set correctly.

For more details see :ref:`settings`.

Initialise the Yabi database
----------------------------

The Yabi codebase employs `South <http://south.aeracode.org/>`_ to manage schema and data migrations.
To initialise the database::

 # yabiadmin syncdb --noinput
 # yabiadmin migrate

These will create the schema, insert setup data, and create initial users.
