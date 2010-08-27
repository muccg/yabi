# -*- coding: utf-8 -*-
# Django settings for yabife project.
import os

if not os.environ.has_key('PROJECT_DIRECTORY'):
	os.environ['PROJECT_DIRECTORY']=os.path.dirname(__file__)
if not os.environ.has_key('SCRIPT_NAME'):								# this will be missing if we are running on the internal server
	os.environ['SCRIPT_NAME']=''
PROJECT_DIRECTORY = os.environ['PROJECT_DIRECTORY']
SCRIPT_NAME = os.environ['SCRIPT_NAME']

from django.utils.webhelpers import url

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# shortcut for overiding variables with environment settings
def environ_or(key,default):
    return os.environ[key] if key in os.environ else default

# make sure that this is a tuple of tuples
ADMINS = (
    (environ_or('ADMIN_EMAIL_NAME','Tech Alerts'), environ_or('ADMIN_EMAIL','alerts@ccg.murdoch.edu.au')),
)

MANAGERS = ADMINS

LOGIN_URL = url("/login")

#
# if we are deploying a DJANGODEV development version, we can override settings with environment variables
#
YABIADMIN = os.environ["YABIADMIN"] if "YABIADMIN" in os.environ else "faramir.localdomain/yabiadmin/trunk"
YABISTORE = os.environ["YABISTORE"] if "YABISTORE" in os.environ else "faramir.localdomain/yabistore/trunk"

# development deployment
if "DJANGODEV" in os.environ:
    DEBUG = True if os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug")) else ("DJANGODEBUG" in os.environ)
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'dev_yabife'                 # Or path to database file if using sqlite3.
    DATABASE_USER = 'yabifeapp'                       # Not used with sqlite3.
    DATABASE_PASSWORD = 'yabifeapp'                   # Not used with sqlite3.
    DATABASE_HOST = 'eowyn.localdomain'               # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''                                # Set to empty string for default. Not used with sqlite3.
    YABIADMIN_SERVER, YABIADMIN_BASE = YABIADMIN.split('/',1)
    YABIADMIN_BASE = "/" + YABIADMIN_BASE
    YABISTORE_SERVER, YABISTORE_BASE = YABISTORE.split('/',1)
    YABISTORE_BASE = "/" + YABISTORE_BASE
    SSL_ENABLED = False
    DEV_SERVER = True

    AUTH_LDAP_SERVER = ('ldaps://fdsdev.localdomain',)
    AUTH_LDAP_USER_BASE = 'ou=People,dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_GROUP_BASE = 'ou=Yabi,ou=Web Groups,dc=ccg,dc=murdoch,dc=edu,dc=au'
    AUTH_LDAP_GROUP = 'yabi'
    DEFAULT_GROUP = "baseuser"
    
    # debug site table
    SITE_ID = 1
    
# production deployment. These must come from the yabi.conf file.
else:
    DEBUG = True if os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug")) else ("DJANGODEBUG" in os.environ)
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = os.environ['DATABASE_ENGINE']
    DATABASE_NAME = os.environ['DATABASE_NAME']
    DATABASE_USER = os.environ['DATABASE_USER']
    DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
    DATABASE_HOST = os.environ['DATABASE_HOST']
    DATABASE_PORT = os.environ['DATABASE_PORT']
    
    YABIADMIN_SERVER, YABIADMIN_BASE = YABIADMIN.split('/',1)
    YABIADMIN_BASE = "/" + YABIADMIN_BASE
    YABISTORE_SERVER, YABISTORE_BASE = YABISTORE.split('/',1)
    YABISTORE_BASE = "/" + YABISTORE_BASE

    AUTH_LDAP_SERVER = tuple(os.environ['AUTH_LDAP_SERVER'].split()) if 'AUTH_LDAP_SERVER' in os.environ else              ('ldaps://fdsdev.localdomain',)
    AUTH_LDAP_USER_BASE = environ_or('AUTH_LDAP_USER_BASE', 'ou=People,dc=ccg,dc=murdoch,dc=edu,dc=au')
    AUTH_LDAP_GROUP_BASE = environ_or('AUTH_LDAP_GROUP_BASE', 'ou=Yabi,ou=Web Groups,dc=ccg,dc=murdoch,dc=edu,dc=au')
    AUTH_LDAP_GROUP = environ_or('AUTH_LDAP_GROUP', 'yabi')
    DEFAULT_GROUP = environ_or('AUTH_LDAP_DEFAULT_GROUP', "baseuser")

    SSL_ENABLED = os.environ['SSL_ENABLED'] if 'SSL_ENABLED' in os.environ else True
    DEV_SERVER = False
    
    # development site id
    SITE_ID = 1



