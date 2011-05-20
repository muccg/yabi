# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(__file__))                  # add our base directory to the pythonpath

from conf import config
config.read_config()
config.sanitise()

# sanity check that temp directory is set
assert config.config['backend'].has_key('temp'), "[backend] section of yabi.conf is missing 'temp' directory setting"
logfile = config.config['backend']['logfile']

from urlparse import urlparse

import stacklessreactor
stacklessreactor.install()

from twisted.web2 import log
from twisted.internet import reactor
from twisted.application import strports, service, internet
from twisted.web2 import server, vhost, channel
from twisted.web2 import resource as web2resource
from twisted.python import util

# for SSL context
from OpenSSL import SSL

from BaseResource import BaseResource

# make sure our env is sane
#assert "GLOBUS_LOCATION" in os.environ
#assert "SGE_ROOT" in os.environ

# Twisted Application Framework setup:
application = service.Application('yabi-be-twisted')

# set up twisted logging
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

LOG_STDOUT = "--logfile=-" in sys.argv or "-l-" in sys.argv

if not LOG_STDOUT:
    path, fname = [ os.path.expanduser(X) for X in os.path.split(logfile)]
    logfileobj = DailyLogFile(fname, path)
    application.setComponent(ILogObserver, FileLogObserver(logfileobj).emit)

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
        ctx.use_certificate_file(os.path.join(config.config['backend']['certfile']))
        ctx.use_privatekey_file(os.path.join(config.config['backend']['keyfile']))
        return ctx

internet.TCPServer(config.config['backend']['port'][1], channel.HTTPFactory(site)).setServiceParent(application)
internet.SSLServer(config.config['backend']['sslport'][1], channel.HTTPFactory(site), ServerContextFactory()).setServiceParent(application)

if config.config['backend']['telnet']:
    # telnet port to python shell
    from twisted.manhole import telnet
    
    shellfactory = telnet.ShellFactory()
    reactor.listenTCP(config.config['backend']['telnetport'][1], shellfactory)
    shellfactory.namespace['app']=application
    shellfactory.namespace['site']=site
    shellfactory.username = ''
    shellfactory.password = ''

def startup():
    # setup yabiadmin server, port and path as global variables
    print "yabi admin server:",config.config["backend"]["admin"]
    
    print "Loading connectors..."
    base.LoadConnectors()
        
    # setup the TaskManager if we are needed
    if config.config["taskmanager"]["startup"]:
        print "Starting task manager"
        import TaskManager
        reactor.callLater(0.1,TaskManager.startup) 
    else:
        print "NOT starting task manager"
        
    print "Initialising connectors..."
    base.startup()

reactor.addSystemEventTrigger("after", "startup", startup)

def shutdown():
    import TaskManager
    TaskManager.shutdown()
    
    # shutdown our connectors
    base.shutdown()
    
reactor.addSystemEventTrigger("before","shutdown",shutdown)

