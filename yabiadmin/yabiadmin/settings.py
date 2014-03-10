# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics
# (http://ccg.murdoch.edu.au/).
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS,"
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS.
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
### END COPYRIGHT ###

import os, sys
from ccg.utils.webhelpers import url
import djcelery
from kombu import Queue
import logging
import logging.handlers

WEBAPP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# setting to control ccg ssl middleware
# see http://code.google.com/p/ccg-django-extras/source/browse/
# you SHOULD change the SSL_ENABLED to True when in production
SSL_ENABLED = False

# set debug, see: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# see: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# see: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'yabiadmin.ssl.SSLRedirect',
    'django.contrib.messages.middleware.MessageMiddleware'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'yabiadmin.yabifeapp',
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'yabiadmin.uploader',
    'djcelery',
    'kombu.transport.django',
    'django_extensions',
    'south',
    'djamboloader',
    'django.contrib.admin'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'yabiadmin.urls'

# these determine which authentication method to use
# yabi uses modelbackend by default, but can be overridden here
# see: https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

# code used for additional user related operations
# see: https://docs.djangoproject.com/en/dev/ref/settings/#auth-profile-module
AUTH_PROFILE_MODULE = 'yabi.ModelBackendUserProfile'

# cookies
# see: https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
# see: https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
# you SHOULD change the cookie to use HTTPONLY and SECURE when in production
SESSION_COOKIE_AGE = 60 * 60
SESSION_COOKIE_PATH = url('/')
SESSION_COOKIE_NAME = 'yabi_sessionid'
#SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_NAME = "csrftoken_yabi"


# Locale
# see: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
#      https://docs.djangoproject.com/en/dev/ref/settings/#language-code
#      https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
USE_I18N = True

# see: https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = url('/login/')
LOGOUT_URL = url('/logout/')

### static file management ###
# see: https://docs.djangoproject.com/en/dev/howto/static-files/
# deployment uses an apache alias
# STATICFILES_DIRS = [os.path.join(WEBAPP_ROOT,"static")]
STATIC_URL = url('/static/')
STATIC_ROOT = os.path.join(WEBAPP_ROOT, 'static')
ADMIN_MEDIA_PREFIX = url('/static/admin/')

# media directories
# see: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(WEBAPP_ROOT, 'static', 'media')
MEDIA_URL = url('/static/media/')

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(WEBAPP_ROOT, 'scratch')
if not os.path.exists(WRITABLE_DIRECTORY):
    os.mkdir(WRITABLE_DIRECTORY)

# put our temporary uploads directory inside WRITABLE_DIRECTORY
FILE_UPLOAD_TEMP_DIR = os.path.join(WRITABLE_DIRECTORY, '.uploads')
if not os.path.exists(FILE_UPLOAD_TEMP_DIR):
    os.mkdir(FILE_UPLOAD_TEMP_DIR)

# see: https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

# validation settings, these reflect the types of backend that yabi can handle
EXEC_SCHEMES = ['ssh', 'ssh+pbspro', 'ssh+torque', 'ssh+sge', 'localex', 'null']
FS_SCHEMES = ['scp', 'sftp', 's3', 'localfs', 'null']
VALID_SCHEMES = EXEC_SCHEMES + FS_SCHEMES

##
## CAPTCHA settings
##
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the url base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')

# captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")


# see: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG

# see: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = [
    'django.template.loaders.app_directories.Loader',
    #'ccg.template.loaders.makoloader.filesystem.Loader',
    #'django.template.loaders.filesystem.Loader'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
# TEMPLATE_DIRS = [
#     os.path.join(WEBAPP_ROOT, "templates"),
#     os.path.join(WEBAPP_ROOT, "yabiadmin", "yabifeapp", "templates", "mako"),
#     os.path.join(WEBAPP_ROOT, "yabiadmin", "yabiengine", "templates", "mako"),
#     os.path.join(WEBAPP_ROOT, "yabiadmin", "yabi", "templates", "mako"),
#     os.path.join(WEBAPP_ROOT, "yabiadmin", "yabi", "templates"),
# ]

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, 'templates')

