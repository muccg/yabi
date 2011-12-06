#!/usr/bin/env python
from datetime import datetime

class Settings:
    user = None
    orm = None
    
settings = Settings()

def set_default_user(user):
    settings.user = user
    
def set_default_orm(orm):
    settings.orm = orm

def auth_user(username, password, email, active=True, staff=False, superuser=False, user=None, orm=None):
    user = user or settings.user
    orm = orm or settings.orm
    
    authuser = orm['auth.user']()
    authuser.last_modified_by = user or authuser
    authuser.last_modified_on = datetime.now()
    authuser.created_by = user or authuser
    authuser.created_on = datetime.now()
    authuser.username = unicode(username)
    authuser.password = make_password_hash(password)
    authuser.email = email
    authuser.is_active = active
    authuser.is_staff = staff
    authuser.is_superuser = superuser
    return authuser
    
def make_password_hash(password):
    from django.contrib.auth.models import get_hexdigest
    import random
    algo = 'sha1'
    salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
    hsh = get_hexdigest(algo, salt, password)
    return '%s$%s$%s' % (algo, salt, hsh)

def yabi_user(username, user=None, orm=None):
    user = user or settings.user
    orm = orm or settings.orm

    yabi_user = orm['yabi.User']()
    yabi_user.last_modified_by = user
    yabi_user.last_modified_on = datetime.now()
    yabi_user.created_by = user
    yabi_user.created_on = datetime.now()
    yabi_user.name = username

    return yabi_user

def yabi_backend(name, description, scheme, hostname, port, path, max_connections=None, lcopy=True, link=True, submission='', user=None, orm=None):
    user = user or settings.user
    orm = orm or settings.orm
    
    yabi_backend = orm['yabi.Backend']()
    yabi_backend.last_modified_by = user
    yabi_backend.last_modified_on = datetime.now()
    yabi_backend.created_by = user
    yabi_backend.created_on = datetime.now()
    yabi_backend.name = name
    yabi_backend.description = description
    yabi_backend.scheme = scheme
    yabi_backend.hostname = hostname
    yabi_backend.port = port
    yabi_backend.path = path
    yabi_backend.max_connections = max_connections
    yabi_backend.lcopy_supported = lcopy
    yabi_backend.link_supported = link
    yabi_backend.submission = submission
    return yabi_backend
        
def yabi_tool(name, display_name, path, description, backend, fs_backend, enabled=True, accepts_input=False, cpus='', walltime='',module='',queue='',max_memory='',job_type='',lcopy=False, link=False, user=None, orm=None):
    user = user or settings.user
    orm = orm or settings.orm

    yabi_tool = orm['yabi.Tool']()
    yabi_tool.last_modified_by = user
    yabi_tool.last_modified_on = datetime.now()
    yabi_tool.created_by = user
    yabi_tool.created_on = datetime.now()
    yabi_tool.name = name
    yabi_tool.display_name = display_name
    yabi_tool.path = path
    yabi_tool.description = description
    yabi_tool.enabled = enabled
    yabi_tool.backend = backend
    yabi_tool.fs_backend = fs_backend
    yabi_tool.accepts_input = accepts_input
    yabi_tool.cpus = cpus
    yabi_tool.walltime = walltime
    yabi_tool.module = module
    yabi_tool.queue = queue
    yabi_tool.max_memory = max_memory
    yabi_tool.job_type = job_type
    yabi_tool.lcopy_supported = lcopy
    yabi_tool.link_supported = link
    return yabi_tool

#def yabi_user(user=None, orm=None):
    #user = user or settings.user
    #orm = orm or settings.orm
    
#def yabi_user(user=None, orm=None):
    #user = user or settings.user
    #orm = orm or settings.orm
    
 
 

def yabi_fileextension(pattern, user=None, orm=None):
    user = user or settings.user
    orm = orm or settings.orm
    
    fileextension = orm['yabi.FileExtension']()
    fileextension.last_modified_by = user
    fileextension.last_modified_on = datetime.now()
    fileextension.created_by = user
    fileextension.created_on = datetime.now()
    fileextension.pattern = pattern
    return fileextension