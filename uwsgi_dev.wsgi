# Generic WSGI application
import os
import os.path
import django.core.handlers.wsgi

webapp_root = os.path.dirname(os.path.abspath(__file__))

def application(environ, start):
    return django.core.handlers.wsgi.WSGIHandler()(environ,start)
