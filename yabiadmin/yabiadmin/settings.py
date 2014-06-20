# -*- coding: utf-8 -*-
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

import os
from ccg_django_utils.webhelpers import url
from ccg_django_utils.conf import EnvConfig

from kombu import Queue

env = EnvConfig()

WEBAPP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRODUCTION = env.get("production", False)

# setting to control ccg ssl middleware
# see http://code.google.com/p/ccg-django-extras/source/browse/
# you SHOULD change the SSL_ENABLED to True when in production
SSL_ENABLED = PRODUCTION

# set debug, see: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = not PRODUCTION

# see: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# see: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'ccg_django_utils.middleware.ssl.SSLRedirect',
    'django.contrib.messages.middleware.MessageMiddleware'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'yabiadmin.yabifeapp',
    'yabiadmin.yabi',
    'yabiadmin.yabiengine',
    'kombu.transport.django',
    'django_extensions',
    'south',
    'djamboloader',
    'django.contrib.admin'
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'yabiadmin.urls'

# cookies
# see: https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
# see: https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
# you SHOULD change the cookie to use HTTPONLY and SECURE when in production
SESSION_COOKIE_AGE = 60 * 60
SESSION_COOKIE_PATH = url('/')
SESSION_COOKIE_NAME = 'yabi_sessionid'
# SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = PRODUCTION
CSRF_COOKIE_NAME = "csrftoken_yabi"
CSRF_COOKIE_SECURE = PRODUCTION

# Locale
# see: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
#      https://docs.djangoproject.com/en/dev/ref/settings/#language-code
#      https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
TIME_ZONE = 'Australia/Perth'
LANGUAGE_CODE = 'en-us'
USE_I18N = True

# see: https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = url('/login/')
LOGOUT_URL = url('/logout/')

# ## static file management ###
# see: https://docs.djangoproject.com/en/dev/howto/static-files/
# deployment uses an apache alias
# STATICFILES_DIRS = [os.path.join(WEBAPP_ROOT,"static")]
STATIC_URL = url('/static/')
STATIC_ROOT = os.path.join(WEBAPP_ROOT, 'static')
ADMIN_MEDIA_PREFIX = url('/static/admin/')

# media directories
# see: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(WEBAPP_ROOT, 'static', 'media')
MEDIA_URL = url('/static/media/')

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = os.path.join(WEBAPP_ROOT, 'scratch')
if not os.path.exists(WRITABLE_DIRECTORY):
    os.mkdir(WRITABLE_DIRECTORY)

# put our temporary uploads directory inside WRITABLE_DIRECTORY
FILE_UPLOAD_TEMP_DIR = os.path.join(WRITABLE_DIRECTORY, '.uploads')
if not os.path.exists(FILE_UPLOAD_TEMP_DIR):
    os.mkdir(FILE_UPLOAD_TEMP_DIR)

# see: https://docs.djangoproject.com/en/dev/ref/settings/#append-slash
APPEND_SLASH = True

#
# CAPTCHA settings
#
# the filesystem space to write the captchas into
CAPTCHA_ROOT = os.path.join(MEDIA_ROOT, 'captchas')

# the url base that points to that directory served out
CAPTCHA_URL = os.path.join(MEDIA_URL, 'captchas')

# captcha image directory
CAPTCHA_IMAGES = os.path.join(WRITABLE_DIRECTORY, "captcha")


# see: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG

# see: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = ('django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader')

# mako compiled templates directory
MAKO_MODULE_DIR = os.path.join(WRITABLE_DIRECTORY, 'templates')

# mako module name
MAKO_MODULENAME_CALLABLE = ''

# ## USER SPECIFIC SETUP ###
# these are the settings you will most likely change to reflect your setup

DATABASES = {
    'default': {
        'ENGINE': env.get_db_engine("dbtype", "pgsql"),
        'NAME': env.get("dbname", "dev_yabi"),
        'USER': env.get("dbuser", "yabiapp"),
        'PASSWORD': env.get("dbpass", "yabiapp"),
        'HOST': env.get("dbserver", ""),
        'PORT': env.get("dbport", ""),
    }
}

