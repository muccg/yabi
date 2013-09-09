Installation under Apache
=========================

Prerequisites
-------------

There are build requirements on Linux systems that you may need. These commands will install them:

 ``$sudo yum install python-setuptools python-devel gcc openssl-devel.x86_64 postgresql84-devel``
 ``$sudo yum install mysql-server mysql mysql-devel MySQL-python libxslt-devel libxml2-devel mod_ssl``
 ``$sudo easy_install pip virtualenv``

**NB:** You might need to change to the right postgres devel version



.. index::
  single: erlang

Erlang
^^^^^^
Yabi uses RabbitMQ as a message broker which itself requires Erlang. The erlang package is provided via EPEL.

Add EPEL via:
 ``$ wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm``
 ``$ wget http://rpms.famillecollet.com/enterprise/remi-release-6.rpm``
 ``$ sudo rpm -Uvh remi-release-6*.rpm epel-release-6*.rpm``

Then install Erlang:

 ``$sudo yum install erlang``


.. index::
  single: rabbitmq

RabbitMQ
^^^^^^^^
To install RabbitMQ:
::
 ``$ wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.1.3/rabbitmq-server-3.1.3-1.noarch.rpm``
 ``$ sudo rpm --import http://www.rabbitmq.com/rabbitmq-signing-key-public.asc``
 ``$ sudo yum install rabbitmq-server-3.1.3-1.noarch.rpm``

Start the service with:
 ``$ /etc/init.d/rabbitmq-server start``


Database
^^^^^^^^

See :ref:`database`.

Yabi RPMS
^^^^^^^^^

.. index::
    single: yabiadmin

Yabi Admin ( The web application )
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

 ``$ sudo yum install yabi-admin-7.0.0-1.x86_64.rpm``

This will add an Apache conf file to /etc/httpd/conf.d called yabiadmin.ccg.
For Apache to pick this up automatically, create a symbolic link:

 ``$ ln -s yabiadmin.ccg yabiadmin.conf``


Yabish
^^^^^^

See See :ref:`yabish`.

.. index::
    single: celery

Start Celery
------------

`Celery <http://celeryproject.org/>`_ is an asynchronous task queue/job queue used by Yabi. It needs to be started separately.

   ``$/etc/init.d/celeryd start``

An example of our celeryd init script can be found in our `source code repository <http://code.google.com/p/yabi/source/browse/yabiadmin/admin_scripts/celeryd>`_.

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

In file: ``/etc/httpd/conf.d/wsgi.conf``

::

   <IfModule mod_wsgi.c>
   LoadModule wsgi_module modules/mod_wsgi.so
   </IfModule>
::

Link ``/etc/httpd/conf.d/yabiadmin.ccg to /etc/httpd/conf.d/yabiadmin.conf`` for it to be loaded by Apache.