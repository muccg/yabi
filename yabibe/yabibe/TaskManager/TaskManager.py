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
from twisted.web import client
from twisted.internet import reactor
import json
import stackless
import random
import os
import pickle

from utils.parsers import parse_url

from TaskTools import Copy, RCopy, Sleep, Log, Status, Exec, Mkdir, Rm, List, UserCreds, GETFailure, CloseConnections

# if debug is on, full tracebacks are logged into yabiadmin
DEBUG = False

# if this is true the backend constantly rants about when it collects the next task
VERBOSE = True

import traceback

from conf import config

from Tasklets import tasklets
from Task import NullBackendTask, MainTask

class CustomTasklet(stackless.tasklet):
    # When this is present, it is called in lieu of __reduce__.
    # As the base tasklet class provides it, we need to as well.
    def __reduce_ex__(self, pickleVersion):
        return self.__reduce__()

    def __reduce__(self):
        # Get into the list that will eventually be returned to
        # __setstate__ and append our own entry into it (the
        # dictionary of instance variables).
        ret = list(stackless.tasklet.__reduce__(self))
        l = list(ret[2])
        l.append(self.__dict__)
        ret[2] = tuple(l)
        result = tuple(ret)
        return result

    def __setstate__(self, l):
        # Update the instance dictionary with the value we added in.
        self.__dict__.update(l[-1])
        # Let the tasklet get on with being reconstituted by giving
        # it the original list (removing our addition).
        return stackless.tasklet.__setstate__(self, l[:-1])

#class CustomTasklet(stackless.tasklet):
    #pass

#CustomTasklet = stackless.tasklet

class TaskManager(object):
    TASK_HOST = "localhost"
    TASK_PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 8000
    TASK_URL = "engine/task/"
    BLOCKED_URL = "engine/blockedtask/"
    
    JOBLESS_PAUSE = 5.0                 # wait this long when theres no more jobs, to try to get another job
    JOB_PAUSE = 0.0                     # wait this long when you successfully got a job, to get the next job
    
    def __init__(self):
        self.pausechannel_task = stackless.channel()
        self.pausechannel_unblock = stackless.channel()
        
        self.tasks = []                 # store all the tasks currently being executed in a list
    
    def start(self):
        """Begin the task manager tasklet. This tasklet continually pops tasks from yabiadmin and sets them up for running"""
        self.runner_thread_task = stackless.tasklet(self.runner)
        self.runner_thread_task.setup()
        self.runner_thread_task.run()
        
        self.runner_thread_unblock = stackless.tasklet(self.unblocker)
        self.runner_thread_unblock.setup()
        self.runner_thread_unblock.run()
                
    def runner(self):
        """The green task that starts up jobs"""
        while True:                 # do forever.
            self.get_next_task()
            
            # wait for this task to start or fail
            Sleep(self.pausechannel_task.receive())
            
    def unblocker(self):
        """green task that checks for blocked jobs that need unblocking"""
        while True:
            self.get_next_unblocked()
            
            # wait for this task to start or fail
            Sleep(self.pausechannel_unblock.receive())
        
    def start_task(self, data):
        try:
            taskdescription=json.loads(data)
            
            print "starting task:",taskdescription['taskid']
            
            if DEBUG:
                print "=========JSON============="
                print json.dumps(taskdescription, sort_keys=True, indent=4)
                print "=========================="
            
            runner_object = None
        
            if parse_url(taskdescription['exec']['backend'])[0].lower()=="null":
                # null backend tasklet runner
                runner_object = NullBackendTask(taskdescription)
            else:
                runner_object = MainTask(taskdescription)
            
            # make the task and run it
            tasklet = CustomTasklet(runner_object.run)
            tasklet.setup()
            
            #add to save list
            tasklets.add(runner_object, taskdescription['taskid'])
            tasklet.run()
            
            # Lets try and start anotherone.
            self.pausechannel_task.send(self.JOB_PAUSE)
            
        except Exception, e:
            # log any exception
            traceback.print_exc()
            raise e

    def start_unblock(self, data):
        try:
            taskdescription=json.loads(data)
            
            print "resuming task:",taskdescription['taskid']
            
            if DEBUG:
                print "=========RESUME==========="
                print json.dumps(taskdescription, sort_keys=True, indent=4)
                print "=========================="
            
            runner_object = tasklets.get(taskdescription['taskid'])
            runner_object.unblock()
           
            # make the task and run it
            tasklet = CustomTasklet(runner_object.run)
            tasklet.setup()
            tasklet.run()
            
            # Lets try and start anotherone.
            self.pausechannel_unblock.send(self.JOB_PAUSE)
            
        except Exception, e:
            # log any exception
            traceback.print_exc()
            raise e
                  
    def get_next_task(self):
         
        useragent = "YabiExec/0.1"
        task_server = "%s://%s:%s" % (config.yabiadminscheme, config.yabiadminserver, config.yabiadminport)
        task_path = os.path.join(config.yabiadminpath, self.TASK_URL)
        task_tag = "?tasktag=%s" % (config.config['taskmanager']['tasktag'])
        task_url = task_server + task_path + task_tag

        if VERBOSE:
            print "Getting next task from:",task_url

        factory = client.HTTPClientFactory(
            url = task_url,
            agent = useragent
            )
        factory.noisy = False
        if VERBOSE:
            print "reactor.connectSSL(",config.yabiadminserver,",",config.yabiadminport,",",os.path.join(config.yabiadminpath,self.TASK_URL),")"
        port = config.yabiadminport
        
        from ServerContextFactory import ServerContextFactory
        reactor.connectSSL(config.yabiadminserver, port, factory, ServerContextFactory())

        # now if the page fails for some reason. deal with it
        def _doFailure(data):
            if VERBOSE:
                print "No more jobs. Sleeping for",self.JOBLESS_PAUSE
            # no more tasks. we should wait for the next task.
            self.pausechannel_task.send(self.JOBLESS_PAUSE)
            
        d = factory.deferred.addCallback(self.start_task).addErrback(_doFailure)
        return d
        
    def get_next_unblocked(self):
        useragent = "YabiExec/0.1"
        task_server = "%s://%s:%s" % (config.yabiadminscheme, config.yabiadminserver, config.yabiadminport)
        task_path = os.path.join(config.yabiadminpath, self.BLOCKED_URL)
        task_tag = "?tasktag=%s" % (config.config['taskmanager']['tasktag'])
        task_url = task_server + task_path + task_tag

        factory = client.HTTPClientFactory(
            url = task_url,
            agent = useragent
            )
        factory.noisy = False
        if VERBOSE:
            print "reactor.connectTCP(",config.yabiadminserver,",",config.yabiadminport,",",os.path.join(config.yabiadminpath,self.TASK_URL),")"
        port = config.yabiadminport
        reactor.connectTCP(config.yabiadminserver, port, factory)

        # now if the page fails for some reason. deal with it
        def _doFailure(data):
            if VERBOSE:
                print "No more unblock requests. Sleeping for",self.JOBLESS_PAUSE
            # no more tasks. we should wait for the next task.
            self.pausechannel_unblock.send(self.JOBLESS_PAUSE)
            
        d = factory.deferred.addCallback(self.start_unblock).addErrback(_doFailure)
        return d
        
