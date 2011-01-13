# -*- coding: utf-8 -*-
import json
import stackless
import random
import os
import pickle

from utils.parsers import parse_url

from TaskTools import Copy, RCopy, Sleep, Log, Status, Exec, Resume, Mkdir, Rm, List, UserCreds, GETFailure, CloseConnections

import traceback
from Exceptions import BlockingException

DEBUG = True

class TaskFailed(Exception):
    pass

class Task(object):
    def __init__(self, json=None):
        self.blocked_stage = None
        
        # stage in file
        if json:
            self.load_json(json)
        
    def load_json(self, json, stage=0):
        self.json = json
        
        # check json is okish
        self._sanity_check()
                
        self.taskid = json['taskid']
        self.statusurl = json['statusurl']
        self.errorurl = json['errorurl']
        self.yabiusername = json['yabiusername']
                
        # shortcuts for our status and log calls
        self.status = lambda x: Status(self.statusurl,x)
        self.log = lambda x: Log(self.errorurl,x)
        
        # stage keeps track of where we are in completing the tasklet, so if we need to restart we can skip
        # parts that are already completed
        self.stage = stage
    
    def run(self):
        try:
            self.main()
        except BlockingException, be:
            # this is to deal with a problem that is temporary and leads to a blocked status
            self._blocked()
            traceback.print_exc()
            self.log("Task moved into blocking state: %s"%be)
            self.status("blocked")
            
        except GETFailure, gf:
            if '503' in gf.message[1]:
                # blocked!
                #print "BLOCKED"
                self._blocked()
                traceback.print_exc()
                self.log("Task moved into blocking state: %s"%gf)
                self.status("blocked")
            else:
                #print "ERROR"
                self._errored()
                traceback.print_exc()
                self.log("Task raised GETFailure: %s"%gf)
                self.status("error")
            
        except Exception, e:
            self._errored()
            traceback.print_exc()
            self.log("Task raised exception: %s"%e)
            self.status("error")
    
    
    def _next_stage(self):
        """Move to the next stage of the tasklet"""
        self.stage += 1
        
    def _set_stage(self, stage):
        self.stage = stage
        
    def _end_stage(self):
        """Mark as ended"""
        self.stage = -1
        
    def _errored(self):
        self.stage = -2

    def _blocked(self):
        # move to blocked. keep the old stage stored
        self.blocked_stage = self.stage
        self.stage = -3
        
    def unblock(self):
        # for a job that is sitting in blocking, move it back out and into its last execution stage
        assert self.blocked_stage != None, "Trying to unblock a task that was never blocked"
        self.stage = self.blocked_stage
        self.blocked_stage = None
        
    def finished(self):
        return self.stage == -1
        
    def errored(self):
        return self.stage == -2

    def blocked(self):
        return self.stage == -3

    def _sanity_check(self):
        # sanity check...
        for key in ['errorurl','exec','stagein','stageout','statusurl','taskid','yabiusername']:
            assert key in self.json, "Task JSON description is missing a vital key '%s'"%key
        
        # check the exec section
        for key in ['backend', 'command', 'fsbackend', 'workingdir']:
            assert key in self.json['exec'], "Task JSON description is missing a vital key inside the 'exec' section. Key name is '%s'"%key
           
