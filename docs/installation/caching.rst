.. index::
    single: django
    single: caching

.. _caching:

Caching
=======

Yabi makes use of the Django caching mechanisms so you should also refer to their documentation:

`https://docs.djangoproject.com/en/dev/topics/cache/ <https://docs.djangoproject.com/en/dev/topics/cache/>`_

By default Yabi uses database caching but for any system that is in production use we would recommend using
memcached. To do so you would need to have memcached installed and running and then set the ``memcache`` config
variable to a space-separated list of memcache servers.

See :ref:`settings`


.. index::
    single: session

Session Engine
==============

Yabi uses a file-based session engine by default. However, in production you should look at using a memcache based
session engine. See:

`https://docs.djangoproject.com/en/1.3/topics/http/sessions/ <https://docs.djangoproject.com/en/1.3/topics/http/sessions/>`_


