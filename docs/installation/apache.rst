.. highlight:: console

Installation under Apache
=========================

.. _erlang:

Erlang
^^^^^^

Yabi uses RabbitMQ as a message broker which itself requires Erlang::

 # yum install erlang

.. _rabbitmq:

RabbitMQ
^^^^^^^^

To install RabbitMQ::

 # rpm --import https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
 # yum install https://www.rabbitmq.com/releases/rabbitmq-server/v3.1.3/rabbitmq-server-3.1.3-1.noarch.rpm

Start the service with::

 # /etc/init.d/rabbitmq-server start

Database
^^^^^^^^

See :ref:`database-setup`.

.. _yabiadmin:

Yabi Admin ( The web application )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The IUS repository provides a ``httpd24u`` package that unfortunately conflicts with ``httpd``.
Therefore if you try to install ``yabi-admin`` you will get a conflict error.
The recommended way (`in the email announcing httpd24u <https://lists.launchpad.net/ius-community/msg01277.html>`_)
to get around this problem is to install the httpd package first and only after that install yabi-admin:: 

 # yum install httpd
 # yum install yabi-admin

This will add an Apache conf file to ``/etc/httpd/conf.d`` called ``yabiadmin.ccg``.
For Apache to pick this up automatically, create a symbolic link::

 # cd /etc/httpd/conf.d && ln -s yabiadmin.ccg yabiadmin.conf

.. _celery:

Start Celery
------------

`Celery <http://celeryproject.org/>`_ is an asynchronous task queue/job queue used by Yabi. It needs to be started separately::

 # /etc/init.d/celeryd start

An example of our celeryd init script and sysconfig file can be found in our `source code repository <https://bitbucket.org/ccgmurdoch/yabi/src//yabiadmin/init_scripts/centos/?at=master>`_.

Restart apache
--------------
For changes to take effect restart apache.


.. index::
    single: apache; configuration

Sample Apache Configuration
===========================

Introduction
------------

This is a sample configuration, for more complete references:
  * `https://docs.djangoproject.com/en/1.3/howto/deployment/modwsgi/ <https://docs.djangoproject.com/en/1.3/howto/deployment/modwsgi/>`_
  * `https://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines <https://code.google.com/p/modwsgi/wiki/ConfigurationGuidelines>`_
  * `https://httpd.apache.org/docs/ <https://httpd.apache.org/docs/>`_



Sample Yabi Configuration
-------------------------------

NB. Yabi uses wsgi so ensure mod_wsgi is loaded:

In file: ``/etc/httpd/conf.d/wsgi.conf``::

   <IfModule mod_wsgi.c>
     LoadModule wsgi_module modules/mod_wsgi.so
   </IfModule>

