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

"""
Queue with priority for managing connections to protocols, hosts and ports
"""
import gevent
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
        
        ##
        ## TEMPORARILY DISABLED
        ##
        return inspect.currentframe().f_back
        
        level = level if level is not None else self.default_level
        
        if not level:
            return
        
        # get caller frame as our tag. TODO: weakref this
        caller = inspect.currentframe().f_back
        assert caller not in self.priomap.keys()
        
        #print "lock tag",tag,"appending to queue of length",len(self.queue)
        
        self._add_tag(prio,caller)
        
        if not self._is_in_head(caller,level):
            print "Locking",caller
        
            while not self._is_in_head(caller,level):
                gevent.sleep()
                
            print "Releasing",caller
                
        return caller
    
    def unlock(self, tag):
        """unlock the queue"""
        #print "removing",tag
        try:
            self._del_tag(tag)
        except KeyError, ke:
            pass                        # trying to unlock a tag that doesnt exist?
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
        