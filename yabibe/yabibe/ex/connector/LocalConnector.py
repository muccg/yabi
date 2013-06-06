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

from ExecConnector import ExecConnector

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "localex"

DEBUG = False

from twistedweb2 import http, responsecode, http_headers, stream

import os
import gevent

from SubmissionTemplate import make_script

from twisted.internet import protocol
from twisted.internet import reactor
from conf import config
from utils.BaseShell import BaseShell, BaseShellProcessProtocol

TMP_DIR = config.config['backend']['temp']


class LocalRun(BaseShell):

    def __init__(self):
        self.wordchars = r"-.:;/="       

    def run(self,
            certfile,
            remote_command="hostname",
            username="yabi",
            host="localhost.localdomain",
            working=TMP_DIR,
            port="22",
            stdout="STDOUT.txt",
            stderr="STDERR.txt",
            password="",
            modules=[],
            streamin=None):
        """Spawn a process to run a local job. return the process handler"""

        if modules:
            remote_command = "&&".join(["module load %s" % module for module in modules] + [remote_command])

        if DEBUG:
            print "running local command:", remote_command

        return BaseShell.execute(self, BaseShellProcessProtocol(streamin), remote_command, working=working)


class LocalConnector(ExecConnector):
    def run(self,
            yabiusername,
            creds,
            command,
            working,
            scheme,
            username,
            host,
            remoteurl,
            channel,
            submission,
            stdout="STDOUT.txt",
            stderr="STDERR.txt",
            walltime=60,
            memory=1024,
            cpus=1,
            queue="testing",
            jobtype="single",
            module=None,
            tasknum=None,
            tasktotal=None):

        # preprocess some stuff
        modules = [] if not module else [X.strip() for X in module.split(",")]

        client_stream = stream.ProducerStream()
        channel.callback(http.Response(responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=client_stream))
        gevent.sleep()

        try:
            if DEBUG:
                print "LOCAL", command, "WORKING:", working, "CREDS passed in:%s" % (creds)
            client_stream.write("Unsubmitted\r\n")
            gevent.sleep(1.0)

            client_stream.write("Pending\r\n")
            gevent.sleep(1.0)

            script_string = make_script(submission, working, command, modules, cpus, memory, walltime, yabiusername, username, host, queue, stdout, stderr, tasknum, tasktotal)

            if DEBUG:
                print "command:", command
                print "username:", username
                print "host:", host
                print "working:", working
                print "port:", "22"
                print "stdout:", stdout
                print "stderr:", stderr
                print "modules:", modules
                print "submission script:", submission
                print "script string:", script_string

            pp = LocalRun().run(None, command, username, host, working, port="22", stdout=stdout, stderr=stderr, password=None, modules=modules)
            client_stream.write("Running\r\n")
            gevent.sleep(1.0)

            while not pp.isDone():
                gevent.sleep()

            # write out stdout and stderr.
            # TODO: make this streaming
            with open(os.path.join(working, stdout), 'w') as fh:
                fh.write(pp.out)
            with open(os.path.join(working, stderr), 'w') as fh:
                fh.write(pp.err)

            if pp.exitcode == 0:
                # success
                client_stream.write("Done\r\n")
                client_stream.finish()
                return

            # error
            if DEBUG:
                print "SSH Job error:"
                print "OUT:", pp.out
                print "ERR:", pp.err
            client_stream.write("Error\r\n")
            client_stream.finish()
            return

        except Exception:
            import traceback
            traceback.print_exc()
            client_stream.write("Error\r\n")
            client_stream.finish()
            return
