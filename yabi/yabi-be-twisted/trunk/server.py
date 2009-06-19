import sys, os

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
import twango_resource

# run as root
PORT = 8000
SSL_PORT = 4430

# Create the resource we will be serving
base = BaseResource()

# Setup default common access logging
res = log.LogWrapperResource(base)
log.DefaultCommonAccessLoggingObserver().start()

# Create the site and application objects
site = server.Site(res)
application = service.Application("gencache")

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
reactor.listenTCP(8021, shellfactory)
shellfactory.namespace['app']=application
shellfactory.namespace['site']=site
shellfactory.username = ''
shellfactory.password = ''

# for testing lets fire up one task
import stackless
def tasklet(num):
    while True:
        #print "BAM",num
        for i in xrange(100):
            stackless.schedule()
            
def starttasklet():
    print "starting tasklet"
    for i in range(1000000):
        task = stackless.tasklet(tasklet)
        task.setup(i)
        #print "starting",i
        task.run()
    print "done"
    
def startup():
        # setup the cache
        print "Startup..."
        reactor.callLater(0.2,starttasklet) 

reactor.addSystemEventTrigger("before", "startup", startup)