print "YABISTORE_SERVER =",YABISTORE_SERVER
print "YABISTORE_BASE =",YABISTORE_BASE
print "YABIADMIN_SERVER =",YABIADMIN_SERVER
print "YABIADMIN_BASE =",YABIADMIN_BASE

for key in [ 'DATABASE_ENGINE','DATABASE_NAME','DATABASE_USER','DATABASE_PASSWORD','DATABASE_HOST','DATABASE_PORT','AUTH_LDAP_SERVER','AUTH_LDAP_USER_BASE','AUTH_LDAP_GROUP_BASE','AUTH_LDAP_GROUP','DEFAULT_GROUP' ]:
    print key, locals()[key]


# email server
EMAIL_HOST = 'ccg.murdoch.edu.au'
EMAIL_APP_NAME = "Yabi Front End"
SERVER_EMAIL = "apache@ccg.murdoch.edu.au"
EMAIL_SUBJECT_PREFIX = "Yabi Frontend %s %s:"%("DEBUG" if DEBUG else "","DEV_SERVER" if DEV_SERVER else "")



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Australia/Perth'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIRECTORY,"static","media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/static/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = url('/static/admin-media/')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n(=cff+h#-^+isd*%(zw*30^^o#19-+vq&83gycv*os1)09$(7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.email.EmailExceptionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.middleware.doc.XViewMiddleware',
    'django.middleware.ssl.SSLRedirect'
)

# our session cookie name (set to be different to admin)
SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = True

ROOT_URLCONF = 'yabife.urls'

TEMPLATE_DIRS = (
   # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
   # Always use forward slashes, even on Windows.
   # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIRECTORY,"templates","mako"),
    os.path.join(PROJECT_DIRECTORY,"djopenid","templates"),

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'yabife.yabifeapp',
    'djopenid.consumer'
)

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"scratch")

# Captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")

##
## Mako settings stuff
##

# extra mako temlate directories
MAKO_TEMPLATE_DIRS = ( os.path.join(PROJECT_DIRECTORY,"templates","mako"), )

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, "templates")

# mako module name
MAKO_MODULENAME_CALLABLE = ''

##
## memcache server list
##
MEMCACHE_SERVERS = os.environ['MEMCACHE_SERVERS'].split()
MEMCACHE_KEYSPACE = "%s-%s"%(os.environ['MEMCACHE_PREFIX'],YABIADMIN_SERVER)


##
## CAPTCHA settings
##
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the URL base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')

AUTHENTICATION_BACKENDS = (
    'djopenid.consumer.models.OpenIDBackend',
    'django.contrib.auth.backends.LDAPBackend',
    'django.contrib.auth.backends.NoAuthModelBackend',
)

# for local development, this is set to the static serving directory. For deployment use Apache Alias
STATIC_SERVER_PATH = os.path.join(PROJECT_DIRECTORY,"static")


##
## Logging setup
##
import logging
LOG_DIRECTORY = os.path.join(PROJECT_DIRECTORY,"logs")
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.CRITICAL
LOGGING_FORMATTER = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s:%(message)s")
LOGS = ['yabife']

# TODO not using mango logging for now, can't add extra handlers to that
from sys import stdout
from logging.handlers import TimedRotatingFileHandler

for logfile in LOGS:
    logger = logging.getLogger(logfile)
    logger.setLevel(LOGGING_LEVEL)
    sh = logging.StreamHandler(stdout)
    sh.setLevel(LOGGING_LEVEL)
    sh.setFormatter(LOGGING_FORMATTER)
    logger.addHandler(sh)
    logfilename = "%s%s" % (logfile, ".log")
    fh = TimedRotatingFileHandler(os.path.join(LOG_DIRECTORY, logfilename), 'midnight')
    fh.setFormatter(LOGGING_FORMATTER)
    fh.setLevel(LOGGING_LEVEL)
    logger.addHandler(fh)


# TODO the file upload only handles files that are written to disk at them moment
# so this MUST be set to 0
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

if 'HTTP_REDIRECT_TO_HTTPS' in os.environ:
    HTTP_REDIRECT_TO_HTTPS = os.environ['HTTP_REDIRECT_TO_HTTPS']
if 'HTTP_REDIRECT_TO_HTTPS_PORT' in os.environ:
    HTTP_REDIRECT_TO_HTTPS_PORT = os.environ['HTTP_REDIRECT_TO_HTTPS_PORT']

