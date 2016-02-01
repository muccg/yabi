# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from ccg_django_utils.webhelpers import url
from ccg_django_utils.conf import EnvConfig

from kombu import Queue

env = EnvConfig()

SCRIPT_NAME = env.get("script_name", os.environ.get("HTTP_SCRIPT_NAME", ""))
FORCE_SCRIPT_NAME = env.get("force_script_name", "") or SCRIPT_NAME or None

WEBAPP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRODUCTION = env.get("production", False)
TESTING = env.get("testing", False)

# set debug, see: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.get("debug", not PRODUCTION)

# django-secure
SECURE_SSL_REDIRECT = env.get("secure_ssl_redirect", PRODUCTION)
# We do clickjacking support using Django's middleware. See MIDDLEWARE_CLASSES
SECURE_FRAME_DENY = False
SECURE_CONTENT_TYPE_NOSNIFF = env.get("secure_content_type_nosniff", PRODUCTION)
SECURE_BROWSER_XSS_FILTER = env.get("secure_browser_xss_filter", PRODUCTION)
SECURE_HSTS_SECONDS = env.get("secure_hsts_seconds", 10)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.get("secure_hsts_include_subdomains", PRODUCTION)

# see: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

ATOMIC_REQUESTS = True

# see: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE_CLASSES = [
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
]

# We don't want to deal with CSRF during testing
# The recommended way is to set special header in the HTTP requests to
# disable CSRF, but we use a lot of different HTTP clients in our tests
# so disabling on the server-side it is easier.
if TESTING:
    MIDDLEWARE_CLASSES.remove('django.middleware.csrf.CsrfViewMiddleware')

# see: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'yabi.yabifeapp',
    'yabi.yabi',
    'yabi.yabiengine',
    'kombu.transport.django',
    'django_extensions',
    'djamboloader',
    'django.contrib.admin',
    'djangosecure',
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'yabi.urls'

# cookies
# see: https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-age
# see: https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
# you SHOULD change the cookie to use HTTPONLY and SECURE when in production
SESSION_COOKIE_AGE = env.get("session_cookie_age", 60 * 60)
SESSION_COOKIE_PATH = url('/')
SESSION_SAVE_EVERY_REQUEST = env.get("session_save_every_request", True)
SESSION_COOKIE_HTTPONLY = SESSION_COOKIE_HTTPONLY = env.get("session_cookie_httponly", True)
SESSION_COOKIE_SECURE = env.get("session_cookie_secure", PRODUCTION)
SESSION_COOKIE_NAME = env.get("session_cookie_name", "yabi_{0}".format(url('/').replace("/", "")))
SESSION_COOKIE_DOMAIN = env.get("session_cookie_domain", "") or None
CSRF_COOKIE_NAME = env.get("csrf_cookie_name", "csrf_{0}".format(SESSION_COOKIE_NAME))
CSRF_COOKIE_DOMAIN = env.get("csrf_cookie_domain", "") or SESSION_COOKIE_DOMAIN
CSRF_COOKIE_PATH = env.get("csrf_cookie_path", SESSION_COOKIE_PATH)
CSRF_COOKIE_SECURE = env.get("csrf_cookie_secure", PRODUCTION)

# Locale
# see: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
#      https://docs.djangoproject.com/en/dev/ref/settings/#language-code
#      https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
TIME_ZONE = env.get("time_zone", "Australia/Perth")
LANGUAGE_CODE = env.get("language_code", "en-us")
USE_I18N = True

# see: https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = url('/login/')
LOGOUT_URL = url('/logout/')

# ## static file management ###
# see: https://docs.djangoproject.com/en/dev/howto/static-files/
# deployment uses an apache alias
# STATICFILES_DIRS = [os.path.join(WEBAPP_ROOT,"static")]
STATIC_URL = url('/static/')
STATIC_ROOT = env.get('static_root', os.path.join(WEBAPP_ROOT, 'static'))
ADMIN_MEDIA_PREFIX = url('/static/admin/')

# media directories
# see: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = env.get('media_root', os.path.join(WEBAPP_ROOT, 'static', 'media'))
MEDIA_URL = url('/static/media/')

# a directory that will be writable by the webserver, for storing various files...
WRITABLE_DIRECTORY = env.get('writable_directory', os.path.join(WEBAPP_ROOT, 'scratch'))
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
        'HOST': env.get("dbserver", "localhost"),
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

# AWS Credentials used to provision EC2 instances
AWS_ACCESS_KEY_ID = env.get("aws_access_key_id", "")
AWS_SECRET_ACCESS_KEY = env.get("aws_secret_access_key", "")

S3_MULTIPART_UPLOAD_MAX_RETRIES = env.get("s3_multipart_upload_max_retries", 10)

