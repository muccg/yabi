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

To initialise the database you will have to run the Django migrations in the Yabi project::

 # yabi migrate

These will create the schema, insert setup data, and create initial users.

Make sure Apache can connect to the database
--------------------------------------------

SELinux on CentOS systems will prevent Apache to connect to any network services by default.
Yabi needs to be able to connect to your database, so you will need to set at least the first of the following SELinux booleans to on:

    httpd_can_network_connect_db (HTTPD Service)
        Allow HTTPD scripts and modules to network connect to databases.
    httpd_can_network_connect (HTTPD Service)
        Allow HTTPD scripts and modules to connect to the network.
