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
from django.utils.webhelpers import url
import djcelery
import yabilogging

### SERVER ###

# SCRIPT_NAME isnt set when not under wsgi
if not os.environ.has_key('SCRIPT_NAME'):
    os.environ['SCRIPT_NAME']=''

SCRIPT_NAME =   os.environ['SCRIPT_NAME']
PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']

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
    'django.middleware.ssl.SSLRedirect'
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'yabiadmin.yabistoreapp',
    'djcelery',
    'djkombu'
]

ROOT_URLCONF = 'yabiadmin.urls'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]
AUTH_PROFILE_MODULE = 'yabi.ModelBackendUserProfile'

# cookies
SESSION_COOKIE_AGE = 60*60
SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_yabiadmin"

# locale
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
USE_I18N = True

LOGIN_URL = url('/accounts/login/')
LOGOUT_URL = url('/accounts/logout/')

# for local development, this is set to the static serving directory. For deployment use Apache Alias
STATIC_SERVER_PATH = os.path.join(PROJECT_DIRECTORY,"static")

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

# media directories
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static","media")
MEDIA_URL = '/static/media/'
ADMIN_MEDIA_PREFIX = url('/static/admin-media/')

APPEND_SLASH = True
SITE_NAME = 'yabiadmin'

# validation settings
VALID_SCHEMES = ['http', 'https', 'gridftp', 'globus', 'sge', 'torque', 'yabifs', 'ssh', 'scp', 's3', 'null', 'ssh+pbspro', 'ssh+torque', 'localfs', 'localex']



### CAPTCHA ###

# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the url base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')

# captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")


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
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'NAME': 'yabiadmin.sqlite3',
        'PASSWORD': '', 
        'HOST': '',                    
        'PORT': '',
    }
}

# Make these unique, and don't share it with anybody.
SECRET_KEY = 'set_this'
HMAC_KEY = 'set_this'

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
MEMCACHE_SERVERS = ['localhost.localdomain:11211']
MEMCACHE_KEYSPACE = "yabiadmin"

# uncomment to use memcache for sessions, be sure to have uncommented memcache settings above
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHE_BACKEND = 'memcached://'+(';'.join(MEMCACHE_SERVERS))+"/"
MEMCACHE_KEYSPACE = "yabiadmin"

# uploads are currently written to disk and double handled, setting a limit will break things 
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






# Load instance settings.
# These are installed locally to this project instance.
# They will be loaded from appsettings.yabiadmin, which can exist anywhere
# in the instance's pythonpath. This is a CCG convention designed to support
# global shared settings among multiple Django projects.
try:
    from appsettings.yabiadmin import *
except ImportError, e:
    pass
