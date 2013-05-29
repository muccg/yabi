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
import os
import shlex
from twisted.internet import protocol
from twisted.internet import reactor

DEBUG = False


class BaseShellProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, stdin=None):
        self.stdin = stdin
        self.err = ""
        self.out = ""
        self.exitcode = None

    def connectionMade(self):
        # when the process finally spawns, close stdin, to indicate we have nothing to say to it
        if self.stdin:
            self.transport.write(self.stdin)
        self.transport.closeStdin()

    def outReceived(self, data):
        self.out += data
        if DEBUG:
            print "OUT:", data

    def errReceived(self, data):
        self.err += data
        if DEBUG:
            print "ERR:", data

    def outConnectionLost(self):
        # stdout was closed. this will be our endpoint reference
        if DEBUG:
            print "Out lost"
        self.unifyLineEndings()

    def inConenctionLost(self):
        if DEBUG:
            print "In lost"
        self.unifyLineEndings()

    def errConnectionLost(self):
        if DEBUG:
            print "Err lost"
        self.unifyLineEndings()

    def processEnded(self, status_object):
        self.exitcode = status_object.value.exitCode
        if DEBUG:
            print "proc ended", self.exitcode
        self.unifyLineEndings()

    def unifyLineEndings(self):
        # try to unify the line endings to \n
        self.out = self.out.replace("\r\n", "\n")
        self.err = self.err.replace("\r\n", "\n")

    def isDone(self):
        return self.exitcode is not None

    def isFailed(self):
        return self.isDone() and self.exitcode != 0


class BaseShell(object):

    wordchars = None

    def __init__(self):
        pass

    def _make_env(self, environ=None):
        """Return a custom environment for the specified cert file"""
        subenv = environ.copy() if environ is not None else os.environ.copy()
        return subenv

    def execute(self, pp, command, env=None, working="/usr/bin"):
        """execute a command using a process protocol"""
     
        arguments = command 
        if self.wordchars is not None: 
            lexer = shlex.shlex(command, posix=True)
            #lexer.wordchars += r"-.:;/="
            lexer.wordchars += self.wordchars
            arguments = list(lexer)

        subenv = env
        if subenv is None:
            subenv = self._make_env()

        if DEBUG:
            print "env", subenv
            print "exec:", command
            print [pp,
                   arguments[0],
                   arguments,
                   subenv,
                   working]

        reactor.spawnProcess(pp,
                             arguments[0],
                             arguments,
                             env=subenv,
                             path=working)
        return pp