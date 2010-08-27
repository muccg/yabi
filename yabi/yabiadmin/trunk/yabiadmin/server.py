# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(__file__))                  # add our base directory to the pythonpath

from urlparse import urlparse

from twisted.web2 import log
from twisted.internet import reactor
from twisted.application import strports, service, internet
from twisted.web2 import server, vhost, channel
from twisted.web2 import resource as web2resource
from twisted.python import util

# for SSL context
from OpenSSL import SSL

NAME = "admin"
APPNAME = "yabiadmin"

from conf import config
config.read_config()
config.sanitise()

# configure up our YABISTORE and YABIADMIN env variables for the django application
os.environ['YABISTORE'] = config.config['admin']['store']
os.environ['YABIBACKEND'] = config.config['admin']['backend']

# Twisted Application Framework setup:
application = service.Application(APPNAME)

# Environment setup for your Django project files:
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

# custom database settings
os.environ['CUSTOMDB']='1'
for setting in ['database_engine', 'database_name', 'database_user', 'database_password', 'database_host', 'database_port','auth_ldap_server', 'auth_ldap_user_base','auth_ldap_group_base','auth_ldap_group','auth_ldap_default_group']:
    os.environ[setting.upper()] = config.config[NAME][setting]

if 'http_redirect_to_https' in config.config[NAME]:
    os.environ['HTTP_REDIRECT_TO_HTTPS'] = config.config[NAME]['http_redirect_to_https']

if config.config[NAME]["debug"]:
    os.environ['DJANGODEBUG'] = '1'
    
# admin email
if config.config[NAME]["alert_email"]:
    os.environ['ADMIN_EMAIL_NAME'],os.environ['ADMIN_EMAIL'] = config.config[NAME]["alert_email"]

if config.config[NAME]["memcache_servers"]:
    os.environ['MEMCACHE_SERVERS'] = config.config[NAME]["memcache_servers"]
if config.config[NAME]["memcache_prefix"]:
    os.environ['MEMCACHE_PREFIX'] = config.config[NAME]["memcache_prefix"]

from twisted.web2 import wsgi, resource
from django.conf import settings
from django.core.management import setup_environ

# this has to be out here for it to work.
if config.config[NAME]["path"]=='/':
    os.environ['SCRIPT_NAME']=''
else:
    os.environ['SCRIPT_NAME']=config.config[NAME]["path"]

import settings
setup_environ(settings)

from django.core.handlers.wsgi import WSGIHandler

def wsgiapp(environ, start):
    return WSGIHandler()(environ,start)
    
# now we are either the base resource, or we need to create a base resource and then create
# a child_ chain to the resource.
if not config.config[NAME]["path"] or config.config[NAME]["path"]=="/":
    base = wsgi.WSGIResource(wsgiapp)
else:
    class BaseResource(resource.PostableResource):
        addSlash=True
    
        def locateChild(self, request, segments):
            # return our local file resource for these segments
            
            # strip trailing /'s (  [''] )
            adminpath = config.config[NAME]["path"].split("/")
            while adminpath and not adminpath[-1]:
                adminpath.pop()
            while adminpath and not adminpath[0]:
                adminpath.pop(0)
            
            asksegments = segments[:]
            
            # while the segments match, consume more
            while len(adminpath) and len(asksegments) and adminpath[0]==asksegments[0]:
                # remove the matching first entry
                adminpath.pop(0)
                asksegments.pop(0)
            
            if len(adminpath):
                # our request is not under the admin path
                return resource.Resource.locateChild(self,request,segments)
            
            return wsgi.WSGIResource(wsgiapp), asksegments
    
    base = BaseResource()
     
# Setup default common access logging
res = log.LogWrapperResource(base)
log.DefaultCommonAccessLoggingObserver().start()

# Create the site and application objects
site = server.Site(res)

# for HTTPS, we need a server context factory to build the context for each ssl connection
class ServerContextFactory:
    def getContext(self):
        """Create an SSL context.
        This is a sample implementation that loads a certificate from a file
        called 'server.pem'."""
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_certificate_file(os.path.join(config.config[NAME]['certfile']))
        ctx.use_privatekey_file(os.path.join(config.config[NAME]['keyfile']))
        return ctx

from twisted.web2 import channel
internet.TCPServer(config.config[NAME]['port'][1], channel.HTTPFactory(site)).setServiceParent(application)
if config.config[NAME]["ssl"]:
    internet.SSLServer(config.config[NAME]['sslport'][1], channel.HTTPFactory(site), ServerContextFactory()).setServiceParent(application)

def startup():
    # setup yabiadmin server, port and path as global variables
    print "yabi backend server:",config.config[NAME]["backend"]
    
    pass

reactor.addSystemEventTrigger("before", "startup", startup)

def shutdown():
    pass
    
reactor.addSystemEventTrigger("before","shutdown",shutdown)

