# Use epoll() as our base reactor
from twisted.internet.epollreactor import EPollReactor as StacklessBaseReactor

import stackless

# seconds between running the greenthreads. 0.0 for flat out 100% CPU
STACKLESS_MAX_PUMP_RATE = 0.1

class StacklessReactor(StacklessBaseReactor):
    """This reactor does the stackless green thread pumping in the main thread, interwoven with the reactor pump"""
    
    def doIteration(self, timeout):
        """Calls the base reactors doIteration, and then fires off all the stackless threads"""
        if timeout > STACKLESS_MAX_PUMP_RATE:
            timeout = STACKLESS_MAX_PUMP_RATE
        #print ".",timeout
        stackless.schedule()
        return StacklessBaseReactor.doIteration(self,timeout)

def install():
    """
    Install the epoll() reactor.
    """
    p = StacklessReactor()
    from twisted.internet.main import installReactor
    installReactor(p)
