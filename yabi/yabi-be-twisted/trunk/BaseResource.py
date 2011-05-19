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
"""Web2 style resource that is gonna serve our children"""
from twisted.web2 import resource, http_headers, responsecode, http
import os, sys

##
## Filesystem resources
##
from fs.resource import FSResource

# backends

#from fs.connector.LocalFilesystem import LocalFilesystem
from fs.connector.GridFTP import GridFTP
from fs.connector.SSHFilesystem import SSHFilesystem
from fs.connector.S3Filesystem import S3Filesystem

##
## Execution resources
##
from ex.resource import ExecResource

# backends
from ex.connector.GlobusConnector import GlobusConnector
from ex.connector.SGEConnector import SGEConnector
from ex.connector.TorqueConnector import TorqueConnector
from ex.connector.SSHConnector import SSHConnector

# taskmanager debug
from TaskManager import TaskManagerResource, TaskManagerPickleResource

VERSION = 0.2
class BaseResource(resource.PostableResource):
    """This is the baseclass for out "/" HTTP resource. It does nothing but defines the various children.
    It is also the location where you hook in you tools, or wsgi apps."""
    addSlash = True
    
    def __init__(self, *args, **kw):
        resource.PostableResource.__init__(self, *args, **kw)
        
        ##
        ## our handlers
        ##
        self.child_fs = FSResource()
        self.child_exec = ExecResource()
        
        #  debug for taskmanager
        self.child_debug = TaskManagerResource()
        self.child_pickle = TaskManagerPickleResource()
        
    def LoadExecConnectors(self, quiet=False):
        self.child_exec.LoadConnectors(quiet)
        
    def LoadFSConnectors(self, quiet=False):
        self.child_fs.LoadConnectors(quiet)
        
    def LoadConnectors(self, quiet=False):
        self.LoadExecConnectors(quiet)
        self.LoadFSConnectors(quiet)
        
    def render(self, ctx):
        """Just returns a helpful text string"""
        return http.Response(responsecode.OK,
                        {'content-type': http_headers.MimeType('text', 'plain')},
                         "Twisted Yabi Core: %s\n"%VERSION)
                         
    def shutdown(self):
        """send signal to each backend that needs info to be written to disk on shutdown.
        at the moment this is only execution backends that are capable of job resumption
        """
        self.child_exec.shutdown()
        
    def startup(self):
        """startup each backend that needs it"""
        self.child_exec.startup()
