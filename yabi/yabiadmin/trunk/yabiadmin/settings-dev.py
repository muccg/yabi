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
        'STORE_HOME': '/home/yabi/.yabi/run/store/',
    },
    'andrew': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '7001',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_HOME': '/home/yabi/.yabi/run/store/',
    },
    'aharvey': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '42080',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_HOME': '/home/yabi/.yabi/run/store/',
    },
    'cwellington': {
	    'BACKEND_IP': '0.0.0.0',
	    'BACKEND_PORT': '9001',
	    'BACKEND_BASE': '/',
	    'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_HOME': '/home/yabi/.yabi/run/store/',
    },
    'tszabo': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '19001',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_HOME': '/home/yabi/.yabi/run/store/',
    },
    'snapshot': {
        'BACKEND_IP': '0.0.0.0',
        'BACKEND_PORT': '21080',
        'BACKEND_BASE': '/',
        'YABI_URL': 'yabi://faramir.localdomain/',
        'STORE_HOME': '/home/yabi/.yabi/run/store/',
    },
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

DEFAULT_STAGEIN_DIRNAME = 'stagein/'

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

# TODO memcache session settings kill app
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHE_BACKEND = 'memcached://'+(';'.join(MEMCACHE_SERVERS))+"/"
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
VALID_SCHEMES = ['http', 'https', 'gridftp', 'globus', 'sge', 'torque', 'yabifs', 'ssh', 'scp', 's3', 'null', 'ssh+pbspro', 'ssh+qsub']

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

# kick off mango initialisation of logging
try:

    from django.contrib import logging as mangologging
except IOError, ioe:
    print "WARNING: inside settings.py I failed to import mangologging because I got the following exception"
    print ioe


##
## SENTRY
##

# Use sentry if we can, otherwise use EmailExceptionMiddleware
# sentry_test is set to true by snapshot deploy, so we can use sentry
# even though debug=True
try:
    assert DEBUG == False
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


# How long to cache decypted credentials for
DEFAULT_CRED_CACHE_TIME = 60*60*24                   # 1 day default