class NullBackendTask(Task):
    def load_json(self, json, stage=0):
        Task.load_json(self, json, stage)
        
        # check if exec scheme is null backend. If this is the case, we need to run our special null backend tasklet
        scheme, address = parse_url(json['exec']['backend'])
        assert scheme.lower() == "null"
    
    def main(self):
        
        if self.stage == 0:
            self.log("null backend... skipping task and copying files")
           
            self.log("making stageout directory %s"%self.json['stageout'])
            self.make_stageout()
        
            self._next_stage()
        
        if self.stage == 1:
            self.status("stagein")
            self.stage_in_files()

            self._next_stage()

        if self.stage == 2:
            self.status("complete")              # null backends are always marked complete

            self._end_stage()

    def make_stageout(self):
        stageout = self.json['stageout']
        
        if DEBUG:
            print "STAGEOUT:",stageout
        try:
            Mkdir(stageout, yabiusername=self.yabiusername)
        except GETFailure, error:
            raise BlockingException("Make directory failed: %s"%error.message[2])
        
    def stage_in_files(self):
        dst = self.json['stageout']
        status = self.status
        log = self.log
        
        # for each stagein, copy to stageout NOT the stagein destination
        for copy in self.json['stagein']:
            src = copy['src']
            
            # check that destination directory exists.
            scheme,address = parse_url(dst)
            
            directory, file = os.path.split(address.path)
            remotedir = scheme+"://"+address.netloc+directory
            if DEBUG:
                print "CHECKING remote:",remotedir
            try:
                listing = List(remotedir, yabiusername=self.yabiusername)
                if DEBUG:
                    print "list result:", listing
            except Exception, error:
                # directory does not exist
                #make dir
                try:
                    Mkdir(remotedir, yabiusername=self.yabiusername)
                except GETFailure, gf:
                    if DEBUG:
                        print "GF_",dir(gf),gf.args,"=====",gf.message
                    raise BlockingException("Make directory failed: %s"%gf.message[2])
            
            if src.endswith("/"):
                log("RCopying %s to %s..."%(src,dst))
                try:
                    RCopy(src,dst, yabiusername=self.yabiusername)
                    log("RCopying %s to %s Success"%(src,dst))
                except GETFailure, error:
                    # error copying!
                    print "TASK[%s]: RCopy %s to %s Error!"%(self.taskid,src,dst)
                    status("error")
                    log("RCopying %s to %s failed: %s"%(src,dst, error))
                    return              # finish task
            
                print "TASK[%s]: RCopy %s to %s Success!"%(self.taskid,src,dst)
            else:
                log("Copying %s to %s..."%(src,dst))
                try:
                    Copy(src,dst, yabiusername=self.yabiusername)
                    log("Copying %s to %s Success"%(src,dst))
                except GETFailure, error:
                    # error copying!
                    print "TASK[%s]: Copy %s to %s Error!"%(self.taskid,src,dst)
                    status("error")
                    log("Copying %s to %s failed: %s"%(src,dst, error))
                    return              # finish task
            
                print "TASK[%s]: Copy %s to %s Success!"%(self.taskid,src,dst)
            
