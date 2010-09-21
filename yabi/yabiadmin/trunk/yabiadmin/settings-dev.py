# -*- coding: utf-8 -*-
# Django settings for project.
import os
from django.utils.webhelpers import url

# PROJECT_DIRECTORY isnt set when not under wsgi
if not os.environ.has_key('PROJECT_DIRECTORY'):
    os.environ['PROJECT_DIRECTORY']=os.path.dirname(__file__).split("/appsettings/")[0]

from appsettings.default_dev import *
from appsettings.yabiadmin.dev import *

# Defaults
#LOGIN_REDIRECT_URL

# These are non standard
LOGIN_URL = url('/login/')
LOGOUT_URL = url('/logout/')

ROOT_URLCONF = 'yabiadmin.urls'

INSTALLED_APPS.extend( [
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'ghettoq'
] )

MEMCACHE_KEYSPACE = "dev-yabiadmin-"

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.LDAPBackend',
    'django.contrib.auth.backends.NoAuthModelBackend',
]

SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_yabiadmin"

#PERSISTENT_FILESTORE = os.path.normpath(os.path.join(PROJECT_DIRECTORY, '..', '..', 'files'))

#Ensure the persistent storage dir exits. If it doesn't, exit noisily.
#assert os.path.exists(PERSISTENT_FILESTORE), "This application cannot start: It expects a writeable directory at %s to use as a persistent filestore" % (PERSISTENT_FILESTORE) 
# a directory that will be writable by the webserver, for storing various files...

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

YABIBACKEND="faramir.localdomain:8000"

FILE_UPLOAD_MAX_MEMORY_SIZE = 0
YABIBACKEND_UPLOAD = 'http://'+YABIBACKEND+"fs/ticket"

##
## Validation settings
##
VALID_SCHEMES = ['http', 'https', 'gridftp', 'globus', 'sge', 'yabifs', 'ssh', 'scp', 's3', 'null']

import logging
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.CRITICAL
LOGGING_FORMATTER = logging.Formatter('[%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
LOGS = ['yabiadmin']

# Making this always point to the yabi users deployment
YABIBACKEND = os.environ["YABIBACKEND"] if "YABIBACKEND" in os.environ else "localhost.localdomain:8000/"
YABISTORE = os.environ["YABISTORE"] if "YABISTORE" in os.environ else "faramir.localdomain/yabistore/trunk"
YABI_URL = "yabi://localhost.localdomain/" # this is used in builder for pointers to previous jobs

YABIBACKEND_COPY = '/fs/copy'
YABIBACKEND_RCOPY = '/fs/rcopy'
YABIBACKEND_MKDIR = '/fs/mkdir'
YABIBACKEND_RM = '/fs/rm'
YABIBACKEND_LIST = '/fs/ls'
YABIBACKEND_PUT = '/fs/put'
YABIBACKEND_GET = '/fs/get'

##
## Celery settings
##
## http://ask.github.com/celery/tutorials/otherqueues.html
#CELERY_QUEUE_NAME = os.environ['CELERY_QUEUE_NAME'] if 'CELERY_QUEUE_NAME' in os.environ else 'default'
CELERY_QUEUE_NAME = 'yabiadmin-dev'

CARROT_BACKEND = "ghettoq.taproot.Database"
CELERYD_LOG_LEVEL = "DEBUG"
CELERYD_CONCURRENCY = 1
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_RESULT_BACKEND = "database"
CELERY_DISABLE_RATE_LIMITS = True
CELERY_QUEUES = {
    CELERY_QUEUE_NAME: {
        "binding_key": "celery",
        "exchange": CELERY_QUEUE_NAME
    },
}
CELERY_DEFAULT_QUEUE = CELERY_QUEUE_NAME
CELERY_DEFAULT_EXCHANGE = CELERY_QUEUE_NAME
CELERY_IGNORE_RESULT = True

print "CELERY_DEFAULT_QUEUE",CELERY_DEFAULT_QUEUE
print "CELERY_QUEUES",CELERY_QUEUES

