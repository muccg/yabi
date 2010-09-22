# -*- coding: utf-8 -*-
# Django settings for project.
import os
from django.utils.webhelpers import url

# PROJECT_DIRECTORY isnt set when not under wsgi
if not os.environ.has_key('PROJECT_DIRECTORY'):
    os.environ['PROJECT_DIRECTORY']=os.path.dirname(__file__).split("/appsettings/")[0]

from appsettings.default_dev import *
from appsettings.yabife.dev import *

# Defaults
#LOGIN_REDIRECT_URL

# These are non standard
LOGIN_URL = url('/login/')
LOGOUT_URL = url('/logout/')

ROOT_URLCONF = 'yabife.urls'

INSTALLED_APPS.extend( [
    'yabife.yabifeapp',
    'djopenid.consumer'
] )

MEMCACHE_KEYSPACE = "dev-yabife-"

AUTHENTICATION_BACKENDS = [
 'djopenid.consumer.models.OpenIDBackend',
 'django.contrib.auth.backends.LDAPBackend',
 'django.contrib.auth.backends.NoAuthModelBackend',
]

SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_NAME = "csrftoken_yabife"

#PERSISTENT_FILESTORE = os.path.normpath(os.path.join(PROJECT_DIRECTORY, '..', '..', 'files'))

#Ensure the persistent storage dir exits. If it doesn't, exit noisily.
#assert os.path.exists(PERSISTENT_FILESTORE), "This application cannot start: It expects a writeable directory at %s to use as a persistent filestore" % (PERSISTENT_FILESTORE) 
# a directory that will be writable by the webserver, for storing various files...

WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

#functions to evaluate for status checking
#from status_checks import *
#STATUS_CHECKS = [check_default]

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

import logging
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.CRITICAL
LOGGING_FORMATTER = logging.Formatter('[%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
LOGS = ['yabife']

# Making this always point to the yabi users deployment
YABIADMIN_SERVER = "https://faramir.localdomain:22443"
YABIADMIN_BASE = "/"
#YABIADMIN_SERVER = os.environ["YABIADMIN_SERVER"] if "YABIADMIN_SERVER" in os.environ else "https://faramir.localdomain:443" 
#YABIADMIN_BASE = os.environ["YABIADMIN_BASE"] if "YABIADMIN_BASE" in os.environ else  "/yabiadmin/" + "<CCG_TARGET_NAME>" + "/"
