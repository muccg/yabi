# -*- coding: utf-8 -*-
# Django settings for project.
import os, sys
from django.utils.webhelpers import url

#TODO
# A log file is created but very little is written to it, stack traces are going to the apache logs
# Session is in db, move to memcache
# favicon filling logs with 404

from appsettings.default_dev import *
from appsettings.yabiadmin.dev import *

# subsitution done by fab, this will be your username or in the case of a snapshot, 'snapshot'
TARGET = '<CCG_TARGET_NAME>'

# The various
# TARGET is used to index into this hash, edit your own settings at will
BACKEND = {
    'ahunter': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '50080',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_SERVER': 'localhost:40080',
        'STORE_BASE': '/yabistore'
    },
    'andrew': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '7001',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_SERVER': 'localhost:7003',
        'STORE_BASE': '/yabistore'
    },
    'aharvey': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '42080',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_SERVER': 'localhost:43080',
        'STORE_BASE': '/yabistore'
    },
    'cwellington': {
	'BACKEND_IP': '0.0.0.0',
	'BACKEND_PORT': '9001',
	'BACKEND_BASE': '/',
	'YABI_URL': 'yabi://faramir.localdomain/',
	'STORE_SERVER': 'localhost:9003',
	'STORE_BASE': '/yabistore',
    },
    'snapshot': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '21080',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_SERVER': 'localhost:23080',
        'STORE_BASE': '/yabistore'
    },
}

# uploads are currently written to disk and double handled, setting a limit will break things 
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

BACKEND_IP = BACKEND[TARGET]['BACKEND_IP']
BACKEND_PORT = BACKEND[TARGET]['BACKEND_PORT']
BACKEND_BASE = BACKEND[TARGET]['BACKEND_BASE']
YABIBACKEND_SERVER = BACKEND_IP + ':' +  BACKEND_PORT
YABISTORE_SERVER = BACKEND[TARGET]['STORE_SERVER']
YABISTORE_BASE = BACKEND[TARGET]['STORE_BASE']
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

if "LOCALDEV" in os.environ:
    SSL_ENABLED = False
    os.environ['PROJECT_DIRECTORY'] = 'TODO'
    assert 'TODO localdev testing'

ROOT_URLCONF = 'yabiadmin.urls'

INSTALLED_APPS.extend( [
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'yabiadmin.yabistoreapp',
    'ghettoq',
    'djcelery'
] )

MEMCACHE_KEYSPACE = "dev-yabiadmin-"+TARGET

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
CELERY_QUEUE_NAME = 'yabiadmin-dev-'+TARGET
CARROT_BACKEND = "ghettoq.taproot.Database"
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


##
## LOGGING
##
import logging
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMATTER = logging.Formatter('[%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
LOGS = ['yabiengine','yabiadmin']


##
## SENTRY
##

# Use sentry if we can, otherwise use EmailExceptionMiddleware
# sentry_test is set to true by snapshot deploy, so we can use sentry
# even though debug=True
try:
    assert DEBUG != True
    SENTRY_REMOTE_URL = 'http://faramir.localdomain/sentryserver/%s/store/' % TARGET
    SENTRY_KEY = 'lrHEULXanJMB5zygOLUUcCRvCxYrcWVZJZ0fzsMzx'
    SENTRY_TESTING = False

    INSTALLED_APPS.extend(['sentry.client'])
    
    from sentry.client.handlers import SentryHandler
    logging.getLogger().addHandler(SentryHandler())

    # Add StreamHandler to sentry's default so you can catch missed exceptions
    logging.getLogger('sentry.errors').addHandler(logging.StreamHandler())

    # remove the EmailExceptionMiddleware so
    # exceptions are handled and mailed by sentry
    try:
        MIDDLEWARE_CLASSES.remove('django.middleware.email.EmailExceptionMiddleware')
    except ValueError,e:
        pass

except (ImportError, AssertionError), e:
    pass
