# -*- coding: utf-8 -*-

import TaskManager

Tasks = TaskManager.TaskManager()

from Tasklets import tasklets

from conf import config

def startup():
    """Start up the TaskManager, so it can go and get some jobs..."""
    print "Starting TaskManager..."
    Tasks.start()
    
    # load up saved tasklets
    print "Loading Tasks..."
    tasklets.load(directory=config.config['backend']['tasklets'])
    
def shutdown():
    """pickle tasks to disk"""
    print "Saving tasklets..."
    tasklets.save(directory=config.config['backend']['tasklets'])

from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref
import sys, os

from FileCopyResource import FileCopyResource
from FileRCopyResource import FileRCopyResource
from FileDeleteResource import FileDeleteResource
from FileListResource import FileListResource
from FileMkdirResource import FileMkdirResource
from FilePutResource import FilePutResource
from FileGetResource import FileGetResource
from FileUploadResource import UploadTicket, FileUploadResource, UploadStatus

from utils.BackendResource import BackendResource

class TaskManagerResource(resource.Resource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.2
    addSlash = True
    
    def __init__(self,*args,**kwargs):
        resource.Resource.__init__(self,*args,**kwargs)
    
    def render(self, request):
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, Tasks.debug())
    