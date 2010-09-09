# -*- coding: utf-8 -*-

DEBUG = False

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
        
    def norun(self):
        self.log("null backend... skipping task and copying files")
        self.log("making stageout directory %s"%self.json['stageout'])
        
        self.make_stageout()
        
        self.status("stagein")
        self.stage_in_files()

        self.status("complete")              # null backends are always marked complete
        
    def run(self):
        self.status("stagein")
        self.stage_in_files()
                
        # make our working directory
        status("mkdir")
        self.mkdir()
        
        # now we are going to run the job
        status("exec")
        self.execute()
        
        # stageout
        log("Staging out results")
        status('stageout')
        
        # recursively copy the working directory to our stageout area
        log("Staging out remote %s to %s..."%(outputdir,task['stageout']))
        
        # make sure we have the stageout directory
        log("making stageout directory %s"%task['stageout'])
        
        self.stageout()
        
        # cleanup
        status("cleaning")
        log("Cleaning up job...")
        
        self.cleanup()
        
        log("Job completed successfully")
        status("complete")
        
    def stage_in_files(self)
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
                return              # finish task
           
            print "TASK[%s]: Copy %s to %s Success!"%(taskid,src,dst)
        
     def mkdir(self):
        # get our credential working directory. We lookup the execution backends auth proxy cache, and get the users home directory from that
        # this comes from their credentials.
        
        scheme, address = parse_url(task['exec']['backend'])
        usercreds = UserCreds(yabiusername, task['exec']['backend'])
        #homedir = usercreds['homedir']
        workingdir = task['exec']['workingdir']
        
        assert address.path=="/", "Error. JSON[exec][backend] has a path. Execution backend URI's must not have a path (path is %s)"%address.path 
        
        if DEBUG:
            print "USERCREDS",usercreds
        
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
        
     def execute(self):
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
        
     def stageout(self):

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
            
     def cleanup(self):
        
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
        
                