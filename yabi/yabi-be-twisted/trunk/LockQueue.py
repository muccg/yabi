# -*- coding: utf-8 -*-

"""
Queue with priority for managing connections to protocols, hosts and ports
"""
import stackless
import inspect


class LockQueue(object):
    def __init__(self, default_level=10):
        self.queue = []
        self.default_level = default_level
        
    def lock(self,priority=100,level=None):
        """
        Priority is the priority level of the lock. Lower priorities are unlocked before higher priorities
        
        level is how high on the queue our lock we need to get before the lock being released
        """
        level = level if level in not None else self.default_level
        
        # get caller frame as our tag
        caller = inspect.currentframe().f_back
        assert True not in [A[1] == caller for A in self.queue], "caller lock for frame already in queue"
        tag = (priority, caller)
        
        self.queue.append( tag )
        while sorted( self.queue ).index( tag )>=level:
            stackless.schedule()
            
        return tag
    
    def unlock(self, tag):
        """unlock the queue"""
        self.queue.remove(tag)
    
    
