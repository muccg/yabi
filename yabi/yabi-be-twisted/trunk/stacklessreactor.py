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
# Use epoll() as our base reactor
from twisted.internet.epollreactor import EPollReactor as StacklessBaseReactor

import stackless

# seconds between running the greenthreads. 0.0 for flat out 100% CPU
STACKLESS_MAX_PUMP_RATE = 0.01

class StacklessReactor(StacklessBaseReactor):
    """This reactor does the stackless green thread pumping in the main thread, interwoven with the reactor pump"""
    
    def doIteration(self, timeout):
        """Calls the base reactors doIteration, and then fires off all the stackless threads"""
        if timeout > STACKLESS_MAX_PUMP_RATE:
            timeout = STACKLESS_MAX_PUMP_RATE
        try:    
            stackless.schedule()
        except Exception, e:
            print "Uncaught Exception in stackless threads"
            import traceback
            traceback.print_exc()
        return StacklessBaseReactor.doIteration(self,timeout)

def install():
    """
    Install the epoll() reactor.
    """
    p = StacklessReactor()
    from twisted.internet.main import installReactor
    installReactor(p)
