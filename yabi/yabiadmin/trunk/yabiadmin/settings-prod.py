# -*- coding: utf-8 -*-
# Django settings for project.
import os, sys
from django.utils.webhelpers import url

from appsettings.default_prod import *
from appsettings.yabiadmin.prod import *

# subsitution done by fab, this will be your username or in the case of a snapshot, 'snapshot'
TARGET = 'live'

# TARGET is used to index into this hash, edit your own settings at will
BACKEND = {
    'live': {
        'BACKEND_IP': '192.168.1.96',
        'BACKEND_PORT': '9001',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://yabi.localdomain/',
        'STORE_HOME': '/usr/local/python/ccgapps/yabiadmin/store/'
    }
}

# uploads are currently written to disk and double handled, setting a limit will break things 
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

BACKEND_IP = BACKEND[TARGET]['BACKEND_IP']
BACKEND_PORT = BACKEND[TARGET]['BACKEND_PORT']
BACKEND_BASE = BACKEND[TARGET]['BACKEND_BASE']
YABIBACKEND_SERVER = BACKEND_IP + ':' +  BACKEND_PORT
YABISTORE_HOME = BACKEND[TARGET]['STORE_HOME']

# this is used in builder for pointers to previous jobs
YABI_URL = BACKEND[TARGET]['YABI_URL']
BACKEND_UPLOAD = 'http://'+BACKEND_IP+':'+BACKEND_PORT+BACKEND_BASE+"fs/ticket"

YABIBACKEND_COPY = '/fs/copy'
YABIBACKEND_RCOPY = '/fs/rcopy'
YABIBACKEND_MKDIR = '/fs/mkdir'
YABIBACKEND_RM = '/fs/rm'
YABIBACKEND_LIST = '/fs/ls'
YABIBACKEND_PUT = '/fs/put'
YABIBACKEND_GET = '/fs/get'

ROOT_URLCONF = 'yabiadmin.urls'

INSTALLED_APPS.extend( [
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'yabiadmin.yabistoreapp',
    'ghettoq',
    'djcelery'
] )

# TODO memcache session settings kill app
#SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
#CACHE_BACKEND = 'memcache'
MEMCACHE_KEYSPACE = "yabiadmin-"+TARGET

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.LDAPBackend',
    'django.contrib.auth.backends.NoAuthModelBackend',
]

SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_yabiadmin"

WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

#functions to evaluate for status checking
#from status_checks import *
#STATUS_CHECKS = [check_default]

APPEND_SLASH = True
SITE_NAME = 'yabiadmin'

##
## CAPTCHA settings
##
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the URL base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')

# Captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")

##
## Validation settings
##
VALID_SCHEMES = ['http', 'https', 'gridftp', 'globus', 'sge', 'yabifs', 'ssh', 'scp', 's3', 'null']

##
## Celery settings
##
import djcelery
djcelery.setup_loader()

CELERY_IGNORE_RESULT = True
CELERY_QUEUE_NAME = 'yabiadmin-'+TARGET
CARROT_BACKEND = "ghettoq.taproot.Database"
CELERYD_LOG_LEVEL = "WARNING"
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


##
## LOGGING
##
import logging
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.WARNING
LOGGING_FORMATTER = logging.Formatter('[%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
LOGS = ['yabiengine','yabiadmin']

# kick off mango initialisation of logging
from django.contrib import logging as mangologging
