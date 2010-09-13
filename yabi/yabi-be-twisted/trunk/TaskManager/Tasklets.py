# -*- coding: utf-8 -*-

import pickle
import os
import dircache
import stackless

from TaskTools import CloseConnections
from Task import NullBackendTask, MainTask

class FileVersionMismatch(Exception): pass

class Tasklets(object):
    """This is a store for all the tasklets running in back end system. 
    From here they can be saved to disk and reloaded when the server is restarted
    """
    
    def __init__(self):
        self.tasks = []
        
    def add(self, task):
        self.tasks.append(task)
        
    def purge(self):
        """purge dead tasks from the list"""
        for task in self.tasks:
            if task.finished():
                self.tasks.remove(task)
        
    def save(self, directory):
        print "TASKS Save",self.tasks
        
        for task in self.tasks:
            # before we pickle it, if we are waiting on a connection in our stack frame, then set it to have failed
            # so that when we are resurrected in the future, the connection will immediately be marked as failed
            fname = os.path.join(directory,str(id(task)))
            
            self.save_task(task,fname)
            
    def save_task(self,task,filename):
        """Save the json and stage to a file"""
        with open(filename,"w") as fh:
            fh.write(pickle.dumps(("V1",task.__class__.__name__,task.stage,task.json)))
  
    def load_task(self,filename):
        """Load the json from a file, create the right task object and return it"""
        with open(filename,'r') as fh:
            version, objname, stage, json = pickle.loads(fh.read())
        
        if version!="V1":
            raise FileVersionMismatch, "File Version Mismatch for %s"%(filename)
        
        # instantiate the object
        task = locals()[objname]()
        task.load_json(json, stage=stage)
        return task
            
    def load(self,directory):
        self.tasks=[]
            
        for f in dircache.listdir(directory):
            
            task = self.load_task(f)
            #print "LOAD",f,task
            os.unlink(os.path.join(directory,f))
            
            # lets try and start the task up
            runner = stackless.tasklet(task.run)
            runner.setup()
            runner.run()
            
            self.tasks.append(task)
            
            print "task",task,"loaded"
           
    def debug(self):
        
        def dump_obj(obj):
            out = ""
            keys = dir(obj)
            #for key in [K for K in keys if not K.startswith("_")]:
            keys.remove("cstate")
            for key in keys:
                out+=key+": "+str(getattr(obj,key))+"\n"
            return out    
        
        output=""
        for task in self.tasks:
            section=str(task)+"\n"+("="*len(str(task)))+"\n"
            section+=dump_obj(task)
            section+="\n"
            
            output = "%s%s\n"%(output,section)
        return output
        
    def pickle(self):
        """ just try and serialise the objects"""
        self.save("/tmp")
    
tasklets = Tasklets()