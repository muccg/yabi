.. index::
    single: django
    single: caching

.. _caching:

Caching
=======

Yabi makes use of the Django caching mechanisms so you should also refer to their documenation:

`https://docs.djangoproject.com/en/dev/topics/cache/ <https://docs.djangoproject.com/en/dev/topics/cache/>`_

By default Yabi uses file based caching but for any system that is in production use we would recommend using
memcached. To do so you would need to have memcached installed and running and then change either the main settings.py file from:

::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': WRITABLE_DIRECTORY,
        }
    }

to:

::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': 'localhost.localdomain:11211',
            'KEYSPACE': "yabiadmin"
        }
    }
   
Or include the second block in your own private settings file so it overrides that in settings.py. See :ref:`settings`