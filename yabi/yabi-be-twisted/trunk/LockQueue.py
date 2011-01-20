# -*- coding: utf-8 -*-

"""
Queue with priority for managing connections to protocols, hosts and ports
"""
import stackless
import inspect

class TagNotInLockQueue(Exception): pass

class LockQueue(object):
    def __init__(self, default_level=10):
        self.queue = {}                             # queue of the format { prio:queue, prio:queue, prio:queue } queue is a FIFO list of lock tags
        self.priomap = {}                           # maps the tags back to their prio
        self.default_level = default_level
        
    def lock(self,prio=100,level=None):
        """
        Priority is the priority level of the lock. Lower priorities are unlocked before higher priorities
        
        level is how high on the queue our lock we need to get before the lock being released
        """
        level = level if level is not None else self.default_level
        
        # get caller frame as our tag. TODO: weakref this
        caller = inspect.currentframe().f_back
        assert caller not in self.priomap.keys()
        
        #print "lock tag",tag,"appending to queue of length",len(self.queue)
        
        self._add_tag(prio,caller)
        
        if not self._is_in_head(caller,level):
            print "Locking",caller
        
            while not self._is_in_head(caller,level):
                stackless.schedule()
                
            print "Releasing",caller
                
        
                
        return caller
    
    def unlock(self, tag):
        """unlock the queue"""
        #print "removing",tag
        self._del_tag(tag)
        #print "length now",len(self.queue)
    
    def _add_tag(self, prio, tag):
        # add to prio queue
        if prio not in self.queue:
            self.queue[prio]=[]
        self.queue[prio].append( tag )
        
        # map back to prio
        self.priomap[tag]=prio
        
    def _del_tag(self, tag):
        # delete priomap pointer
        prio = self.priomap[tag]
        del self.priomap[tag]
        
        # delete tag
        self.queue[prio].remove(tag)
        if not len(self.queue[prio]):
            self.queue[prio]
    
    def _full_queue(self):
        for prio in sorted(self.queue.keys()):
            for item in self.queue[prio]:
                yield item
                
    def _is_in_head(self, tag, level=None):
        """return true is tag is inside 'level' head items.
        eg. if level is 10, returns true for a passed in tag if it is in the top 10 of a united queue
        returns false if its further down (and thus needs locking)
        """
        level = level if level is not None else self.default_level
        
        for num, item in enumerate(self._full_queue()):
            #print "looking for",tag,"in",num,item,"to see if its greater than",level
            if num>=level:
                return False
            if item==tag:
                return True
        
        raise TagNotInLockQueue, "Tag not found in queue"
        