# Add special connection option for MySQL
if env.get("dbtype", "") == "mysql":
    DATABASES['default']['OPTIONS'] = \
        {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'}

# Make this unique, and don't share it with anybody.
# see: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env.get("secret_key", "changeme")

# email settings so yabi can send email error alerts etc
# See: https://docs.djangoproject.com/en/1.6/ref/settings/#email-host
EMAIL_HOST = env.get("email_host", "")
# See: https://docs.djangoproject.com/en/1.6/ref/settings/#email-port
EMAIL_PORT = env.get("email_port", 25)

# See: https://docs.djangoproject.com/en/1.6/ref/settings/#email-host-user
EMAIL_HOST_USER = env.get("email_host_user", "")
# See: https://docs.djangoproject.com/en/1.6/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = env.get("email_host_password", "")

# See: https://docs.djangoproject.com/en/1.6/ref/settings/#email-use-tls
EMAIL_USE_TLS = env.get("email_use_tls", False)

# see: https://docs.djangoproject.com/en/1.6/ref/settings/#email-subject-prefix
EMAIL_APP_NAME = "Yabi Admin "
EMAIL_SUBJECT_PREFIX = env.get("email_subject_prefix", "DEV ")

# See: https://docs.djangoproject.com/en/1.6/ref/settings/#email-backend
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
elif DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(WRITABLE_DIRECTORY, "mail")
    if not os.path.exists(EMAIL_FILE_PATH):
        os.mkdir(EMAIL_FILE_PATH)

# See: https://docs.djangoproject.com/en/1.6/ref/settings/#server-email
SERVER_EMAIL = env.get("server_email", "noreply@ccg_yabiadmin_prod")

# admins to email error reports to
# see: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ('alert', env.get("alert_email", "root@localhost"))
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

# yabi uses modelbackend by default, but can be overridden here
# code used for additional user related operations
# see: https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
# see: https://docs.djangoproject.com/en/dev/ref/settings/#auth-profile-module
if env.get("auth_ldap_server", ""):
    AUTHENTICATION_BACKENDS = [
        'ccg_django_utils.auth.backends.LDAPBackend',
        'ccg_django_utils.auth.backends.NoAuthModelBackend',
    ]
    AUTH_PROFILE_MODULE = 'yabi.LDAPBackendUserProfile'
else:
    AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
    AUTH_PROFILE_MODULE = 'yabi.ModelBackendUserProfile'

AUTH_LDAP_SERVER = env.getlist("auth_ldap_server", [])
AUTH_LDAP_USER_BASE = env.get("auth_ldap_user_base", 'ou=People,dc=set_this,dc=edu,dc=au')
AUTH_LDAP_GROUP_BASE = env.get("auth_ldap_group_base", 'ou=Yabi,ou=Web Groups,dc=set_this,dc=edu,dc=au')
AUTH_LDAP_GROUP = env.get("auth_ldap_group", 'yabi')
AUTH_LDAP_DEFAULT_GROUP = env.get("auth_ldap_default_group", 'baseuser')
AUTH_LDAP_GROUPOC = env.get("auth_ldap_groupoc", 'groupofuniquenames')
AUTH_LDAP_USEROC = env.get("auth_ldap_useroc", 'inetorgperson')
AUTH_LDAP_MEMBERATTR = env.get("auth_ldap_memberattr", 'uniqueMember')
AUTH_LDAP_USERDN = env.get("auth_ldap_userdn", 'ou=People')
LDAP_DONT_REQUIRE_CERT = env.get("ldap_dont_require_cert", False)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

if env.get("memcache", ""):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': env.getlist("memcache"),
            'KEYSPACE': "%(project_name)s-prod" % env
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'yabi_cache',
            'TIMEOUT': 3600,
            'MAX_ENTRIES': 600
        }
    }

    SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    SESSION_FILE_PATH = WRITABLE_DIRECTORY

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

