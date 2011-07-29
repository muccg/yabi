# -*- coding: utf-8 -*-
"""
"""
# there is no default setup here as one of these configs should be made 'default' by the settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'set_this',
        'NAME': 'set_this',
        'PASSWORD': 'set_this', 
        'HOST': 'set_this',                    
        'PORT': '',
    }
}

AUTH_LDAP_SERVER = ['ldaps://set_this.localdomain']
AUTH_LDAP_USER_BASE = 'ou=People,dc=set_this,dc=edu,dc=au'
AUTH_LDAP_GROUP_BASE = 'ou=Yabi,ou=Web Groups,dc=set_this,dc=edu,dc=au'
AUTH_LDAP_GROUP = 'yabi'
AUTH_LDAP_DEFAULT_GROUP = 'baseuser'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'set_this'

# memcache server list
MEMCACHE_SERVERS = ['set_this.localdomain:11211']
MEMCACHE_KEYSPACE = "yabiadmin-live"

# email server
EMAIL_HOST = 'ccg.murdoch.edu.au'
EMAIL_APP_NAME = "Yabi Admin "
SERVER_EMAIL = "apache@set_this"
EMAIL_SUBJECT_PREFIX = "LIVE "

# default emails
ADMINS = [
    ( 'alert', 'alerts@set_this' )
]
MANAGERS = ADMINS
