import sys
import os

from twisted.application import internet, service
from twisted.web import server, resource, wsgi, static
from twisted.python import threadpool
from twisted.internet import reactor

# for SSL context
from OpenSSL import SSL

# our root and google resource
sys.path=['.']+sys.path
import twango_resource

# run as root
PORT = 80
SSL_PORT = 443

MANGO_APP = "nutrition"

#
# DEBUG on for this app
#
os.environ['DJANGODEV']="1"
os.environ['DJANGODEBUG']="1"
os.environ['TWISTED_MANGO']='1'

# Environment setup for your Django project files:
sys.path.append(MANGO_APP)
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings'%MANGO_APP
from django.core.handlers.wsgi import WSGIHandler

def wsgi_resource():
    pool = threadpool.ThreadPool()
    pool.start()
    reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)               # shutdown the pool on SIGKILL so we don't end up stale
    wsgi_resource = wsgi.WSGIResource(reactor, pool, WSGIHandler())
    return wsgi_resource


# Twisted Application Framework setup:
application = service.Application('twisted-django')

# WSGI container for Django, combine it with twisted.web.Resource:
# XXX this is the only 'ugly' part: see the 'getChild' method in twresource.Root 
wsgi_root = wsgi_resource()
root = twango_resource.Root(wsgi_root)

# Servce Django media files off of /media:
staticrsrc = static.File(os.path.join(os.path.abspath("."), "%s/media"%MANGO_APP))
root.putChild("media", staticrsrc)

# The cool part! Add in pure Twisted Web Resouce in the mix
# This 'pure twisted' code could be using twisted's XMPP functionality, etc:
root.putChild("reference", twango_resource.GoogleResource())

# Serve it up:
main_site = server.Site(root)
internet.TCPServer(PORT, main_site).setServiceParent(application)

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

internet.SSLServer(SSL_PORT, main_site, ServerContextFactory()).setServiceParent(application)
