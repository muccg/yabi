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
"""This is like pexpect, but will work on any file descriptor that you pass it.
So you are reponsible for opening and close the file descriptor.

$Id: fdpexpect.py 505 2007-12-26 21:33:50Z noah $
"""

from pexpect import *
import os

__all__ = ['fdspawn']

class fdspawn (spawn):

    """This is like pexpect.spawn but allows you to supply your own open file
    descriptor. For example, you could use it to read through a file looking
    for patterns, or to control a modem or serial device. """

    def __init__ (self, fd, args=[], timeout=30, maxread=2000, searchwindowsize=None, logfile=None):

        """This takes a file descriptor (an int) or an object that support the
        fileno() method (returning an int). All Python file-like objects
        support fileno(). """

        ### TODO: Add better handling of trying to use fdspawn in place of spawn
        ### TODO: (overload to allow fdspawn to also handle commands as spawn does.

        if type(fd) != type(0) and hasattr(fd, 'fileno'):
            fd = fd.fileno()

        if type(fd) != type(0):
            raise ExceptionPexpect ('The fd argument is not an int. If this is a command string then maybe you want to use pexpect.spawn.')

        try: # make sure fd is a valid file descriptor
            os.fstat(fd)
        except OSError:
            raise ExceptionPexpect, 'The fd argument is not a valid file descriptor.'

        self.args = None
        self.command = None
        spawn.__init__(self, None, args, timeout, maxread, searchwindowsize, logfile)
        self.child_fd = fd
        self.own_fd = False
        self.closed = False
        self.name = '<file descriptor %d>' % fd

    def __del__ (self):

        return

    def close (self):

        if self.child_fd == -1:
            return
        if self.own_fd:
            self.close (self)
        else:
            self.flush()
            os.close(self.child_fd)
            self.child_fd = -1
            self.closed = True

    def isalive (self):

        """This checks if the file descriptor is still valid. If os.fstat()
        does not raise an exception then we assume it is alive. """

        if self.child_fd == -1:
            return False
        try:
            os.fstat(self.child_fd)
            return True
        except:
            return False

    def terminate (self, force=False):

        raise ExceptionPexpect ('This method is not valid for file descriptors.')

    def kill (self, sig):

        return

