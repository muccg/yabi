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
import logging
import logging.handlers

PROJECT_DIRECTORY = os.environ.get('PROJECT_DIRECTORY', os.path.abspath('.'))

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
    'ccg.middleware.ssl.SSLRedirect'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'yabiadmin.yabistoreapp',
    'djcelery',
    'djkombu',
    'django_extensions',
    'south'    
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
SESSION_COOKIE_AGE = 60*60
SESSION_COOKIE_PATH = url('/')
SESSION_COOKIE_NAME = 'yabiadmin_sessionid'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = False 
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_NAME = "csrftoken_yabiadmin"


# Locale
# see: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
#      https://docs.djangoproject.com/en/dev/ref/settings/#language-code
#      https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
USE_I18N = True

# see: https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = url('/accounts/login/')
LOGOUT_URL = url('/accounts/logout/')


### static file management ###
# see: https://docs.djangoproject.com/en/dev/howto/static-files/
# deployment uses an apache alias
STATICFILES_DIRS = [os.path.join(PROJECT_DIRECTORY,"static")]
STATIC_URL = url('/static/')
ADMIN_MEDIA_PREFIX = url('/static/admin/')

# media directories
# see: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static","media")
MEDIA_URL = url('/static/media/')

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

# see: https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

# TODO: probably deprecated
SITE_NAME = 'yabiadmin'

# validation settings, these reflect the types of backend that yabi can handle
EXEC_SCHEMES = ['globus', 'sge', 'torque', 'ssh', 'ssh+pbspro', 'ssh+torque', 'ssh+sge', 'localex','explode','null']
FS_SCHEMES = ['http', 'https', 'gridftp', 'yabifs', 'scp', 's3', 'localfs','null']
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
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'ccg.template.loaders.makoloader.filesystem.Loader'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIRECTORY,"templates"),
]

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, "templates")

# mako module name
MAKO_MODULENAME_CALLABLE = ''




### USER SPECIFIC SETUP ###
# these are the settings you will most likely change to reflect your setup

# see: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'NAME': 'yabiadmin.sqlite3',
        'PASSWORD': '', 
        'HOST': '',                    
        'PORT': '',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Make this unique, and don't share it with anybody.
# see: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'set_this'
HMAC_KEY = 'set_this'

# email settings so yabi can send email error alerts etc
# see https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'set_this'
EMAIL_APP_NAME = "Yabi Admin "
SERVER_EMAIL = "apache@set_this"                      # from address
EMAIL_SUBJECT_PREFIX = "DEV "

# admins to email error reports to
# see: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ( 'alert', 'alerts@set_this.com' )
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


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost.localdomain:11211',
        'KEYSPACE': "yabiadmin"
    }
}

# uncomment to use memcache for sessions, be sure to have uncommented memcache settings above
# see https://docs.djangoproject.com/en/dev/ref/settings/#session-engine
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# uploads are currently written to disk and double handled, setting a limit will break things
# see https://docs.djangoproject.com/en/dev/ref/settings/#file-upload-max-memory-size
# this also ensures that files are always written to disk so we can access them via temporary_file_path
FILE_UPLOAD_MAX_MEMORY_SIZE = 0


### BACKEND ###
# point this to the yabi backend server
BACKEND_IP = '0.0.0.0'
BACKEND_PORT = '9001'
BACKEND_BASE = '/'
TASKTAG = 'set_this' # this must be the same in the yabi.conf for the backend that will consume tasks from this admin
YABIBACKEND_SERVER = BACKEND_IP + ':' +  BACKEND_PORT
YABISTORE_HOME = '.yabi/run/store/'
BACKEND_UPLOAD = 'http://'+BACKEND_IP+':'+BACKEND_PORT+BACKEND_BASE+"fs/ticket"

YABIBACKEND_COPY = '/fs/copy'
YABIBACKEND_RCOPY = '/fs/rcopy'
YABIBACKEND_MKDIR = '/fs/mkdir'
YABIBACKEND_RM = '/fs/rm'
YABIBACKEND_LIST = '/fs/ls'
YABIBACKEND_PUT = '/fs/put'
YABIBACKEND_GET = '/fs/get'

DEFAULT_STAGEIN_DIRNAME = 'stagein/'

# How long to cache decypted credentials for
DEFAULT_CRED_CACHE_TIME = 60*60*24                   # 1 day default


### CELERY ###
djcelery.setup_loader()

CELERY_IGNORE_RESULT = True
CELERY_QUEUE_NAME = 'yabiadmin'
CARROT_BACKEND = "django"
CELERYD_LOG_LEVEL = "DEBUG"
CELERYD_CONCURRENCY = 1
CELERYD_PREFETCH_MULTIPLIER = 1
#CELERY_DISABLE_RATE_LIMITS = True
CELERY_QUEUES = {
    CELERY_QUEUE_NAME: {
        "binding_key": "celery",
        "exchange": CELERY_QUEUE_NAME
    },
}
CELERY_DEFAULT_QUEUE = CELERY_QUEUE_NAME
CELERY_DEFAULT_EXCHANGE = CELERY_QUEUE_NAME
CELERY_IMPORTS = ("yabiadmin.yabiengine.tasks",)
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"


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
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter':'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'yabiadmin': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG'
        }
    }
}




# Load instance settings.
# These are installed locally to this project instance.
# They will be loaded from appsettings.yabiadmin, which can exist anywhere
# in the instance's pythonpath. This allows private and local settings to be kept out
# of this file.
try:
    from appsettings.yabiadmin import *
except ImportError, e:
    pass
