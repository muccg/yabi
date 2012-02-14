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
"""Our twisted filesystem server resource"""

from twistedweb2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref
import sys, os

from FileCopyResource import FileCopyResource, FileCopyProgressResource
from FileRCopyResource import FileRCopyResource
from FileDeleteResource import FileDeleteResource
from FileListResource import FileListResource
from FileMkdirResource import FileMkdirResource
from FileLinkResource import FileLinkResource
from FileLCopyResource import FileLCopyResource
from FilePutResource import FilePutResource
from FileGetResource import FileGetResource
from FileUploadResource import UploadTicket, FileUploadResource, UploadStatus

from utils.BackendResource import BackendResource

class FSResource(resource.Resource, BackendResource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.2
    addSlash = True
    
    def __init__(self,*args,**kwargs):
        BackendResource.__init__(self,*args,**kwargs)
    
    def LoadConnectors(self, quiet=False):
        """Load all the backend connectors into our backends"""
        import connector
        return BackendResource.LoadConnectors(self,connector,'FSConnector','fs', quiet=quiet)
    
    def render(self, request):
        # break our request path into parts
        parts = request.path.split("/")
        assert parts[0]=="", "Expected a leading '/' on the request path"
        
        backendname = parts[2]
        
        # no name? just status
        if not backendname and len(parts)==3:
            # status page
            page = "Yabi Filesystem Connector Resource Version: %s\n"%self.VERSION
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
        if segments[0]=="copy":
            # wanting the file copy resource
            return FileCopyResource(request,segments,fsresource = self), []
        elif segments[0]=="copyprogress":
            # wanting the file copy resource
            return FileCopyProgressResource(), []
        elif segments[0]=="mkdir":
            return FileMkdirResource(request,segments,fsresource=self), []
        elif segments[0]=="ls":
            return FileListResource(request,segments,fsresource=self), []
        elif segments[0]=="ln":
            return FileLinkResource(request,segments,fsresource=self), []
        elif segments[0]=="lcopy":
            return FileLCopyResource(request,segments,fsresource=self), []
        elif segments[0]=="rm":
            return FileDeleteResource(request,segments,fsresource=self), []
        elif segments[0]=="rcopy":
            return FileRCopyResource(request,segments,fsresource=self), []
        elif segments[0]=="put":
            return FilePutResource(request,segments,fsresource=self), []
        elif segments[0]=="get":
            return FileGetResource(request,segments,fsresource=self), []
        elif segments[0]=="uploadstatus":
            return UploadStatus(request, segments, fsresource=self), []
        elif segments[0]=="ticket":
            return UploadTicket(request, segments, fsresource=self), []
        elif segments[0]=="upload":
            return FileUploadResource(request, segments, fsresource=self), segments[1:]
        
                
        return resource.Resource.locateChild(self,request,segments)