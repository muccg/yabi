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

ADMINS = (
    ('Tech Alerts', 'alerts@ccg.murdoch.edu.au')
)

MANAGERS = ADMINS

LOGIN_URL = "/login"

# development deployment
if "DJANGODEV" in os.environ:
    DEBUG = True if os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug")) else ("DJANGODEBUG" in os.environ)
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'dev_yabi_yabife'                 # Or path to database file if using sqlite3.
    DATABASE_USER = 'yabifeapp'                       # Not used with sqlite3.
    DATABASE_PASSWORD = 'yabifeapp'                   # Not used with sqlite3.
    DATABASE_HOST = 'eowyn.localdomain'               # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''                                # Set to empty string for default. Not used with sqlite3.
    YABIADMIN_SERVER = "127.0.0.1:8001"
    SSL_ENABLED = False
    DEV_SERVER = True
    
    # debug site table
    SITE_ID = 1
    
# production deployment (probably using wsgi)
else:
    DEBUG = os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug"))
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
    DATABASE_NAME = 'live_yabi_yabife'                # Or path to database file if using sqlite3.
    DATABASE_USER = 'yabifeapp'                       # Not used with sqlite3.
    DATABASE_PASSWORD = 'yabifeapp'                   # Not used with sqlite3.
    DATABASE_HOST = 'iridium.localdomain'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
    YABIADMIN_SERVER = "127.0.0.1:8001"
    SSL_ENABLED = True
    DEV_SERVER = False
    
    # development site id
    SITE_ID = 1

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

ROOT_URLCONF = 'yabife.urls'

TEMPLATE_DIRS = (
   # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
   # Always use forward slashes, even on Windows.
   # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIRECTORY,"templates","mako"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'yabife.yabifeapp'
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
MEMCACHE_SERVERS = ['memcache1.localdomain:11211','memcache2.localdomain:11211']
MEMCACHE_KEYSPACE = ""

##
## CAPTCHA settings
##
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the URL base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')


##
## Auth settings
##
AUTH_LDAP_SERVER = 'ldaps://fds2.localdomain'
AUTH_LDAP_BASE = 'ou=People,dc=ccg,dc=murdoch,dc=edu,dc=au'
AUTH_LDAP_GROUP_BASE = 'ou=Yabi,ou=Web Groups,dc=ccg,dc=murdoch,dc=edu,dc=au'
AUTH_LDAP_GROUP = 'yabi'
DEFAULT_GROUP = "baseuser"


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.LDAPBackend',
#    'django.contrib.auth.backends.ModelBackend',
)

# for local development, this is set to the static serving directory. For deployment use Apache Alias
STATIC_SERVER_PATH = os.path.join(PROJECT_DIRECTORY,"static")
