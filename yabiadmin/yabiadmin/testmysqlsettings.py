from yabiadmin.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'NAME': 'test_yabi',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'},
    }
}