# mako module name
MAKO_MODULENAME_CALLABLE = ''

### USER SPECIFIC SETUP ###
# these are the settings you will most likely change to reflect your setup

# see: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'NAME': 'dev_yabi',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'},
    }
}

# Make this unique, and don't share it with anybody.
# see: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'set_this'

# email settings so yabi can send email error alerts etc
# see https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'set_this'
EMAIL_APP_NAME = "Yabi Admin "
SERVER_EMAIL = "apache@set_this"                      # from address
EMAIL_SUBJECT_PREFIX = "DEV "

# admins to email error reports to
# see: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ('alert', 'alerts@set_this.com')
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# if you want to use ldap you'll need to uncomment and configure this section
# you'll also need to change AUTHENTICATION_BACKENDS and AUTH_PROFILE_MODULE
#AUTH_LDAP_SERVER = ['ldaps://set_this.localdomain']
#AUTH_LDAP_USER_BASE = 'ou=People,dc=set_this,dc=edu,dc=au'
#AUTH_LDAP_GROUP_BASE = 'ou=Yabi,ou=Web Groups,dc=set_this,dc=edu,dc=au'
#AUTH_LDAP_GROUP = 'yabi'
#AUTH_LDAP_DEFAULT_GROUP = 'baseuser'
#AUTH_LDAP_GROUPOC = 'groupofuniquenames'
#AUTH_LDAP_USEROC = 'inetorgperson'
#AUTH_LDAP_MEMBERATTR = 'uniqueMember'
#AUTH_LDAP_USERDN = 'ou=People'

# set up caching. For production you should probably use memcached
# see https://docs.djangoproject.com/en/dev/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'yabi_cache',
        'TIMEOUT': 3600,
        'MAX_ENTRIES': 600
    }
}

# see https://docs.djangoproject.com/en/dev/ref/settings/#session-engine
# https://docs.djangoproject.com/en/1.3/ref/settings/#std:setting-SESSION_FILE_PATH
# in production we would suggest using memcached for your session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = WRITABLE_DIRECTORY

# uploads are currently written to disk and double handled, setting a limit will break things
# see https://docs.djangoproject.com/en/dev/ref/settings/#file-upload-max-memory-size
# this also ensures that files are always written to disk so we can access them via temporary_file_path
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

DEFAULT_STAGEIN_DIRNAME = 'stagein/'

# How long to cache decypted credentials for
DEFAULT_CRED_CACHE_TIME = 60 * 60 * 24                   # 1 day default


### CELERY ###
# see http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
djcelery.setup_loader()
# see http://docs.celeryproject.org/en/latest/getting-started/brokers/django.html
#BROKER_URL = 'django://'
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# http://celery.readthedocs.org/en/latest/whatsnew-3.1.html#last-version-to-enable-pickle-by-default
# Pickle is unsecure, but to ensure that we won't fail on existing messages
# we will do this upgrade in 2 steps. For now we make our messages json, but
# still accept 'pickle' to allow failing on existing messages or clearing all
# messages before the upgrade.
# TODO: in a next release drop 'pickle' from CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

# see http://docs.celeryproject.org/en/latest/configuration.html
CELERY_IGNORE_RESULT = True
# Not found in latest docs CELERY_QUEUE_NAME = 'yabiadmin'
# Deprecated alias CARROT_BACKEND = "django"
# Not found in latest docs CELERYD_LOG_LEVEL = "DEBUG"
CELERYD_CONCURRENCY = 4
CELERYD_PREFETCH_MULTIPLIER = 4
CELERY_DISABLE_RATE_LIMITS = True
# see http://docs.celeryproject.org/en/latest/configuration.html#id23
CELERY_SEND_EVENTS = True
CELERY_SEND_TASK_SENT_EVENT = True

# see http://docs.celeryproject.org/en/latest/userguide/routing.html
FILE_OPERATIONS = 'file_operations'

