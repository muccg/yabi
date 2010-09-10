# -*- coding: utf-8 -*-
import json
import stackless
import random
import os
import pickle

from utils.parsers import parse_url

from TaskTools import Copy, RCopy, Sleep, Log, Status, Exec, Mkdir, Rm, List, UserCreds, GETFailure, CloseConnections

import traceback

DEBUG = False

class TaskFailed(Exception):
    pass

class Task(object):
    def __init__(self, task):
        # stage in file
        self.json = task
        
        # check json is okish
        self._sanity_check()
                
        self.taskid = task['taskid']
        self.statusurl = task['statusurl']
        self.errorurl = task['errorurl']
        self.yabiusername = task['yabiusername']
                
        # shortcuts for our status and log calls
        self.status = lambda x: Status(self.statusurl,x)
        self.log = lambda x: Log(self.errorurl,x)
        
    def _sanity_check(self):
        # sanity check...
        for key in ['errorurl','exec','stagein','stageout','statusurl','taskid','yabiusername']:
            assert key in self.json, "Task JSON description is missing a vital key '%s'"%key
        
        # check the exec section
        for key in ['backend', 'command', 'fsbackend', 'workingdir']:
            assert key in self.json['exec'], "Task JSON description is missing a vital key inside the 'exec' section. Key name is '%s'"%key
        

class NullBackendTask(Task):
    def __init__(self, task):
        Task.__init__(self, task)
        
        # check if exec scheme is null backend. If this is the case, we need to run our special null backend tasklet
        scheme, address = parse_url(task['exec']['backend'])
        assert scheme.lower() == "null"
        
    def run(self):
        self.log("null backend... skipping task and copying files")
        self.log("making stageout directory %s"%self.json['stageout'])
        
        self.make_stageout()
        
        self.status("stagein")
        self.stage_in_files()

        self.status("complete")              # null backends are always marked complete

    def make_stageout(self):
        stageout = self.json['stageout']
        
        if DEBUG:
            print "STAGEOUT:",stageout
        try:
            Mkdir(stageout, yabiusername=self.yabiusername)
        except GETFailure, error:
            pass
        
    def stage_in_files(self):
        dst = stageout
        status = self.status
        log = self.log
        
        # for each stagein, copy to stageout NOT the stagein destination
        for copy in task['stagein']:
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
                print "Remote DIR does not exist"
                
                #make dir
                Mkdir(remotedir, yabiusername=self.yabiusername)
            
            if src.endswith("/"):
                log("RCopying %s to %s..."%(src,dst))
                try:
                    RCopy(src,dst, yabiusername=self.yabiusername)
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
                    Copy(src,dst, yabiusername=self.yabiusername)
                    log("Copying %s to %s Success"%(src,dst))
                except GETFailure, error:
                    # error copying!
                    print "TASK[%s]: Copy %s to %s Error!"%(taskid,src,dst)
                    status("error")
                    log("Copying %s to %s failed: %s"%(src,dst, error))
                    return              # finish task
            
                print "TASK[%s]: Copy %s to %s Success!"%(taskid,src,dst)
            
class MainTask(Task):
    def __init__(self, task):
        Task.__init__(self, task)
        
        # check if exec scheme is null backend. If this is the case, we need to run our special null backend tasklet
        scheme, address = parse_url(task['exec']['backend'])
        assert scheme.lower() != "null"   
                
    def run(self):
        self.status("stagein")
        self.stage_in_files()
                
        # make our working directory
        status("mkdir")
        outuri, outdir = self.mkdir()                     # make the directories we are working in
        
        # now we are going to run the job
        status("exec")
        self.execute(outdir)
        
        # stageout
        log("Staging out results")
        status('stageout')
        
        # recursively copy the working directory to our stageout area
        log("Staging out remote %s to %s..."%(outputdir,task['stageout']))
        
        # make sure we have the stageout directory
        log("making stageout directory %s"%task['stageout'])
        
        self.stageout(outuri)
        
        # cleanup
        status("cleaning")
        log("Cleaning up job...")
        
        self.cleanup()
        
        log("Job completed successfully")
        status("complete")
        
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
                print "Remote DIR does not exist"
                
                #make dir
                Mkdir(remotedir, yabiusername=self.yabiusername)
            
            log("Copying %s to %s..."%(src,dst))
            try:
                Copy(src,dst, yabiusername=self.yabiusername)
                log("Copying %s to %s Success"%(src,dst))
            except GETFailure, error:
                # error copying!
                print "TASK[%s]: Copy %s to %s Error!"%(taskid,src,dst)
                status("error")
                log("Copying %s to %s failed: %s"%(src,dst, error))
                
                raise TaskError("Stage In failed")
           
            print "TASK[%s]: Copy %s to %s Success!"%(taskid,src,dst)
        
     def mkdir(self):
        task=self.json
        
        # get our credential working directory. We lookup the execution backends auth proxy cache, and get the users home directory from that
        # this comes from their credentials.
        scheme, address = parse_url(task['exec']['backend'])
        usercreds = UserCreds(yabiusername, task['exec']['backend'])
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
            Mkdir(outputuri, yabiusername=yabiusername)
        except GETFailure, error:
            # error making directory
            print "TASK[%s]:Mkdir failed!"%(self.taskid)
            status("error")
            log("Making working directory of %s failed: %s"%(outputuri,error))
            
            raise TaskError("Mkdir failed")
        
        return outputuri,outputdir
        
     def execute(self, outputdir):
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
                    self.log("Remote execution backend changed status to: %s"%(line))
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
                    
                    Exec(uri, command=task['exec']['command'], stdout="STDOUT.txt",stderr="STDERR.txt", callbackfunc=_task_status_change, yabiusername=self.yabiusername, **extras)                # this blocks untill the command is complete.
                    self.log("Execution finished")
                except GETFailure, error:
                    # error executing
                    print "TASK[%s]: Execution failed!"%(self.taskid)
                    self.status("error")
                    self.log("Execution of %s on %s failed: %s"%(task['exec']['command'],task['exec']['backend'],error))
                    
                    # finish task
                    raise TaskError("Execution failed")
                
            except CloseConnections, cc:
                print "CLOSECONNECTIONS",cc
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
            # error executing
            print "TASK[%s]: Stageout failed!"%(taskid)
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
        for copy in task['stagein']:
            dst_url = task['exec']['fsbackend']
            log("Deleting %s..."%(dst_url))
            try:
                if DEBUG:
                    print "RM1:",dst_url
                Rm(dst_url, yabiusername=self.yabiusername, recurse=True)
            except GETFailure, error:
                # error deleting. This is logged but is non fatal
                print "TASK[%s]: Delete %s Error!"%(self.taskid, dst_url)
                #status("error")
                log("Deleting %s failed: %s"%(dst_url, error))
                
                # finish task
                raise TaskFailed("Cleanup failed")
        
                