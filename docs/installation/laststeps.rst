.. highlight:: console

.. _laststeps:

Last steps
==========

At this stage we should have everything installed, the database, caching and sessions configured.

As a last step before starting the applications you should go through all the variables in ``/etc/yabiadmin/yabiadmin.conf`` and make sure everything is set to sensible values. See :ref:``settings``.

Restart apache
--------------

To start up the Yabi web application restart Apache::

 # /etc/init.d/httpd restart

Start Celery
------------

To start up the Yabi Backend start Celery::

 # /etc/init.d/celeryd start


At this stage you should be able to access the Yabi web application by browsing to https://YOURHOST/yabi/.

The Yabi default installation creates two users *demo* and *admin*, where *demo* is a normal user and *admin* is Yabi administrator.
The password for *demo* is *demo* and for *admin* is *admin*.

In order to test the system, log in with the *demo* user and create a workflow that has one job running the ``hostname`` tool. You should be able to submit this workflow and it should run to completion.

