from yabiadmin.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'yabiapp',
        'NAME': 'test_yabi',
        'PASSWORD': 'yabiapp',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {}
    }
}

SWIFT_BACKEND_SEGMENT_SIZE = 1234567  # approx 1MB segments just for testing