class MainTask(Task):
    STAGEIN = 0
    MKDIR = 1
    EXEC = 2
    STAGEOUT = 3
    CLEANUP = 4
    
    def __init__(self, json=None):
        Task.__init__(self,json)
        
        # for resuming started backend execution jobs
        self._jobid = None
    
    def load_json(self, json, stage=0):
        Task.load_json(self, json, stage)
        
        # check if exec scheme is null backend. If this is the case, we need to run our special null backend tasklet
        scheme, address = parse_url(json['exec']['backend'])
        assert scheme.lower() != "null"
           
    def main(self):
        
        if self.stage == self.STAGEIN:
            self.status("stagein")
            self.stage_in_files()
                
            self._next_stage()
                
        if self.stage == self.MKDIR:
            # make our working directory
            self.status("mkdir")
            self.outuri, self.outdir = self.mkdir()                     # make the directories we are working in
        
            self._next_stage()
        
        if self.stage == self.EXEC:
            # now we are going to run the job
            self.status("exec")
            if self._jobid is None:
                # start a fresh taskjob
                print "Executing fresh:",self._jobid
                self.execute(self.outdir)                        # TODO. implement picking up on this exec task without re-running it??
        
            else:
                # reconnect with this taskjob
                print "Reconnecting with taskjob:",self._jobid
                self.resume(self.outdir)
        
            self._set_stage(self.STAGEOUT)
        
        if self.stage == self.STAGEOUT:
            # stageout
            self.log("Staging out results")
            self.status('stageout')
        
            # recursively copy the working directory to our stageout area
            self.log("Staging out remote %s to %s..."%(self.outdir,self.json['stageout']))
        
            # make sure we have the stageout directory
            self.log("making stageout directory %s"%self.json['stageout'])
        
            self.stageout(self.outuri)
        
            self._next_stage()
            
        if self.stage == self.CLEANUP:
        
            # cleanup
            self.status("cleaning")
            self.log("Cleaning up job...")
        
            self.cleanup()
        
            self.log("Job completed successfully")
            self.status("complete")
            
            self._end_stage()
        
    def stage_in_files(self):
        task = self.json
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
                listing = List(remotedir, yabiusername=self.yabiusername)
                if DEBUG:
                    print "list result:", listing
            except Exception, error:
                # directory does not exist
                #make dir
                Mkdir(remotedir, yabiusername=self.yabiusername)
            
            self.log("Copying %s to %s..."%(src,dst))
            try:
                Copy(src,dst, yabiusername=self.yabiusername)
                self.log("Copying %s to %s Success"%(src,dst))
            except GETFailure, error:
                if "503" in error.message[1]:
                    raise                               # reraise a blocking error so our top level catcher will catch it and block the task
                # error copying!
                print "TASK[%s]: Copy %s to %s Error!"%(self.taskid,src,dst)
                self.status("error")
                self.log("Copying %s to %s failed: %s"%(src,dst, error))
                
                raise TaskFailed("Stage In failed")
        
            print "TASK[%s]: Copy %s to %s Success!"%(self.taskid,src,dst)
        
    def mkdir(self):
        task=self.json
        
        # get our credential working directory. We lookup the execution backends auth proxy cache, and get the users home directory from that
        # this comes from their credentials.
        scheme, address = parse_url(task['exec']['backend'])
        usercreds = UserCreds(self.yabiusername, task['exec']['backend'])
        workingdir = task['exec']['workingdir']
        
        assert address.path=="/", "Error. JSON[exec][backend] has a path. Execution backend URI's must not have a path (path is %s)"%address.path 
        
        if DEBUG:
            print "USERCREDS",usercreds
        
        fsbackend = task['exec']['fsbackend']
        
        outputuri = fsbackend + ("/" if not fsbackend.endswith('/') else "") + "output/"
        outputdir = workingdir + ("/" if not workingdir.endswith('/') else "") + "output/"
        
        print "Making directory",outputuri
        #self._tasks[stackless.getcurrent()]=workingdir
        try:
            Mkdir(outputuri, yabiusername=self.yabiusername)
        except GETFailure, error:
            if "503" in error.message[1]:
                    raise                               # reraise a blocking error so our top level catcher will catch it and block the task
            # error making directory
            print "TASK[%s]:Mkdir failed!"%(self.taskid)
            self.status("error")
            self.log("Making working directory of %s failed: %s"%(outputuri,error))
            
            raise TaskFailed("Mkdir failed")
        
        return outputuri,outputdir
        
    def execute(self, outputdir):
        task=self.json
        retry=True
        while retry:
            retry=False
            
            try:
                exec_status = [None]
                
                # callback for job execution status change messages
                def _task_status_change(line):
                    """Each line that comes back from the webservice gets passed into this callback"""
                    line = line.strip()
                    if DEBUG:
                        print "_task_status_change(",line,")"
                    self.log("Remote execution backend sent status message: %s"%(line))
                    
                    # check for job id number
                    if line.startswith("id") and '=' in line:
                        key,value = line.split("=")
                        value = value.strip()
                        
                        print "execution job given ID:",value
                        self._jobid = value
                        #self.remote_id(value)                           # TODO:send this id back to the middleware
                    else:
                        exec_status[0] = line.lower()
                        self.status("exec:%s"%(exec_status[0]))
                
                # submit the job to the execution middle ware
                self.log("Submitting to %s command: %s"%(task['exec']['backend'],task['exec']['command']))
                
                try:
                    uri = task['exec']['backend']+outputdir
                    
                    # create extra parameter list
                    extras = {}
                    for key in [ 'cpus', 'job_type', 'max_memory', 'module', 'queue', 'walltime' ]:
                        if key in task['exec'] and task['exec'][key]:
                            extras[key]=task['exec'][key]
                    
                    Exec(uri, command=task['exec']['command'], remote_info=task['remoteinfourl'],stdout="STDOUT.txt",stderr="STDERR.txt", callbackfunc=_task_status_change, yabiusername=self.yabiusername, **extras)     # this blocks untill the command is complete. or the execution errored
                    print "EXEC_STATUS",exec_status
                    if exec_status[0] == 'error':
                        print "TASK[%s]: Execution failed!"%(self.taskid)
                        self.status("error")
                        self.log("Execution of %s on %s failed: %s"%(task['exec']['command'],task['exec']['backend'],error))
                        
                        # finish task
                        raise TaskFailed("Execution failed")
                    else:
                        self.log("Execution finished")
                except GETFailure, error:
                    if "503" in error.message[1]:
                        raise                               # reraise a blocking error so our top level catcher will catch it and block the task
                    # error executing
                    print "TASK[%s]: Execution failed!"%(self.taskid)
                    self.status("error")
                    self.log("Execution of %s on %s failed: %s"%(task['exec']['command'],task['exec']['backend'],error))
                    
                    # finish task
                    raise TaskFailed("Execution failed")
                
            except CloseConnections, cc:
                retry=True
                
            stackless.schedule()

    def resume(self, outputdir):
        task=self.json
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
                    self.log("Remote execution backend sent status message: %s"%(line))
                    
                    # check for job id number
                    if line.startswith("id") and '=' in line:
                        key,value = line.split("=")
                        value = value.strip()
                        
                        print "execution job RE-given ID:",value
                        self._jobid = value
                    else:
                        self.status("exec:%s"%(line.lower()))
                
                # submit the job to the execution middle ware
                self.log("Submitting to %s command: %s"%(task['exec']['backend'],task['exec']['command']))
                
                try:
                    uri = task['exec']['backend']+outputdir

                    # create extra parameter list
                    extras = {}
                    for key in [ 'cpus', 'job_type', 'max_memory', 'module', 'queue', 'walltime' ]:
                        if key in task['exec'] and task['exec'][key]:
                            extras[key]=task['exec'][key]
                    
                    Resume(self._jobid, uri, command=task['exec']['command'], stdout="STDOUT.txt",stderr="STDERR.txt", callbackfunc=_task_status_change, yabiusername=self.yabiusername, **extras)                # this blocks untill the command is complete.
                    self.log("Execution finished")
                except GETFailure, error:
                    if "503" in error.message[1]:
                        raise                               # reraise a blocking error so our top level catcher will catch it and block the task
                    # error executing
                    print "TASK[%s]: Execution failed!"%(self.taskid)
                    self.status("error")
                    self.log("Resumption of %s on %s failed: %s"%(task['exec']['command'],task['exec']['backend'],error))
                    
                    # finish task
                    raise TaskFailed("Execution failed: %s"%(error))

            except CloseConnections, cc:
                retry=True
                
            stackless.schedule()
        
    def stageout(self,outputuri):
        task=self.json
        if DEBUG:
            print "STAGEOUT:",task['stageout']
        try:
            Mkdir(task['stageout'], yabiusername=self.yabiusername)
        except GETFailure, error:
            pass
        
        try:
            RCopy(outputuri,task['stageout'], yabiusername=self.yabiusername)
            self.log("Files successfuly staged out")
        except GETFailure, error:
            if "503" in error.message[1]:
                    raise                               # reraise a blocking error so our top level catcher will catch it and block the task
            # error executing
            print "TASK[%s]: Stageout failed!"%(self.taskid)
            self.status("error")
            if DEBUG:
                self.log("Staging out remote %s to %s failed... \n%s"%(outputuri,task['stageout'],traceback.format_exc()))
            else:
                self.log("Staging out remote %s to %s failed... %s"%(outputuri,task['stageout'],error))
            
            # finish task
            raise TaskFailed("Stageout failed")
            
    def cleanup(self):
        task=self.json
        # cleanup working dir
        for copy in self.json['stagein']:
            dst_url = copy['dst']
            self.log("Deleting %s..."%(dst_url))
            try:
                if DEBUG:
                    print "RM1:",dst_url
                Rm(dst_url, yabiusername=self.yabiusername, recurse=True)
            except GETFailure, error:
                if "503" in error.message[1]:
                    raise                               # reraise a blocking error so our top level catcher will catch it and block the task
                # error deleting. This is logged but is non fatal
                print "TASK[%s]: Delete %s Error!"%(self.taskid, dst_url)
                #status("error")
                self.log("Deleting %s failed: %s"%(dst_url, error))
                
                # finish task
                raise TaskFailed("Cleanup failed")
            
        dst_url = task['exec']['fsbackend']
        self.log("Deleting containing folder %s..."%(dst_url))
        try:
            if DEBUG:
                print "RM2:",dst_url
            Rm(dst_url, yabiusername=self.yabiusername, recurse=True)
        except GETFailure, error:
            if "503" in error.message[1]:
                    raise                               # reraise a blocking error so our top level catcher will catch it and block the task
            # error deleting. This is logged but is non fatal
            print "TASK[%s]: Delete %s Error!"%(self.taskid, dst_url)
            #status("error")
            self.log("Deleting %s failed: %s"%(dst_url, error))
            
            # finish task
            raise TaskFailed("Cleanup failed")
                