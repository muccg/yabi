.. index::
    single: authentication

Authentication
==============

If you don't want to use ldap, you'll need to make changes in the :ref:`settings`:

Change this:

::

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.LDAPBackend',
        'django.contrib.auth.backends.NoAuthModelBackend',
    ]

To this:

::

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend'
    ]

