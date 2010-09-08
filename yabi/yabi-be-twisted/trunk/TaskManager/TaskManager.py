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
        return tuple(ret)

    def __setstate__(self, l):
        # Update the instance dictionary with the value we added in.
        self.__dict__.update(l[-1])
        # Let the tasklet get on with being reconstituted by giving
        # it the original list (removing our addition).
        return stackless.tasklet.__setstate__(self, l[:-1])

#class CustomTasklet(stackless.tasklet):
    #pass

CustomTasklet = stackless.tasklet

class TaskManager(object):
    TASK_HOST = "localhost"
    TASK_PORT = int(os.environ['PORT']) if 'PORT' in os.environ else 8000
    TASK_URL = "engine/task/"
    
    JOBLESS_PAUSE = 5.0                 # wait this long when theres no more jobs, to try to get another job
    JOB_PAUSE = 0.0                     # wait this long when you successfully got a job, to get the next job
    
    def __init__(self):
        self.pausechannel = stackless.channel()
    
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
        taskdescription=json.loads(data)
        
        print "starting task:",taskdescription['taskid']
        
        runner = None
       
        if parse_url(taskdescription['exec']['backend'])[0].lower()=="null":
            # null backend tasklet runner
            runner = self.task_nullbe
        
        # make the task and run it
        tasklet = CustomTasklet(self.task)
        tasklet.setup(taskdescription, runner)
        
        #add to save list
        tasklets.add(tasklet)
        
        tasklet.run()
        
        # task successfully started. Lets try and start anotherone.
        self.pausechannel.send(self.JOB_PAUSE)
         
         
    def get_next_task(self):
         
        useragent = "YabiExec/0.1"
        
        factory = client.HTTPClientFactory(
            os.path.join(config.yabiadminpath,self.TASK_URL+"?origin=%s:%s"%tuple(config.config['backend']['port'])),
            agent = useragent
            )
        factory.noisy = False
        if VERBOSE:
            print "reactor.connectTCP(",config.yabiadminserver,",",config.yabiadminport,",",os.path.join(config.yabiadminpath,self.TASK_URL),")"
        reactor.connectTCP(config.yabiadminserver, config.yabiadminport, factory)
        
        
        
        # now if the page fails for some reason. deal with it
        def _doFailure(data):
            #print "No more jobs. Sleeping for",self.JOBLESS_PAUSE
            # no more tasks. we should wait for the next task.
            self.pausechannel.send(self.JOBLESS_PAUSE)
            
        return factory.deferred.addCallback(self.start_task).addErrback(_doFailure)
        
    def task(self,task, taskrunner=None):
        """Entry point for Task tasklet"""
        taskid = task['taskid']
        if not taskrunner:
            taskrunner=self.task_mainline
        try:
            return taskrunner(task)
        except Exception, exc:
            print "TASK[%s] raised uncaught exception: %s"%(taskid,exc)
            traceback.print_exc()
            if DEBUG:
                Log(task['errorurl'],"Raised uncaught exception: %s"%(traceback.format_exc()))
            else:
                Log(task['errorurl'],"Raised uncaught exception: %s"%(exc))
            Status(task['statusurl'],"error")
        
    def task_nullbe(self, task):
        """ Our special copy case for null backend"""
        print "=========NULL============="
        print json.dumps(task, sort_keys=True, indent=4)
        print "=========================="
        
        # stage in file
        taskid = task['taskid']
        
        statusurl = task['statusurl']
        errorurl = task['errorurl']
        yabiusername = task['yabiusername']
        
        # sanity check...
        for key in ['errorurl','exec','stagein','stageout','statusurl','taskid','yabiusername']:
            assert key in task, "Task JSON description is missing a vital key '%s'"%key
        
        # check the exec section
        for key in ['backend', 'command', 'fsbackend', 'workingdir']:
            assert key in task['exec'], "Task JSON description is missing a vital key inside the 'exec' section. Key name is '%s'"%key
        
        # shortcuts for our status and log calls
        status = lambda x: Status(statusurl,x)
        log = lambda x: Log(errorurl,x)
        
        # check if exec scheme is null backend. If this is the case, we need to run our special null backend tasklet
        scheme, address = parse_url(task['exec']['backend'])
        assert scheme.lower() == "null"
           
        log("null backend... skipping task and copying files")
           
        # make sure we have the stageout directory
        log("making stageout directory %s"%task['stageout'])
        if DEBUG:
            print "STAGEOUT:",task['stageout']
        try:
            Mkdir(task['stageout'], yabiusername=yabiusername)
        except GETFailure, error:
            pass
        
        dst = task['stageout']
              
        # for each stagein, copy to stageout NOT the stagein destination
        status("stagein")
        for copy in task['stagein']:
            src = copy['src']
            
            # check that destination directory exists.
            scheme,address = parse_url(dst)
            
            directory, file = os.path.split(address.path)
            remotedir = scheme+"://"+address.netloc+directory
            if DEBUG:
                print "CHECKING remote:",remotedir
            try:
                listing = List(remotedir, yabiusername=yabiusername)
                if DEBUG:
                    print "list result:", listing
            except Exception, error:
                # directory does not exist
                print "Remote DIR does not exist"
                
                #make dir
                Mkdir(remotedir, yabiusername=yabiusername)
            
            if src.endswith("/"):
                log("RCopying %s to %s..."%(src,dst))
                try:
                    RCopy(src,dst, yabiusername=yabiusername)
                    log("RCopying %s to %s Success"%(src,dst))
                except GETFailure, error:
                    # error copying!
                    print "TASK[%s]: RCopy %s to %s Error!"%(taskid,src,dst)
                    status("error")
                    log("RCopying %s to %s failed: %s"%(src,dst, error))
                    return              # finish task
            
                print "TASK[%s]: RCopy %s to %s Success!"%(taskid,src,dst)
            else:
                log("Copying %s to %s..."%(src,dst))
                try:
                    Copy(src,dst, yabiusername=yabiusername)
                    log("Copying %s to %s Success"%(src,dst))
                except GETFailure, error:
                    # error copying!
                    print "TASK[%s]: Copy %s to %s Error!"%(taskid,src,dst)
                    status("error")
                    log("Copying %s to %s failed: %s"%(src,dst, error))
                    return              # finish task
            
                print "TASK[%s]: Copy %s to %s Success!"%(taskid,src,dst)
            
        
        status("complete")              # null backends are always marked complete
        
        
    def task_mainline(self, task):
        """Our top down greenthread code"""
        print "=========JSON============="
        print json.dumps(task, sort_keys=True, indent=4)
        print "=========================="
        
        # stage in file
        taskid = task['taskid']
        
        statusurl = task['statusurl']
        errorurl = task['errorurl']
        yabiusername = task['yabiusername']
        
        # sanity check...
        for key in ['errorurl','exec','stagein','stageout','statusurl','taskid','yabiusername']:
            assert key in task, "Task JSON description is missing a vital key '%s'"%key
        
        # check the exec section
        for key in ['backend', 'command', 'fsbackend', 'workingdir']:
            assert key in task['exec'], "Task JSON description is missing a vital key inside the 'exec' section. Key name is '%s'"%key
        
        # shortcuts for our status and log calls
        status = lambda x: Status(statusurl,x)
        log = lambda x: Log(errorurl,x)
        
        # check if exec scheme is null backend. If this is the case, we need to run our special null backend tasklet
        scheme, address = parse_url(task['exec']['backend'])
        if scheme.lower() == "null":
            log("null backend... skipping task and copying files")
            
            status("complete")              # null backends are always marked complete
            return                          # exit this task
        
        status("stagein")
        for copy in task['stagein']:
            src = copy['src']
            dst = copy['dst']
            
            # check that destination directory exists.
            scheme,address = parse_url(dst)
            
            directory, file = os.path.split(address.path)
            remotedir = scheme+"://"+address.netloc+directory
            if DEBUG:
                print "CHECKING remote:",remotedir
            try:
                listing = List(remotedir, yabiusername=yabiusername)
                if DEBUG:
                    print "list result:", listing
            except Exception, error:
                # directory does not exist
                print "Remote DIR does not exist"
                
                #make dir
                Mkdir(remotedir, yabiusername=yabiusername)
            
            log("Copying %s to %s..."%(src,dst))
            try:
                Copy(src,dst, yabiusername=yabiusername)
                log("Copying %s to %s Success"%(src,dst))
            except GETFailure, error:
                # error copying!
                print "TASK[%s]: Copy %s to %s Error!"%(taskid,src,dst)
                status("error")
                log("Copying %s to %s failed: %s"%(src,dst, error))
                return              # finish task
           
            print "TASK[%s]: Copy %s to %s Success!"%(taskid,src,dst)
        
        # get our credential working directory. We lookup the execution backends auth proxy cache, and get the users home directory from that
        # this comes from their credentials.
        
        scheme, address = parse_url(task['exec']['backend'])
        usercreds = UserCreds(yabiusername, task['exec']['backend'])
        #homedir = usercreds['homedir']
        workingdir = task['exec']['workingdir']
        
        assert address.path=="/", "Error. JSON[exec][backend] has a path. Execution backend URI's must not have a path (path is %s)"%address.path 
        
        if DEBUG:
            print "USERCREDS",usercreds
                
        # make our working directory
        status("mkdir")
        
        #fsscheme, fsaddress = parse_url(task['exec']['fsbackend'])
        #mkuri = fsscheme+"://"+fsaddress.username+"@"+fsaddress.hostname+workingdir
        fsbackend = task['exec']['fsbackend']
        
        outputuri = fsbackend + ("/" if not fsbackend.endswith('/') else "") + "output/"
        outputdir = workingdir + ("/" if not workingdir.endswith('/') else "") + "output/"
        
        print "Making directory",outputuri
        #self._tasks[stackless.getcurrent()]=workingdir
        try:
            Mkdir(outputuri, yabiusername=yabiusername)
        except GETFailure, error:
            # error making directory
            print "TASK[%s]:Mkdir failed!"%(taskid)
            status("error")
            log("Making working directory of %s failed: %s"%(outputuri,error))
            return 
        
        # now we are going to run the job
        status("exec")
        
        retry=True
        while retry:
            retry=False
            
            try:
                # callback for job execution status change messages
                def _task_status_change(line):
                    """Each line that comes back from the webservice gets passed into this callback"""
                    line = line.strip()
                    if DEBUG:
                        print "_task_status_change(",line,")"
                    log("Remote execution backend changed status to: %s"%(line))
                    status("exec:%s"%(line.lower()))
                
                # submit the job to the execution middle ware
                log("Submitting to %s command: %s"%(task['exec']['backend'],task['exec']['command']))
                
                try:
                    uri = task['exec']['backend']+outputdir
                    
                    # create extra parameter list
                    extras = {}
                    for key in [ 'cpus', 'job_type', 'max_memory', 'module', 'queue', 'walltime' ]:
                        if key in task['exec'] and task['exec'][key]:
                            extras[key]=task['exec'][key]
                    
                    Exec(uri, command=task['exec']['command'], stdout="STDOUT.txt",stderr="STDERR.txt", callbackfunc=_task_status_change, yabiusername=yabiusername, **extras)                # this blocks untill the command is complete.
                    log("Execution finished")
                except GETFailure, error:
                    # error executing
                    print "TASK[%s]: Execution failed!"%(taskid)
                    status("error")
                    log("Execution of %s on %s failed: %s"%(task['exec']['command'],task['exec']['backend'],error))
                    return              # finish task
            except CloseConnections, cc:
                print "CLOSECONNECTIONS",cc
                retry=True
                
            stackless.schedule()
        
        # stageout
        log("Staging out results")
        status('stageout')
        
        # recursively copy the working directory to our stageout area
        log("Staging out remote %s to %s..."%(outputdir,task['stageout']))
        
        # make sure we have the stageout directory
        log("making stageout directory %s"%task['stageout'])
        if DEBUG:
            print "STAGEOUT:",task['stageout']
        try:
            Mkdir(task['stageout'], yabiusername=yabiusername)
        except GETFailure, error:
            pass
        
        try:
            RCopy(outputuri,task['stageout'], yabiusername=yabiusername)
            log("Files successfuly staged out")
        except GETFailure, error:
            # error executing
            print "TASK[%s]: Stageout failed!"%(taskid)
            status("error")
            if DEBUG:
                log("Staging out remote %s to %s failed... \n%s"%(outputuri,task['stageout'],traceback.format_exc()))
            else:
                log("Staging out remote %s to %s failed... %s"%(outputuri,task['stageout'],error))
            return              # finish task
        
        # cleanup
        status("cleaning")
        log("Cleaning up job...")
        
        # cleanup working dir
        for copy in task['stagein']:
            dst_url = fsbackend
            log("Deleting %s..."%(dst_url))
            try:
                if DEBUG:
                    print "RM1:",dst_url
                Rm(dst_url, yabiusername=yabiusername, recurse=True)
            except GETFailure, error:
                # error deleting. This is logged but is non fatal
                print "TASK[%s]: Delete %s Error!"%(taskid, dst_url)
                #status("error")
                log("Deleting %s failed: %s"%(dst_url, error))
                #return              # finish task
        
        log("Job completed successfully")
        status("complete")
        
        
