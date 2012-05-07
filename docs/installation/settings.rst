.. index::
    single: django
    single: settings.py

.. _settings:

Settings File
=============

As Yabi uses the Django web application framework, much of its configuration is
through the settings.py file. For most settings in this file you can consult
the `Django documentation <https://docs.djangoproject.com/en/dev/ref/settings/>`_.

Please note that at the end of our settings.py file we have included this:

::

    try:
        from appsettings.yabiadmin import *
    except ImportError, e:
        pass

This will attempt to load further settings from the PYTHONPATH. If it succeeds, then any setting in that file will
override the setting in the main settings.py file. In this way we can maintain our own private settings.

In the yabiadmin.wsgi file we establish this PYTHONPATH here:

::

    sys.path.append(os.path.join("/usr","local","etc","ccgapps"))

Then we have our private settings in this file: ``/usr/local/etc/ccgapps/appsettings/yabiadmin/__init__.py`` Please note
there must also be an ``__init__.py`` file in the appsettings directory for Python to recognise this as a module.

Development versus Production Settings
--------------------------------------

Yabi comes "out-of-the-box" with many settings set to development levels. For instance DEBUG is turned on and SSL_ENABLED is turned off.
If you are rolling Yabi out on to production servers **you must take care to change your settings to appropriate values**.

Your primary guide should be the Django documentation, in particular the `settings reference <https://docs.djangoproject.com/en/dev/ref/settings/>`_, 
where many best practice guidelines are provided. In particular you should also focus on these specific settings. If these are not set 
correctly the Login page will display a warning message.

::

    SSL_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    DEBUG = False
    SECRET_KEY - set to your own unique value


Example Private Settings File
-----------------------------

An example of the settings that we keep in this private settings file follows:

::

    # -*- coding: utf-8 -*-
    # set your own database here
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#databases
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.set_this',
            'USER': 'set_this',
            'NAME': 'set_this',
            'PASSWORD': 'set_this', 
            'HOST': 'set_this',                    
            'PORT': '',
        }
    }
    
    # if you are using ldap you can set all ldap settings at this level
    # you'll also need to make sure you are using the AUTHENTICATION_BACKENDS below
    AUTH_LDAP_SERVER = ['set_this']
    AUTH_LDAP_USER_BASE = 'set_this'
    AUTH_LDAP_GROUP_BASE = 'set_this'
    AUTH_LDAP_GROUP = 'yabi'
    AUTH_LDAP_DEFAULT_GROUP = 'baseuser'
    AUTH_LDAP_GROUPOC = 'groupofuniquenames'
    AUTH_LDAP_USEROC = 'inetorgperson'
    AUTH_LDAP_MEMBERATTR = 'uniqueMember'
    AUTH_LDAP_USERDN = 'ou=People'
    
    # these determine which authentication method to use
    # yabi uses modelbackend by default, but can be overridden here
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
    AUTHENTICATION_BACKENDS = [
     'django.contrib.auth.backends.LDAPBackend',
     'django.contrib.auth.backends.NoAuthModelBackend',
    ]
    
    # code used for additional user related operations
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#auth-profile-module
    AUTH_PROFILE_MODULE = 'yabifeapp.LDAPBackendUser'
    
    # Make this unique, and don't share it with anybody.
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
    SECRET_KEY = 'set_this'
    
    # memcache server list
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': ['memcache_server.localdomain:11211'],
            'KEYSPACE': "yabi"
        }
    }   

    # uncomment to use memcache for sessions, be sure to have uncommented memcache settings above
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#session-engine
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    
    # email settings so yabi can send email error alerts etc
    # see https://docs.djangoproject.com/en/dev/ref/settings/#email-host
    EMAIL_HOST = 'set_this'
    EMAIL_APP_NAME = "Yabi "
    SERVER_EMAIL = "apache@set_this"                      # from address
    EMAIL_SUBJECT_PREFIX = ""
    
    # admins to email error reports to
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#admins
    ADMINS = [
        ( 'alert', 'set_this' )
    ]
    
    # see: https://docs.djangoproject.com/en/dev/ref/settings/#managers
    MANAGERS = ADMINS
    
    # Make this unique, and don't share it with anybody.
    HMAC_KEY = 'set_this'
    
    # backend address
    BACKEND_IP = '0.0.0.0'
    BACKEND_PORT = '20000'
    BACKEND_BASE = '/'
    TASKTAG = 'set_this' # this must be the same in the yabi.conf for the backend that will consume tasks from this admin
    YABIBACKEND_SERVER = BACKEND_IP + ':' +  BACKEND_PORT
    YABISTORE_HOME = 'set_this'
    BACKEND_UPLOAD = 'http://'+BACKEND_IP+':'+BACKEND_PORT+BACKEND_BASE+"fs/ticket"


.. index::
    single: backend; configuration


Yabi Backend Configuration
==========================

On startup, the backend will load some default settings, and then go looking for a yabi.conf file of settings to load. The search path it uses is:

::

    ~/.yabi/yabi.conf
    ~/.yabi/backend/yabi.conf
    ~/yabi.conf
    ~/.yabi
    /etc/yabi.conf
    /etc/yabi/yabi.conf

If it doesn't find a yabi.conf file at one of these locations, it just starts up with the defaults.

You can find the default settings template in the `source code repository <http://code.google.com/p/yabi/source/browse/yabibe/yabibe/conf/yabi_defaults.conf?>`_
Copy this file to your preferred yabi.conf location and edit it to set the settings. You can also override this behavior and explicitly
set a yabi.conf location by setting the YABICONF environment variable before starting the backend.
