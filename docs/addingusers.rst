.. index::
   single: users
   single: users; adding

.. _addingusers:

Adding Users
============

To add users to the Yabi system you will need to be logged into the Adminstration part of the application.

.. index::
   single: users; regular

Adding Regular Users
--------------------

At the main page you will see a list of all tables available for editing. Of interest are the Auth User table
and the Yabi User table.

The Auth User is the main authentication table used by Django Auth to store user details. Add a record to this table
ensuring that the Active checkbox is ticked and the Staff and Superuser checkboxes are **not** ticked.

When you create an Auth User record you will find that a corresponding Yabi User record is automatically created. This 
is where additional user information can be stored. If you edit the Yabi User record you will see two options:

* User option access - controls whether the Account and Change Password screens are available to the user
* Credential access - determines whether the Credential modification screen is available to the user

.. index::
    single: ldap
    single: authentication

Using Different Authentication Backends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are using a different authentication method such as LDAP or "Kerberos and LDAP" you don't have to add
users manually to the Yabi. After you set up Yabi to use one of these authentication methods all you have to do is
add the user to the Yabi or Yabi Administrators LDAP group and their user account will be created automatically
the first time they log in into Yabi.

See :ref:`authentication` for more detail on setting up LDAP or "Kerberos and LDAP" authentication.


.. index::
   single: users; administrator

Adding Adminstrator Users
-------------------------

To add an adminstrator follow the steps above to add a regular user and the also ensure that the Staff 
and Superuser checkboxes are ticked.

If you wish to you could use the Django Permissions system to give finer grained permissions to users i.e. 
permission to add tools only.

.. index::
   single: users; setup

.. _viewing_a_users_setup:

Viewing a User's Setup
----------------------

There are a couple of admin tools that allow an administrator to view a users setup. First click on Users under the Yabi section 
(**not** under the Auth section). This will show you a list of users you have added to Yabi. Clicking on the ``Tools`` 
or ``Backend`` links will give you further detail.

User Tools
^^^^^^^^^^

This listing will show you all the tools a user has access to and the tool groups the tools belong to.

User Backends
^^^^^^^^^^^^^

This listing will show you all the execution and filesystem backend credentials set up for the user.
