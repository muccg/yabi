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
from django.utils.webhelpers import url
import yabi_logging

### SERVER ###
if not os.environ.has_key('SCRIPT_NAME'):
    os.environ['SCRIPT_NAME']=''

SCRIPT_NAME =   os.environ['SCRIPT_NAME']
PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']


### PROJECT_DIRECTORY isnt set when not under wsgi
##if not os.environ.has_key('PROJECT_DIRECTORY'):
##    os.environ['PROJECT_DIRECTORY']=os.path.dirname(__file__).split("/appsettings/")[0]


# https
if SCRIPT_NAME:
    SSL_ENABLED = True
else:
    SSL_ENABLED = False


### DEBUG ###
DEBUG = True
DEV_SERVER = True
SITE_ID = 1


### APPLICATION
MIDDLEWARE_CLASSES = [
    'django.middleware.email.EmailExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.ssl.SSLRedirect',
    'django.contrib.messages.middleware.MessageMiddleware',
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'yabife.registration',
    'yabife.yabifeapp',
    ]

ROOT_URLCONF = 'yabife.urls'

AUTHENTICATION_BACKENDS = [
 'django.contrib.auth.backends.ModelBackend'
]

AUTH_PROFILE_MODULE = 'yabifeapp.ModelBackendUser'

# cookies
SESSION_COOKIE_AGE = 60*60
SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_yabife"

# Locale
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
USE_I18N = True

LOGIN_URL = url('/login/')
LOGOUT_URL = url('/logout/')

# for local development, this is set to the static serving directory. For deployment use Apache Alias
STATIC_SERVER_PATH = os.path.join(PROJECT_DIRECTORY,"static")

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

# media directories
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static","media")
MEDIA_URL = '/static/media/'
ADMIN_MEDIA_PREFIX = url('/static/admin-media/')

APPEND_SLASH = True
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

FILE_UPLOAD_MAX_MEMORY_SIZE = 0



### TEMPLATING ###
TEMPLATE_DEBUG = DEBUG

TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
]

TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIRECTORY,"templates","mako"), 
    os.path.join(PROJECT_DIRECTORY,"templates"),
]

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, "templates")

# mako module name
MAKO_MODULENAME_CALLABLE = ''



### USER SPECIFIC SETUP ###
# these are the settings you will most likely change to reflect your setup

# point this towards a database in the normal Django fashion
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'set_this',
        'NAME': 'set_this',
        'PASSWORD': 'set_this', 
        'HOST': 'set_this',                    
        'PORT': '',
    }
}

# Make this unique, and don't share it with anybody.
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


# if you want to use memcache, including for sessions, uncomment and configure
# memcache server list
#MEMCACHE_SERVERS = ['set_this.localdomain:11211']
#MEMCACHE_KEYSPACE = "yabife-"

# email server
EMAIL_HOST = 'set_this'
EMAIL_APP_NAME = "Yabi Admin "
SERVER_EMAIL = "apache@set_this"                      # from address
EMAIL_SUBJECT_PREFIX = "DEV "

# default emails
ADMINS = [
    ( 'alert', 'alerts@set_this.com' )
]
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





# Load instance settings.
# These are installed locally to this project instance.
# They will be loaded from appsettings.yabiadmin, which can exist anywhere
# in the instance's pythonpath. This is a CCG convention designed to support
# global shared settings among multiple Django projects.
try:
    from appsettings.yabife import *
except ImportError, e:
    pass
