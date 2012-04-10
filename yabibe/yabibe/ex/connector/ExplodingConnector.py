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

from ExecConnector import ExecConnector, ExecutionError

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "explode"

DEBUG = False

from twistedweb2 import http, responsecode, http_headers, stream

import shlex
import os
from utils.protocol import globus
import gevent
import tempfile

from utils.geventtools import sleep

from conf import config
from SubmissionTemplate import make_script

from twisted.internet import protocol
from twisted.internet import reactor

import random

possible_delay_sets = [
         # normal   
         [   
            (10.0, "Unsubmitted"),
            (10.0, "Pending"),
            (10.0, "Running"),
            (30.0, "Error")
         ],
         
         # no pending
         [   
            (10.0, "Unsubmitted"),
            (10.0, "Running"),
            (30.0, "Error")
         ],
         
         # no running
         [   
            (10.0, "Unsubmitted"),
            (10.0, "Pending"),
            (30.0, "Error")
         ],
         
         # straight to error
         [   
            (10.0, "Unsubmitted"),
            (30.0, "Error")
         ],
         
         # nothing but error
         [   
            (10.0, "Error")
         ],
         
         # speed run
         [   
            (0.1, "Unsubmitted"),
            (0.1, "Pending"),
            (0.1, "Running"),
            (0.1, "Error")
         ],
         
         # speed bomb
         [
            (0, "Unsubmitted"),
            (0, "Pending"),
            (0, "Running"),
            (0, "Error")
         ]
    ]
             
         
class ExplodingConnector(ExecConnector):    
    def run(self, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, submission, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None):
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        gevent.sleep()
        
        #times = random.choice(possible_delay_sets)
        times = possible_delay_sets[-1]

        print "Exploding Connector: command %s, remoteurl %s, delay_set %s" % (command, remoteurl, str(times))
        
        for delay, message in times:
            sleep(delay)
            print "Exploding Connector: remoteurl %s, message %s" % (remoteurl, message)
            client_stream.write("%s\r\n"%message)
        
        client_stream.finish()
        return
        
