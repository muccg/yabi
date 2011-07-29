#!/usr/bin/env python

# WSGI bootstrapper for django
import os, sys
import site
import time # this is to avoid a python bug (the time module isn't thread-safe), see CCG Trac ticket #1674

# where are we installed
projectdir=os.path.dirname(__file__)            # PROJECTDIR/nutrition
parentdir=os.path.dirname(projectdir)           # PROJECTDIR/
priv_settings_dir=os.path.join("/usr","local","etc","ccgapps") # location of private, site specific settings

# run some checks and alert users to help them find errors
if not os.path.exists(projectdir):
    raise Exception("Directory does not exist: %s" % projectdir)
if not os.path.exists(parentdir):
    raise Exception("Directory does not exist: %s" % parentdir)
if not os.path.exists(priv_settings_dir):
    raise Exception("Directory does not exist: %s" % priv_settings_dir)


# virtual python env setup, work out python install version so we use the correct site-packages
python_version = "python%s.%s" % (sys.version_info[0], sys.version_info[1])
site.addsitedir(os.path.join(projectdir,"virtualpython","lib",python_version,"site-packages"))
site.addsitedir(projectdir)

# the parent directory to search
sys.path.append(projectdir)
sys.path.append(parentdir)
sys.path.append(priv_settings_dir)

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
