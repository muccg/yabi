# -*- coding: utf-8 -*-

import TaskManager

Tasks = TaskManager.TaskManager()

from Tasklets import tasklets

from conf import config

import stackless

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
    
    for i in range(20):
        stackless.schedule()
    
    tasklets.save(directory=config.config['backend']['tasklets'])

from twisted.web2 import resource, http_headers, responsecode, http, server
from twisted.internet import defer, reactor
import weakref
import sys, os

class TaskManagerResource(resource.Resource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.2
    addSlash = True
    
    def __init__(self,*args,**kwargs):
        resource.Resource.__init__(self,*args,**kwargs)
    
    def render(self, request):
        tasklets.purge()
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, tasklets.debug())

class TaskManagerPickleResource(resource.Resource):
    """This is the resource that connects to all the filesystem backends"""
    VERSION=0.2
    addSlash = True
    
    def __init__(self,*args,**kwargs):
        resource.Resource.__init__(self,*args,**kwargs)
    
    def render(self, request):
        tasklets.purge()
        stackless.schedule()
        return http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, tasklets.pickle())
    