# OpenStack Credentials used to provision Nova instances
OPENSTACK_USER = env.get("openstack_user", "")
OPENSTACK_PASSWORD = env.get("openstack_password", "")

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
SERVER_EMAIL = env.get("server_email", "noreply@ccg_yabi_prod")

# admins to email error reports to
# see: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ('alert', env.get("alert_email", "root@localhost"))
]

# see: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

# Default authentication is against the Database (with case insensitive usernames)
# Change AUTH_TYPE if you would like to use another authentication method to one of:
#   - ldap : Authenticate against LDAP
#   - kerberos: Authenticate against Kerberos
#   - kerberos+ldap: Authenticate against Kerberos but use LDAP to check Yabi group
#                    membership, superuser status and fetch user details.
#                    and user details

AUTH_TYPE = env.get("auth_type", "").lower()

# Set to True if you would like to add the Database Authentication as a fallback.
# This is useful to be able to log in even if there is some problem with your
# LDAP, Kerberos etc. server.
# AUTH_ENABLE_DB_FALLBACK = env.get("auth_enable_db_fallback", True)
AUTH_ENABLE_DB_FALLBACK = env.get("auth_enable_db_fallback", True)

AUTHENTICATION_BACKENDS = []
if AUTH_TYPE == 'ldap':
    AUTHENTICATION_BACKENDS = [
        'yabi.authbackends.ldap.LDAPBackend'
    ]
elif AUTH_TYPE == 'kerberos+ldap':
    AUTHENTICATION_BACKENDS = [
        'yabi.authbackends.kerberosldap.KerberosLDAPBackend'
    ]

if AUTHENTICATION_BACKENDS == [] or AUTH_ENABLE_DB_FALLBACK:
    AUTHENTICATION_BACKENDS.append('yabi.authbackends.CaseInsensitiveUsernameModelBackend')

AUTH_KERBEROS_REALM = env.get('auth_kerberos_realm', '')
AUTH_KERBEROS_SERVICE = env.get('auth_kerberos_service', '')

# LDAP details have to be set correctly if AUTH_TYPE is "ldap" or "kerberos+ldap"
# LDAP settings you have to set for sure:
AUTH_LDAP_SERVER = env.getlist("auth_ldap_server", [])
AUTH_LDAP_USER_BASE = env.get("auth_ldap_user_base", "")
AUTH_LDAP_YABI_GROUP_DN = env.get("auth_ldap_yabi_group_dn", "")
AUTH_LDAP_YABI_ADMIN_GROUP_DN = env.get("auth_ldap_yabi_admin_group_dn", "")
# LDAP settings you might want to set:
AUTH_LDAP_SYNC_USER_ON_LOGIN = env.get("auth_ldap_sync_user_on_login", False)
AUTH_LDAP_USER_FILTER = env.get("auth_ldap_user_filter", "(objectclass=person)")
# This is the attribute of a Group that contains Users in the group
AUTH_LDAP_MEMBER_ATTR = env.get("auth_ldap_member_attr", "uniqueMember")
# This is the attribute of a user that is stored in the group membership attribute.
# Can be "dn" or "username"
AUTH_LDAP_MEMBER_ATTR_HAS_USER_ATTR = env.get("auth_ldap_member_attr_has_user_attr", "dn")
# This is the attribute of a User that contains Groups a user is member of
AUTH_LDAP_MEMBER_OF_ATTR = env.get("auth_ldap_member_of_attr", "memberOf")
AUTH_LDAP_USERNAME_ATTR = env.get("auth_ldap_username_attr", "uid")
AUTH_LDAP_EMAIL_ATTR = env.get("auth_ldap_email_attr", "mail")
AUTH_LDAP_LASTNAME_ATTR = env.get("auth_ldap_lastname_attr", "sn")
AUTH_LDAP_FIRSTNAME_ATTR = env.get("auth_ldap_firstname_attr", "givenName")
AUTH_LDAP_REQUIRE_TLS_CERT = env.get("auth_ldap_require_tls_cert", True)

# This honours the X-Forwarded-Host header set by our nginx frontend when
# constructing redirect URLS.
# see: https://docs.djangoproject.com/en/1.4/ref/settings/#use-x-forwarded-host
USE_X_FORWARDED_HOST = env.get("use_x_forwarded_host", True)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

if env.get("memcache", ""):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': env.getlist("memcache"),
            'KEYSPACE': env.get("key_prefix", "yabi")
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
ALLOWED_HOSTS = env.getlist("allowed_hosts", ["localhost"])

