import sys, os

from urlparse import urlparse

from twisted.web2 import log
from twisted.internet import reactor
from twisted.application import strports, service, internet
from twisted.web2 import server, vhost, channel
from twisted.web2 import resource as web2resource
from twisted.python import util

# for SSL context
from OpenSSL import SSL

from conf import config
config.read_config()
config.sanitise()

# Twisted Application Framework setup:
application = service.Application('yabiadmin')

# Environment setup for your Django project files:
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from twisted.web2 import wsgi
from django.conf import settings
from django.core.management import setup_environ

import settings
setup_environ(settings)

from django.core.handlers.wsgi import WSGIHandler

def application(environ, start):
    os.environ['SCRIPT_NAME']=environ['SCRIPT_NAME']
    if 'DJANGODEV' in environ:
        os.environ['DJANGODEV']=environ['DJANGODEV']
    if 'DJANGODEBUG' in environ:
        os.environ['DJANGODEBUG']=environ['DJANGODEBUG']
    result = WSGIHandler()(environ,start)
    #print "result:\n\n",result
    return result
    
base = wsgi.WSGIResource(application)

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
        ctx.use_certificate_file('servercert.pem')
        ctx.use_privatekey_file('serverkey.pem')
        return ctx

from twisted.web2 import channel
internet.TCPServer(config.config['admin']['port'][1], channel.HTTPFactory(site)) #.setServiceParent(application)
if config.config["admin"]["ssl"]:
    internet.SSLServer(config.config['admin']['sslport'][1], channel.HTTPFactory(site), ServerContextFactory()) #.setServiceParent(application)

def startup():
    # setup yabiadmin server, port and path as global variables
    print "yabi backend server:",config.config["admin"]["backend"]
    
    pass

reactor.addSystemEventTrigger("before", "startup", startup)

def shutdown():
    pass
    
reactor.addSystemEventTrigger("before","shutdown",shutdown)