CELERY_QUEUES = (
    Queue('celery', routing_key='celery'),
    Queue(FILE_OPERATIONS, routing_key=FILE_OPERATIONS),
)

FILE_OPERATIONS_ROUTE = {
        'queue': FILE_OPERATIONS,
        'routing_key': FILE_OPERATIONS,
}

CELERY_ROUTES = {
    'yabiadmin.backend.celerytasks.stage_in_files': FILE_OPERATIONS_ROUTE,
    'yabiadmin.backend.celerytasks.stage_out_files': FILE_OPERATIONS_ROUTE,
}

CELERY_IMPORTS = ("yabiadmin.backend.celerytasks",)
CELERY_ACKS_LATE = True
# Not sure if this is still needed BROKER_TRANSPORT = "kombu.transport.django.Transport"

# Set this to 1000 or even higher on LIVE
CELERYD_MAX_TASKS_PER_CHILD = 100

### PREVIEW SETTINGS

# The truncate key controls whether the file may be previewed in truncated form
# (ie the first "size" bytes returned). If set to false, files beyond the size
# limit simply won't be available for preview.
#
# The override_mime_type key will set the content type that's sent in the
# response to the browser, replacing the content type received from Admin.
#
# MIME types not in this list will result in the preview being unavailable.
PREVIEW_SETTINGS = {
    # Text formats.
    "text/plain": {"truncate": True},

    # Structured markup formats.
    "text/html": {"truncate": False, "sanitise": True},
    "application/xhtml+xml": {"truncate": False, "sanitise": True},
    "text/svg+xml": {"truncate": True, "override_mime_type": "text/plain"},
    "text/xml": {"truncate": True, "override_mime_type": "text/plain"},
    "application/xml": {"truncate": True, "override_mime_type": "text/plain"},

    # Image formats.
    "image/gif": {"truncate": False},
    "image/jpeg": {"truncate": False},
    "image/png": {"truncate": False},
}

# The length of time preview metadata will be cached, in seconds.
PREVIEW_METADATA_EXPIRY = 60

# The maximum file size that can be previewed.
PREVIEW_SIZE_LIMIT = 1048576

# Used by djamboloader to combo load the YUI JS files
THIRTY_DAYS = 30 * 24 * 60 * 60
JAVASCRIPT_LIBRARIES = {
    "yui_3_5_1": {
        "path": os.path.join(WEBAPP_ROOT, "static/javascript/lib/yui-3.5.1/build/"),
        "cache_for": THIRTY_DAYS,
    },
    "yui2in3_2_9_0": {
        "path": os.path.join(WEBAPP_ROOT, "static/javascript/lib/yui-2in3/dist/2.9.0/build/"),
        "cache_for": THIRTY_DAYS,
    },
}

### LOGGING SETUP ###
# see https://docs.djangoproject.com/en/dev/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': 'YABI [%(name)s:%(levelname)s:%(asctime)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s'
        },
        'simple': {
            'format': 'YABI %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
        },

        'django': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',
        },

        'yabiadmin': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# qsub and qstat paths
SCHEDULER_COMMAND_PATHS = {
    "torque": {"qsub": "/opt/torque/2.3.13/bin/qsub",
               "qstat": "/opt/torque/2.3.13/bin/qstat",
               "qdel": "/opt/torque/2.3.13/bin/qdel"},
    "sge": {"qsub": "/opt/sge6/bin/linux-x64/qsub",
            "qstat": "/opt/sge6/bin/linux-x64/qstat",
            "qdel": "/opt/sge6/bin/linux-x64/qdel",
            "qacct": "/opt/sge6/bin/linux-x64/qacct"},
}


# Load instance settings.
# These are installed locally to this project instance.
# They will be loaded from appsettings.yabiadmin, which can exist anywhere
# in the instance's pythonpath. This allows private and local settings to be kept out
# of this file.
try:
    from appsettings.yabiadmin import *
except ImportError as e:
    pass