# This honours the X-Forwarded-Host header set by our nginx frontend when
# constructing redirect URLS.
# see: https://docs.djangoproject.com/en/1.4/ref/settings/#use-x-forwarded-host
USE_X_FORWARDED_HOST = env.get("use_x_forwarded_host", True)

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
slurm_path = env.get("slurm_path", "")
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
BROKER_URL = env.get("celery_broker", 'amqp://guest:guest@localhost:5672//')

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
# Not found in latest docs CELERY_QUEUE_NAME = 'yabi'
# Deprecated alias CARROT_BACKEND = "django"
# Not found in latest docs CELERYD_LOG_LEVEL = "DEBUG"
CELERYD_POOL_RESTARTS = True
CELERYD_CONCURRENCY = 4
CELERYD_PREFETCH_MULTIPLIER = 4
CELERY_DISABLE_RATE_LIMITS = True
# see http://docs.celeryproject.org/en/latest/configuration.html#id23
CELERY_SEND_EVENTS = True
CELERY_SEND_TASK_SENT_EVENT = True

# see http://docs.celeryproject.org/en/latest/userguide/routing.html
FILE_OPERATIONS = 'file_operations'
PROVISIONING = 'provisioning'

CELERY_QUEUES = (
    Queue('celery', routing_key='celery'),
    Queue(FILE_OPERATIONS, routing_key=FILE_OPERATIONS),
    Queue(PROVISIONING, routing_key=PROVISIONING),
)

FILE_OPERATIONS_ROUTE = {
    'queue': FILE_OPERATIONS,
    'routing_key': FILE_OPERATIONS,
}

PROVISIONING_ROUTE = {
    'queue': PROVISIONING,
    'routing_key': PROVISIONING,
}

CELERY_ROUTES = {
    'yabi.backend.celerytasks.provision_fs_be': PROVISIONING_ROUTE,
    'yabi.backend.celerytasks.provision_ex_be': PROVISIONING_ROUTE,
    'yabi.backend.celerytasks.clean_up_dynamic_backends': PROVISIONING_ROUTE,

    'yabi.backend.celerytasks.stage_in_files': FILE_OPERATIONS_ROUTE,
    'yabi.backend.celerytasks.stage_out_files': FILE_OPERATIONS_ROUTE,
}

CELERY_IMPORTS = ("yabi.backend.celerytasks",)
CELERY_ACKS_LATE = True
# Not sure if this is still needed BROKER_TRANSPORT = "kombu.transport.django.Transport"

# Set this to 1000 or even higher on LIVE
CELERYD_MAX_TASKS_PER_CHILD = env.get("celeryd_max_tasks_per_child", 100)
CELERYD_FORCE_EXECV = True

CELERYD_LOG_FORMAT = "YABI [%(name)s:%(levelname)s:%(asctime)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s"

# How much to wait between polling whether the Dynamic Backend is ready for usage
# DYNBE_READY_POLL_INTERVAL = 120

# How much to wait between retrying a task if the task limit on Backends has
# been reached.
# TASK_LIMIT_REACHED_RETRY_INTERVAL = 120

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
        "path": os.path.join(STATIC_ROOT, "javascript/lib/yui-3.5.1/build/"),
        "cache_for": THIRTY_DAYS,
    },
    "yui2in3_2_9_0": {
        "path": os.path.join(STATIC_ROOT, "javascript/lib/yui-2in3/dist/2.9.0/build/"),
        "cache_for": THIRTY_DAYS,
    },
}

# We're not running tests through Django but the System Check Frameworks complains if
# TEST_RUNNER isn't set
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# The logging settings here apply only to the Django WSGI process.
# Celery is left to hijack the root logger. We add our custom handlers after
# that in yabi.backend.celerytasks.
CCG_LOG_DIRECTORY = env.get('log_directory', os.path.join(WEBAPP_ROOT, "log"))
if not os.path.exists(CCG_LOG_DIRECTORY):
    os.mkdir(CCG_LOG_DIRECTORY)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'syslog': {
            'format': 'YABI [%(name)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s] %(message)s'
        },
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
            '()': 'yabi.yabiengine.engine_logging.YabiContextFilter'
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
            'filename': os.path.join(CCG_LOG_DIRECTORY, 'yabi.log'),
            'when': 'midnight',
            'formatter': 'verbose'
        },
        'django_file': {
            'level': 'DEBUG',
            'class': 'ccg_django_utils.loghandlers.ParentPathFileHandler',
            'filename': os.path.join(CCG_LOG_DIRECTORY, 'yabi_django.log'),
            'when': 'midnight',
            'formatter': 'verbose'
        },
        'db_logfile': {
            'level': 'DEBUG',
            'class': 'ccg_django_utils.loghandlers.ParentPathFileHandler',
            'filename': os.path.join(CCG_LOG_DIRECTORY, 'yabi_db.log'),
            'when': 'midnight',
            'formatter': 'db'
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
            'class': 'yabi.yabiengine.engine_logging.YabiDBHandler'
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
            'handlers': ['console', 'django_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'db_logfile'],
            'level': 'WARNING',
            'propagate': False,
        },
        'yabi': {
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