# See: https://docs.djangoproject.com/en/1.6/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = env.get("allowed_hosts", "").split()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

# Any settings that should be changed for just for testing runs
if env.get("use_testing_settings", False):
    SWIFT_BACKEND_SEGMENT_SIZE = 1234567  # approx 1MB segments
    torque_path = "/opt/torque/2.3.13/bin"
    sge_path = "/opt/sge6/bin/linux-x64"
else:
    torque_path = ""
    sge_path = ""

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

torque_path = env.get("torque_path", torque_path)
sge_path = env.get("sge_path", sge_path)
SCHEDULER_COMMAND_PATHS = {
    "torque": {"qsub": os.path.join(torque_path, "qsub"),
               "qstat": os.path.join(torque_path, "qstat"),
               "qdel": os.path.join(torque_path, "qdel")},
    "sge": {"qsub": os.path.join(sge_path, "qsub"),
            "qstat": os.path.join(sge_path, "qstat"),
            "qdel": os.path.join(sge_path, "qdel"),
            "qacct": os.path.join(sge_path, "qacct")},
}

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

# uploads are currently written to disk and double handled, setting a limit will break things
# see https://docs.djangoproject.com/en/dev/ref/settings/#file-upload-max-memory-size
# this also ensures that files are always written to disk so we can access them via temporary_file_path
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

DEFAULT_STAGEIN_DIRNAME = 'stagein/'

# How long to cache decypted credentials for
DEFAULT_CRED_CACHE_TIME = 60 * 60 * 24                   # 1 day default


# ## CELERY ###
# see http://docs.celeryproject.org/en/latest/getting-started/brokers/django.html
# BROKER_URL = 'django://'
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# http://celery.readthedocs.org/en/latest/whatsnew-3.1.html#last-version-to-enable-pickle-by-default
# Pickle is unsecure, but to ensure that we won't fail on existing messages
# we will do this upgrade in 2 steps. For now we make our messages json, but
# still accept 'pickle' to allow failing on existing messages or clearing all
# messages before the upgrade.
# TODO: in a next release drop 'pickle' from CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

# see http://docs.celeryproject.org/en/latest/configuration.html
CELERY_IGNORE_RESULT = True
# Not found in latest docs CELERY_QUEUE_NAME = 'yabiadmin'
# Deprecated alias CARROT_BACKEND = "django"
# Not found in latest docs CELERYD_LOG_LEVEL = "DEBUG"
CELERYD_CONCURRENCY = 4
CELERYD_PREFETCH_MULTIPLIER = 4
CELERY_DISABLE_RATE_LIMITS = True
# see http://docs.celeryproject.org/en/latest/configuration.html#id23
CELERY_SEND_EVENTS = True
CELERY_SEND_TASK_SENT_EVENT = True

# see http://docs.celeryproject.org/en/latest/userguide/routing.html
FILE_OPERATIONS = 'file_operations'

CELERY_QUEUES = (
    Queue('celery', routing_key='celery'),
    Queue(FILE_OPERATIONS, routing_key=FILE_OPERATIONS),
)

FILE_OPERATIONS_ROUTE = {
    'queue': FILE_OPERATIONS,
    'routing_key': FILE_OPERATIONS,
}

CELERY_ROUTES = {
    'yabiadmin.backend.celerytasks.stage_in_files': FILE_OPERATIONS_ROUTE,
    'yabiadmin.backend.celerytasks.stage_out_files': FILE_OPERATIONS_ROUTE,
}

CELERY_IMPORTS = ("yabiadmin.backend.celerytasks",)
CELERY_ACKS_LATE = True
# Not sure if this is still needed BROKER_TRANSPORT = "kombu.transport.django.Transport"

# Set this to 1000 or even higher on LIVE
CELERYD_MAX_TASKS_PER_CHILD = env.get("celeryd_max_tasks_per_child", 100)
CELERYD_FORCE_EXECV = True

CELERYD_LOG_FORMAT = "YABI [%(name)s:%(levelname)s:%(asctime)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s"

