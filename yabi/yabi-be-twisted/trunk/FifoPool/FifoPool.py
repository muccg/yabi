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
import os
import tempfile
import weakref

from conf import config

FIFO_MOD = 0666

class FifoPool(object):
    """FifoPool is a pool of fifo objects. This allows us to quickly ascertain how many transfers are going on.
    This is where fifo's are created and allocated, and also where they are cleaned up."""
    
    def __init__(self, storage=None):
        if storage:
            assert os.path.exists(storage) and os.path.isdir(storage), "Storage directory %s does not exist"%storage
            self.storage = storage
        else:
            self._make_fifo_storage()
        
        self._fifos={}
        
    def _make_fifo_storage(self):
        """makes a directory for storing the fifos in"""
        directory = config.config['backend']['fifos']
        if not directory:
            self.storage = tempfile.mkdtemp(prefix="yabi-fifo-")
        else:
            self.storage = directory
        #print "=================> FifoPool created in",self.storage
    
    def _make_fifo(self, prefix="fifo_",suffix=""):
        """make a fifo on the filesystem and return its path"""
        filename = tempfile.mktemp(suffix=suffix, prefix=prefix, dir=self.storage)                # insecure, but we dont care
        os.umask(0)
        os.mkfifo(filename, FIFO_MOD)
        return filename
    
    def Get(self):
        """return a new fifo path"""
        fifo = self._make_fifo()
        self._fifos[fifo]=[]
        return fifo
        
    def WeakLink(self, fifo, *procs):
        """Link the running proccesses to our fifo. Weak refs are used. When all the weakrefs for a fifo expire, the fifo is deleted. AUTOMAGICAL power of weakrefs"""
        
        # a closure to remove the fifo if the list is empty
        def remove_ref( weak ):
            self._fifos[fifo].remove(weak)
            if not self._fifos[fifo]:
                # empty. delete us
                os.unlink(fifo)
                del self._fifos[fifo]
        
        for proc in procs:
            ref = weakref.ref( proc, remove_ref )
            self._fifos[fifo].append(ref)
            
    def MakeURLForFifo(self,filename):
        return "file://"+os.path.normpath(filename)