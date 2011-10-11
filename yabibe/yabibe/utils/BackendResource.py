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
"""Base class for backends"""

import os

from conf import config

class BackendResource(object):
    def __init__(self,*args,**kwargs):
        """Pass in the backends to be served out by this FSResource"""
        self.backends={}
        for name, bend in kwargs.iteritems():
            self.AddBackend(name, bend)
            
    def AddBackend(self, name, bend):
        bend.backend = name                     # store the name in the backend, so the backend knows about it
        self.backends[name]=bend
            
    def GetBackend(self, name):
        return self.backends[name]
    
    def Backends(self):
        return self.backends.keys()
        
    def shutdown(self):
        """tell each backend to shutdown its state onto disk"""
        for name, bend in self.backends.iteritems():
            if hasattr(bend, "shutdown"):
                print "Shutting down %s..."%(name)
                bend.shutdown(directory=config.config['backend']['tasklets'])
                
    def startup(self):
        """tell each backend to bring up its state from disk"""
        for name, bend in self.backends.iteritems():
            if hasattr(bend, "startup"):
                print "Starting up %s..."%(name)
                bend.startup(directory=config.config['backend']['tasklets'])
    
    def LoadConnectors(self, connector, skip='BaseClass', brief='unknown', quiet=False):
        """Load all the backend connectors into our backends. Use module passed in as connector, and skip the class named in skip
        'brief' is just a short textual description for error reporting. should be 'exec' or 'fs'
        """
        connectors = [name for name in dir(connector) if not name.startswith('_') and name != skip]
        for connector_name in connectors:
            conn = getattr(connector,connector_name)
            if hasattr(conn,'ENV_CHILD_INHERIT') and hasattr(conn,'ENV_CHECK') and hasattr(conn,'SCHEMA'):
                # connector looks ok so far. lets check the env vars
                envcheck = [var in os.environ for var in conn.ENV_CHECK]
                if False in envcheck:
                    # some env var failed
                    missing_envs = [ conn.ENV_CHECK[ind] for ind,val in enumerate(envcheck) if not val]
                    
                    if not quiet:
                        print "Skipping %s connector %s. Environment variable%s %s missing" % (
                            brief,
                            connector_name, 
                            "s" if len(missing_envs)>1 else "",
                            ",".join( missing_envs )
                        )
                else:
                    if not quiet:
                        print "Adding %s connector %s under schema %s"%(brief,connector_name,conn.SCHEMA)
                    
                    # lets save what env vars we can save away
                    connector_env = {}
                    for env in conn.ENV_CHILD_INHERIT:
                        if env in os.environ:
                            connector_env[env] = os.environ[env]
                    
                    # instantiate the backend
                    backend = getattr(conn,connector_name)()
                
                    # set those env vars
                    backend.SetEnvironment(connector_env)
                
                    # add it in
                    self.AddBackend(conn.SCHEMA, backend)
            else:
                if not quiet:
                    print "Skipping %s connector %s. Connector needs ENV_CHILD_INHERIT, ENV_CHECK and SCHEMA"%(brief,connector_name)