# ## PREVIEW SETTINGS

# The truncate key controls whether the file may be previewed in truncated form
# (ie the first "size" bytes returned). If set to false, files beyond the size
# limit simply won't be available for preview.
#
# The override_mime_type key will set the content type that's sent in the
# response to the browser, replacing the content type received from Admin.
#
# MIME types not in this list will result in the preview being unavailable.
PREVIEW_SETTINGS = {
    # Text formats.
    "text/plain": {"truncate": True},

    # Structured markup formats.
    "text/html": {"truncate": False, "sanitise": True},
    "application/xhtml+xml": {"truncate": False, "sanitise": True},
    "text/svg+xml": {"truncate": True, "override_mime_type": "text/plain"},
    "text/xml": {"truncate": True, "override_mime_type": "text/plain"},
    "application/xml": {"truncate": True, "override_mime_type": "text/plain"},

    # Image formats.
    "image/gif": {"truncate": False},
    "image/jpeg": {"truncate": False},
    "image/png": {"truncate": False},
}

# The length of time preview metadata will be cached, in seconds.
PREVIEW_METADATA_EXPIRY = 60

# The maximum file size that can be previewed.
PREVIEW_SIZE_LIMIT = 1048576

# Used by djamboloader to combo load the YUI JS files
THIRTY_DAYS = 30 * 24 * 60 * 60
JAVASCRIPT_LIBRARIES = {
    "yui_3_5_1": {
        "path": os.path.join(WEBAPP_ROOT, "static/javascript/lib/yui-3.5.1/build/"),
        "cache_for": THIRTY_DAYS,
    },
    "yui2in3_2_9_0": {
        "path": os.path.join(WEBAPP_ROOT, "static/javascript/lib/yui-2in3/dist/2.9.0/build/"),
        "cache_for": THIRTY_DAYS,
    },
}

# The logging settings here apply only to the Django WSGI process.
# Celery is left to hijack the root logger. We add our custom handlers after
# that in yabiadmin.backend.celerytasks.
CCG_LOG_DIRECTORY = os.path.join(WEBAPP_ROOT, "log")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': 'YABI [%(name)s:%(levelname)s:%(asctime)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s'
        },
        'db': {
            'format': 'YABI [%(name)s:%(duration)s:%(sql)s:%(params)s] %(message)s'
        },
        'simple': {
            'format': 'YABI %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'yabi_context_exists': {
            '()': 'yabiadmin.yabiengine.engine_logging.YabiContextFilter'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'ccg_django_utils.loghandlers.ParentPathFileHandler',
            'filename': os.path.join(CCG_LOG_DIRECTORY, 'yabiadmin.log'),
            'when': 'midnight',
            'formatter': 'verbose'
        },
        'django_file': {
            'level': 'DEBUG',
            'class': 'ccg_django_utils.loghandlers.ParentPathFileHandler',
            'filename': os.path.join(CCG_LOG_DIRECTORY, 'yabiadmin_django.log'),
            'when': 'midnight',
            'formatter': 'verbose'
        },
        'db_logfile': {
            'level': 'DEBUG',
            'class': 'ccg_django_utils.loghandlers.ParentPathFileHandler',
            'filename': os.path.join(CCG_LOG_DIRECTORY, 'yabiadmin_db.log'),
            'when': 'midnight',
            'formatter': 'db'
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'facility': 'local4',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
            'include_html': True
        },
        'yabi_db_handler': {
            'level': 'DEBUG',
            'filters': ['yabi_context_exists'],
            'class': 'yabiadmin.yabiengine.engine_logging.YabiDBHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console', 'django_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'django_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'db_logfile', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'yabiadmin': {
            'handlers': ['console', 'file', 'yabi_db_handler'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    }
}

# In the case of running in a Celery worker process, Celery will sort
# out its own logging. So we don't need Django to configure anything.
if os.environ.get("YABI_CELERY_WORKER", ""):
    LOGGING = {"version": 1}
