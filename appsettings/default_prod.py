# -*- coding: utf-8 -*-
"""
Django settings import defaults for production server
"""
import os
from django.utils.webhelpers import url

# PROJECT_DIRECTORY is set when under wsgi
assert os.environ.has_key('PROJECT_DIRECTORY')

# SCRIPT_NAME isnt set when not under wsgi
if not os.environ.has_key('SCRIPT_NAME'):
    os.environ['SCRIPT_NAME']=''

SCRIPT_NAME =   os.environ['SCRIPT_NAME']
PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']

DEBUG = False
DEV_SERVER = False
SITE_ID = 1

# default emails
ADMINS = [
    ( 'Tech Alerts', 'alerts@set_this_please.com' )
]
MANAGERS = ADMINS

# https
if SCRIPT_NAME:
    SSL_ENABLED = True
else:
    SSL_ENABLED = False

# Locale
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
USE_I18N = True

LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY, 'logs')
TEMPLATE_DEBUG = DEBUG

LOGIN_URL = url('/accounts/login/')
LOGOUT_URL = url('/accounts/logout/')

##
## Django Core stuff
##
TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
]
MIDDLEWARE_CLASSES = [
    'django.middleware.email.EmailExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.ssl.SSLRedirect'
]
TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIRECTORY,"templates","mako"), 
    os.path.join(PROJECT_DIRECTORY,"templates"),
]
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
]

# for local development, this is set to the static serving directory. For deployment use Apache Alias
STATIC_SERVER_PATH = os.path.join(PROJECT_DIRECTORY,"static")

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

##
## Mako settings stuff
##

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, "templates")

# mako module name
MAKO_MODULENAME_CALLABLE = ''

# cookies
SESSION_COOKIE_AGE = 60*60

MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static","media")
MEDIA_URL = '/static/media/'
ADMIN_MEDIA_PREFIX = url('/static/admin-media/')
