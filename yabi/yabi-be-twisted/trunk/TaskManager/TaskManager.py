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
VERBOSE = False

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
    
    JOBLESS_PAUSE = 5.0                 # wait this long when theres no more jobs, to try to get another job
    JOB_PAUSE = 0.0                     # wait this long when you successfully got a job, to get the next job
    
    def __init__(self):
        self.pausechannel = stackless.channel()
        
        self.tasks = []                 # store all the tasks currently being executed in a list
    
    def start(self):
        """Begin the task manager tasklet. This tasklet continually pops tasks from yabiadmin and sets them up for running"""
        self.runner_thread = stackless.tasklet(self.runner)
        self.runner_thread.setup()
        self.runner_thread.run()
        
    def runner(self):
        """The green task that starts up jobs"""
        while True:                 # do forever.
            self.get_next_task()
            
            # wait for this task to start or fail
            Sleep(self.pausechannel.receive())
        
    def start_task(self, data):
        try:
            taskdescription=json.loads(data)
            
            print "starting task:",taskdescription['taskid']
            
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
            tasklets.add(runner_object)
            tasklet.run()
            
            # Lets try and start anotherone.
            self.pausechannel.send(self.JOB_PAUSE)
            
        except Exception, e:
            # log any exception
            traceback.print_exc()
            raise e
         
    def get_next_task(self):
         
        useragent = "YabiExec/0.1"
        task_server = "%s://%s:%s" % (config.yabiadminscheme, config.yabiadminserver, config.yabiadminport)
        task_path = os.path.join(config.yabiadminpath, self.TASK_URL)
        task_origin = "?origin=%s:%s" % tuple(config.config['backend']['port'])
        task_url = task_server + task_path + task_origin

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
            print "No more jobs. Sleeping for",self.JOBLESS_PAUSE
            # no more tasks. we should wait for the next task.
            self.pausechannel.send(self.JOBLESS_PAUSE)
            
        d = factory.deferred.addCallback(self.start_task).addErrback(_doFailure)
        return d
        
