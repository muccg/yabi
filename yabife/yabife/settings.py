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

import os
from ccg.utils.webhelpers import url
import logging
import logging.handlers


# these settings are used when running under WSGI
if not os.environ.has_key('SCRIPT_NAME'):
    os.environ['SCRIPT_NAME']=''
SCRIPT_NAME =   os.environ['SCRIPT_NAME']
PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']

# setting to control ssl middleware
if SCRIPT_NAME:
    SSL_ENABLED = True
else:
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
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.ssl.SSLRedirect',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',    
    'django.contrib.messages',
    'django_extensions',
    'south',
    'yabife.registration',
    'yabife.yabifeapp',
    ]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'yabife.urls'

# these determine which authentication method to use
# yabi uses modelbackend by default, but can be overridden here
# see: https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
 'django.contrib.auth.backends.ModelBackend'
]

# code used for additional user related operations
# see: https://docs.djangoproject.com/en/dev/ref/settings/#auth-profile-module
AUTH_PROFILE_MODULE = 'yabifeapp.ModelBackendUser'

# cookies
# see: https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
# see: https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
SESSION_COOKIE_AGE = 60*60
SESSION_COOKIE_PATH = url('/')
SESSION_COOKIE_NAME = 'yabife_sessionid'
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_yabife"


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
STATICFILES_DIRS = []
STATIC_ROOT = os.path.join(PROJECT_DIRECTORY,"static")
STATIC_URL = url('/static/')
ADMIN_MEDIA_PREFIX = url('/static/admin-media/')

# media directories
# see: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static","media")
MEDIA_URL = url('/static/media/')

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

# see: https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

# TODO: probably deprecated
SITE_NAME = 'yabife'

##
## CAPTCHA settings
##
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the URL base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')

# Captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")

# see: https://docs.djangoproject.com/en/dev/ref/settings/#file-upload-max-memory-size
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

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
        'NAME': 'yabife.sqlite3',
        'PASSWORD': '', 
        'HOST': '',                    
        'PORT': '',
    }
}

# Make this unique, and don't share it with anybody.
# see: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = 'set_this'

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


# memcache server list
# add a list of your memcache servers
MEMCACHE_SERVERS = ['localhost.localdomain:11211']
MEMCACHE_KEYSPACE = "yabife"

# file cookie persisting for connection between yabife and yabiadmin, this is not used if memcache is turned on
#FILE_COOKIE_DIR = WRITABLE_DIRECTORY
#FILE_COOKIE_NAME = 'yabife_cookie.txt'

# email settings so yabi can send email error alerts etc
# see https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'set_this'
EMAIL_APP_NAME = "Yabi Admin "
SERVER_EMAIL = "apache@set_this"
EMAIL_SUBJECT_PREFIX = "DEV "

# admins to email error reports to
# see: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ( 'alert', 'alerts@set_this.com' )
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS


#functions to evaluate for status checking
import status
STATUS_CHECKS = [
    status.check_database,
    status.check_disk,
]



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
    "text/plain": { "truncate": True },

    # Structured markup formats.
    "text/html": { "truncate": False, "sanitise": True },
    "application/xhtml+xml": { "truncate": False, "sanitise": True },
    "text/svg+xml": { "truncate": True, "override_mime_type": "text/plain" },
    "text/xml": { "truncate": True, "override_mime_type": "text/plain" },
    "application/xml": { "truncate": True, "override_mime_type": "text/plain" },

    # Image formats.
    "image/gif": { "truncate": False },
    "image/jpeg": { "truncate": False },
    "image/png": { "truncate": False },
}

# The length of time preview metadata will be cached, in seconds.
PREVIEW_METADATA_EXPIRY = 60

# The maximum file size that can be previewed.
PREVIEW_SIZE_LIMIT = 1048576

# the uri for your yabiadmin server. If you put this uri in a browser it should bring up the yabiadmin login page
YABIADMIN_SERVER = 'http://127.0.0.1:8001/'

# terms of service for the registration application
TERMS_OF_SERVICE = "Set your Terms of Service here, or import from another file"


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
        'yabife': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG'
        }
    }
}



# Load instance settings.
# These are installed locally to this project instance.
# They will be loaded from appsettings.yabiadmin, which can exist anywhere
# in the instance's pythonpath. This is a CCG convention designed to support
# global shared settings among multiple Django projects.
try:
    from appsettings.yabife import *
except ImportError, e:
    pass
