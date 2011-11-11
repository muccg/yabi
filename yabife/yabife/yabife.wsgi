#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

def prependpackage(sitedir, name, known_paths):
    """Process a .pth file within the site-packages directory:
       For each line in the file, either combine it with sitedir to a path
       and add that to known_paths, or execute it if it starts with 'import '.
    """
    if known_paths is None:
        site._init_pathinfo()
        reset = 1
    else:
        reset = 0
    fullname = os.path.join(sitedir, name)
    try:
        f = open(fullname, "rU")
    except IOError:
        return
    with f:
        for line in f:
            if line.startswith("#"):
                continue
            if line.startswith(("import ", "import\t")):
                exec line
                continue
            line = line.rstrip()
            dir, dircase = site.makepath(sitedir, line)
            if not dircase in known_paths and os.path.exists(dir):
                sys.path.insert(0,dir)
                known_paths.add(dircase)
    if reset:
        known_paths = None
    return known_paths

def prependsitedir(sitedir, known_paths=None):
    """Add 'sitedir' argument to sys.path if missing and handle .pth files in
    'sitedir'"""
    if known_paths is None:
        known_paths = site._init_pathinfo()
        reset = 1
    else:
        reset = 0
    sitedir, sitedircase = site.makepath(sitedir)
    if not sitedircase in known_paths:
        sys.path.insert(0,sitedir)        # Add path component
    try:
        names = os.listdir(sitedir)
    except os.error:
        return
    dotpth = os.extsep + "pth"
    names = [name for name in names if name.endswith(dotpth)]
    for name in sorted(names):
        prependpackage(sitedir, name, known_paths)
    if reset:
        known_paths = None
    return known_paths

# virtual python env setup, work out python install version so we use the correct site-packages
python_version = "python%s.%s" % (sys.version_info[0], sys.version_info[1])
prependsitedir(os.path.join(projectdir,"virtualpython","lib",python_version,"site-packages"))
prependsitedir(projectdir)

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
