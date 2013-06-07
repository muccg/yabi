from yabiadmin.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'yabminapp',
        'NAME': 'dev_yabi',
        'PASSWORD': 'yabminapp',
        'HOST': '',
        'PORT': '',
    }
}
