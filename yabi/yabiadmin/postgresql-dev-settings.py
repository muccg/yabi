# Local PostgreSQL development DB settings
import os
# development deployment
if "DJANGODEV" in os.environ:
    DEBUG = True if os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug")) else ("DJANGODEBUG" in os.environ)
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'dev_yabmin'            # Or path to database file if using sqlite3.
    DATABASE_USER = 'yabminapp'             # Not used with sqlite3.
    DATABASE_PASSWORD = 'yabminapp'         # Not used with sqlite3.
    DATABASE_HOST = 'eowyn'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
    SSL_ENABLED = False
    DEV_SERVER = True

    # debug site table
    SITE_ID = 1

# production deployment (probably using wsgi)
else:
    DEBUG = os.path.exists(os.path.join(PROJECT_DIRECTORY,".debug"))
    TEMPLATE_DEBUG = DEBUG
    DATABASE_ENGINE = 'postgresql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASE_NAME = 'dev_yabmin'            # Or path to database file if using sqlite3.
    DATABASE_USER = 'yabminapp'             # Not used with sqlite3.
    DATABASE_PASSWORD = 'yabminapp'         # Not used with sqlite3.
    DATABASE_HOST = 'eowyn'             # Set to empty string for localhost. Not used with sqlite3.
    DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
    SSL_ENABLED = True
    DEV_SERVER = False

    # development site id
    SITE_ID = 1
