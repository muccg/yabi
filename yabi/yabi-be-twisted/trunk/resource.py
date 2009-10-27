"""Web2 style resource that is gonna serve our children"""
from twisted.web2 import resource, http_headers, responsecode, http
import os, sys

##
## MANGO child
##

os.environ['TWISTED_MANGO']='1'

MANGO_APP = "yabiadmin"

# Environment setup for your Django project files:
sys.path.append(MANGO_APP)
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings'%MANGO_APP

from twisted.web2 import wsgi
from django.core.handlers.wsgi import WSGIHandler

def application(environ, start):
    os.environ['SCRIPT_NAME']=environ['SCRIPT_NAME']
    if 'DJANGODEV' in environ:
        os.environ['DJANGODEV']=environ['DJANGODEV']
    return WSGIHandler()(environ,start)
    
##
## Filesystem resources
##
from fs.resource import FSResource

# backends

from fs.connector.LocalFilesystem import LocalFilesystem
from fs.connector.GridFTP import GridFTP

##
## Execution resources
##
from ex.resource import ExecResource

# backends
from ex.connector.GlobusConnector import GlobusConnector
from ex.connector.SGEConnector import SGEConnector

VERSION = 0.1
class BaseResource(resource.PostableResource):
    """This is the baseclass for out "/" HTTP resource. It does nothing but defines the various children.
    It is also the location where you hook in you tools, or wsgi apps."""
    addSlash = True
    
    def __init__(self, *args, **kw):
        resource.PostableResource.__init__(self, *args, **kw)
        
        ##
        ## our handlers
        ##
        
        ##
        ## TODO CAVEAT: these backends should be created dynamically based on data pulled from the yabi backend webservice
        ##
        
        # filesystem backends
        self.child_fs = FSResource(
                #file = LocalFileResource(directory="/tmp/filesystem"),
                #gridftp1 = GlobusFileResource(remoteserver="xe-ng2.ivec.org", remotepath="/scratch"),
                #gridftp2 = GlobusFileResource(remoteserver="xe-ng2.ivec.org", remotepath="/scratch/bi01"),
                yabifs = LocalFilesystem(directory="/tmp/filesystem"),
                gridftp = GridFTP()
            )
            
        # execution backends
        #self.child_exec = ExecResource(
                #globus = GlobusConnector(),
                #sge = SGEConnector(),
            #)
            
        # dynamic execution backends
        self.child_exec = ExecResource()
            
        self.child_yabiadmin = wsgi.WSGIResource(application)
        
    def LoadExecConnectors(self):
        self.child_exec.LoadConnectors()
        
    def render(self, ctx):
        """Just returns a helpful text string"""
        return http.Response(responsecode.OK,
                        {'content-type': http_headers.MimeType('text', 'plain')},
                         "Twisted Yabi Core: %s\n"%VERSION)
