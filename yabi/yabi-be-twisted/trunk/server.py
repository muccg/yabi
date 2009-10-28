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

from resource import BaseResource

# our root and google resource
sys.path=['.']+sys.path

# run as root
PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 8000
TELNET_PORT = 8021
SSL_PORT = 4430

import conf
if "YABIADMIN" in os.environ:
    conf.yabiadmin.parse_url(os.environ['YABIADMIN'])

# make sure our env is sane
import os
assert "GLOBUS_LOCATION" in os.environ
#assert "SGE_ROOT" in os.environ

# Create the resource we will be serving
base = BaseResource()

# Setup default common access logging
res = log.LogWrapperResource(base)
log.DefaultCommonAccessLoggingObserver().start()

# Create the site and application objects
site = server.Site(res)
application = service.Application("yabi-be-twisted")

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

# Twisted Application Framework setup:
application = service.Application('twisted')
from twisted.web2 import channel
internet.TCPServer(PORT, channel.HTTPFactory(site)).setServiceParent(application)
internet.SSLServer(SSL_PORT, channel.HTTPFactory(site), ServerContextFactory()).setServiceParent(application)

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
    print "yabiadmin server:",conf.yabiadmin.SERVER,"port:",conf.yabiadmin.PORT,"path:",conf.yabiadmin.PATH
    
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

