import sys, os

from urlparse import urlparse

import stacklessreactor
stacklessreactor.install()

from twisted.web2 import log
from twisted.internet import reactor
from twisted.application import strports, service, internet
from twisted.web2 import server, vhost, channel
from twisted.python import util


# for SSL context
from OpenSSL import SSL

# for stackless
import stackless

from BaseResource import BaseResource

# our root and google resource
sys.path=['.']+sys.path

# run as root
#PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 8000
#TELNET_PORT = int(os.environ['TELNET_PORT']) if 'TELNET_PORT' in os.environ else 8021
#SSL_PORT = int(os.environ['SSL_PORT']) if 'SSL_PORT' in os.environ else 4430

from conf import config
config.read_config()
config.sanitise()
portconfig = config.classify_ports()

# make sure our env is sane
import os
assert "GLOBUS_LOCATION" in os.environ
#assert "SGE_ROOT" in os.environ

from django.conf import settings
from django.core.management import setup_environ
#import yabiadmin.settings
#setup_environ(yabiadmin.settings)

from django.core.handlers.wsgi import WSGIHandler
from twisted.web2 import wsgi
from twisted.web2 import resource as web2resource

# Twisted Application Framework setup:
application = service.Application('yabi-be-twisted')

# for each module that is set to be started, create its resource
modules = {}
resource_directories = {
    'admin':'yabiadmin',
    'frontend':'yabife',
    'store':'yabistore',
}

path_store = sys.path
print "SYS PATH:",path_store

# application function for wsgi
def app_builder(appname):
    def app(environ, start):
        
        print "APP",appname
        
        # do we need this?
        
        #sys.path=[resource_directories[appname]]+sys.path
        sys.path=[resource_directories[appname], '/usr/local/stackless/lib/python26.zip', '/usr/local/stackless/lib/python2.6', '/usr/local/stackless/lib/python2.6/plat-linux2', '/usr/local/stackless/lib/python2.6/lib-tk', '/usr/local/stackless/lib/python2.6/lib-old', '/usr/local/stackless/lib/python2.6/lib-dynload', '/usr/local/stackless/lib/python2.6/site-packages','.']
        
        os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings'%resource_directories[appname]
        os.environ['SCRIPT_NAME']=environ['SCRIPT_NAME']
        if 'DJANGODEV' in environ:
            os.environ['DJANGODEV']=environ['DJANGODEV']
        if 'DJANGODEBUG' in environ:
            os.environ['DJANGODEBUG']=environ['DJANGODEBUG']
        
        print "application:",os.environ['DJANGO_SETTINGS_MODULE'],os.environ['SCRIPT_NAME'],os.environ['DJANGODEV'],os.environ['DJANGODEBUG']
            
        result = WSGIHandler()(environ,start)
        
        print "PAGE:",result
        
        #sys.path = path_store
        
        return result
    return app

# Create the resource we will be serving
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
        ctx.use_certificate_file('servercert.pem')
        ctx.use_privatekey_file('serverkey.pem')
        return ctx

from twisted.web2 import channel
internet.TCPServer(config.config['backend']['port'][1], channel.HTTPFactory(site)).setServiceParent(application)
internet.SSLServer(config.config['backend']['sslport'][1], channel.HTTPFactory(site), ServerContextFactory()).setServiceParent(application)

# telnet port to python shell
from twisted.manhole import telnet

shellfactory = telnet.ShellFactory()
reactor.listenTCP(TELNET_PORT, shellfactory)
shellfactory.namespace['app']=application
shellfactory.namespace['site']=site
shellfactory.username = ''
shellfactory.password = ''

def startup():
    # setup yabiadmin server, port and path as global variables
    print "yabi admin server:",config.yabiadmin
    
    print "Loading connectors..."
    base.LoadConnectors()
        
    # setup the TaskManager if we are needed
    if "TASKMANAGER" in os.environ:
        print "Starting task manager"
        import TaskManager
        reactor.callLater(0.1,TaskManager.startup) 
    else:
        print "NOT starting task manager"
        

reactor.addSystemEventTrigger("before", "startup", startup)

def shutdown():
    import TaskManager
    TaskManager.shutdown()
    
reactor.addSystemEventTrigger("before","shutdown",shutdown)

