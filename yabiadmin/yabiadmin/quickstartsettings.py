from yabiadmin.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'NAME': 'yabiadmin_quickstart.sqlite3',
        'PASSWORD': '', 
        'HOST': '',                    
        'PORT': '',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

BACKEND_PORT = '8001'

HMAC_KEY = 'quickstart'
TASKTAG = 'quickstart' 
