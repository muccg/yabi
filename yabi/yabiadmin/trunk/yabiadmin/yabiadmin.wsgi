#!/usr/bin/env python

# WSGI bootstrapper for django
import os

# where are we installed
projectdir=os.path.dirname(__file__)            # PROJECTDIR/nutrition
parentdir=os.path.dirname(projectdir)           # PROJECTDIR/

# virtual python env setup
import site
site.addsitedir(os.path.join(projectdir,"virtualpython","lib","python2.6","site-packages"))
site.addsitedir(projectdir)

import sys

# the parent directory to search
sys.path.append(projectdir)
sys.path.append(parentdir)
sys.path.append(os.path.join("/usr","local","etc","ccgapps"))

# save the project dir in a environment variable
os.environ['PROJECT_DIRECTORY']=projectdir

# set up the egg cache
eggdir = os.path.join(projectdir,"scratch","egg-cache")
try:
    os.makedirs(eggdir)
except OSError, ose:
    pass
os.environ['PYTHON_EGG_CACHE']=eggdir

# setup the settings module for the WSGI app
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings'%(os.path.basename(projectdir))

import django.core.handlers.wsgi

# we are gonna do some voodoo to pull out our SCRIPT_NAME
# TODO: work out how to get the request.META object inside a tag processor
def wrapper(environ, start):
        os.environ['SCRIPT_NAME']=environ['SCRIPT_NAME']
        if 'DJANGODEV' in environ:
            os.environ['DJANGODEV']=environ['DJANGODEV']
        return django.core.handlers.wsgi.WSGIHandler()(environ,start)

application = wrapper

#django.core.handlers.wsgi.WSGIHandler()
