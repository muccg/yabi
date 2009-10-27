"""Our twisted filesystem server resource"""

from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor

import weakref
import sys, os

from ExecRunResource import ExecRunResource

class ExecResource(resource.Resource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.1
    addSlash = True
    
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
    
    def LoadConnectors(self):
        """Load all the backend connectors into our backends"""
        import connector
        connectors = [name for name in dir(connector) if not name.startswith('_') and name != 'ExecConnector']
        for connector_name in connectors:
            conn = getattr(connector,connector_name)
            if hasattr(conn,'ENV_CHILD_INHERIT') and hasattr(conn,'ENV_CHECK') and hasattr(conn,'SCHEMA'):
                # connector looks ok so far. lets check the env vars
                envcheck = [var in os.environ for var in conn.ENV_CHECK]
                if False in envcheck:
                    # some env var failed
                    missing_envs = [ conn.ENV_CHECK[ind] for ind,val in enumerate(envcheck) if not val]
                    
                    print "Skipping exec connector %s. Environment variable%s %s missing" % (
                            connector_name, 
                            "s" if len(missing_envs)>1 else "",
                            ",".join( missing_envs )
                        )
                else:
                    print "Adding exec connector %s under schema %s"%(connector_name,conn.SCHEMA)
                    
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
                print "Skipping exec connector %s. Connector needs ENV_CHILD_INHERIT, ENV_CHECK and SCHEMA"%connector_name
        
    def render(self, request):
        # break our request path into parts
        parts = request.path.split("/")
        assert parts[0]=="", "Expected a leading '/' on the request path"
        
        backendname = parts[2]
        
        # no name? just status
        if not backendname and len(parts)==3:
            # status page
            page = "Yabi Exec Connector Resource Version: %s\n"%self.VERSION
            page += "Available backends: "+", ".join(self.backends.keys())
            page += "\n\n"
            return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, page)
        
        # check for backend name
        if backendname not in self.backends:
            return http.Response( responsecode.NOT_FOUND, {'content-type': http_headers.MimeType('text', 'plain')}, "Backend '%s' not found"%backendname)
        
        backend = self.backends[backendname]
        page = "Hello, %s!"%backend
        
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, page)
    
    def locateChild(self, request, segments):
        # return our local file resource for these segments
        if segments[0]=="run":
            # wanting the file copy resource
            return ExecRunResource(request,segments,fsresource = self), []
        
        return resource.Resource.locateChild(self,request,segments)