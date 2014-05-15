from settings import *

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

DEBUG = False

# Default SSL on and forced, turn off if necessary
SSL_ENABLED = True
SSL_FORCE = True

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

try:
    from localsettings import *
except ImportError, e:
    pass
