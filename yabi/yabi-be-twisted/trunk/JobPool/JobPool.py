from weakref import WeakValueDictionary
import stackless

class JobPool(object):
    """This is the pool of presently running stackless green threads. They are referenced by an ID number. When a run() task is finished,
    it disappears from this pool"""
    
    #def __init__(self):
        #self.pool = WeakValueDictionary()
        
    #def add(self, id, job):
        #self.pool[id] = job
        
    #def schedule(self):
        #"""Pump all the running jobs"""
        #stackless.schedule()
    
    def run(self):
        stackless.run()