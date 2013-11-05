from yabiadmin.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'yabiapp',
        'NAME': 'dev_yabi',
        'PASSWORD': 'yabiapp',
        'HOST': '',
        'PORT': '',
    }
}
