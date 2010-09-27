# -*- coding: utf-8 -*-
# Django settings for project.
import os
from django.utils.webhelpers import url

#TODO
# May need to point to a users deployment rather than yabi user??
# File does not exist: /usr/local/python/ccgapps/yabiadmin/ahunter/yabiadmin/static/admin-media/js/jquery.min.js, referer: https://faramir.localdomain/yabiadmin/ahunter/admin/yabi/toolset/
# A log file is created but very little is written to it, stack traces are going to the apache logs

# PROJECT_DIRECTORY isnt set when not under wsgi
# TODO Is this still valid? Asserting
assert os.environ.has_key('PROJECT_DIRECTORY')
if not os.environ.has_key('PROJECT_DIRECTORY'):
    os.environ['PROJECT_DIRECTORY']=os.path.dirname(__file__).split("/appsettings/")[0]

from appsettings.default_dev import *
from appsettings.yabiadmin.dev import *

# THIS SHOULD NOT BE IN SVN
# TODO update dev_yabi schema
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'yabminapp',
        'NAME': 'dev_yabi_ahunter',
        'PASSWORD': 'yabminapp',
        'HOST': 'eowyn.localdomain',
        'PORT': '',
    }
}

# uploads are currently written to disk and double handled, setting a limit will break things 
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

# TODO Make this per user
BACKEND_IP = os.environ["BACKEND_IP"] if "BACKEND_IP" in os.environ else "0.0.0.0"
BACKEND_PORT = os.environ["BACKEND_PORT"] if "BACKEND_PORT" in os.environ else "50080"
BACKEND_BASE = os.environ["BACKEND_BASE"] if "BACKEND_BASE" in os.environ else "/"
BACKEND_UPLOAD = 'http://'+BACKEND_IP+':'+BACKEND_PORT+BACKEND_BASE+"fs/ticket"
# this is used in builder for pointers to previous jobs
YABI_URL = os.environ["YABI_URL"] if "YABI_URL" in os.environ else "yabi://faramir.localdomain/" 

YABIBACKEND_COPY = '/fs/copy'
YABIBACKEND_RCOPY = '/fs/rcopy'
YABIBACKEND_MKDIR = '/fs/mkdir'
YABIBACKEND_RM = '/fs/rm'
YABIBACKEND_LIST = '/fs/ls'
YABIBACKEND_PUT = '/fs/put'
YABIBACKEND_GET = '/fs/get'

SSL_FORCE = True
if "LOCALDEV" in os.environ:
    SSL_ENABLED = False

ROOT_URLCONF = 'yabiadmin.urls'

INSTALLED_APPS.extend( [
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'ghettoq',
    'djcelery'
] )

MEMCACHE_KEYSPACE = "dev-yabiadmin-<CCG_TARGET_NAME>"

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

import logging
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.CRITICAL
LOGGING_FORMATTER = logging.Formatter('[%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
LOGS = ['yabiengine','yabiadmin']

##
## Celery settings
##
import djcelery
djcelery.setup_loader()

CELERY_IGNORE_RESULT = True
CELERY_QUEUE_NAME = 'yabiadmin-dev-<CCG_TARGET_NAME>'
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
