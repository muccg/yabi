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
from ExecConnector import ExecConnector, ExecutionError

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "ssh"

DEBUG = False

from twisted.web2 import http, responsecode, http_headers, stream

import shlex
from utils.protocol import globus
import stackless
import tempfile

from utils.stacklesstools import sleep
from utils.protocol import ssh

from conf import config

sshauth = ssh.SSHAuth.SSHAuth()

class SSHConnector(ExecConnector, ssh.KeyStore.KeyStore):
    def __init__(self):
        ExecConnector.__init__(self)
        
        configdir = config.config['backend']['certificates']
        ssh.KeyStore.KeyStore.__init__(self, dir=configdir)
    
    def run(self, yabiusername, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", maxWallTime=60, maxMemory=1024, cpus=1, queue="testing", jobType="single", module=None, **creds):
        # preprocess some stuff
        modules = [] if not module else [X.strip() for X in module.split(",")]
        
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        stackless.schedule()
        
        try:
            if DEBUG:
                print "SSH",command,"WORKING:",working    
            client_stream.write("Unsubmitted\n")
            stackless.schedule()
            
            client_stream.write("Pending\n")
            stackless.schedule()
            
            if not creds:
                creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, "/")
        
            usercert = self.save_identity(creds['key'])
            
            if DEBUG:
                print "usercert:",usercert
                print "command:",command
                print "username:",username
                print "host:",host
                print "working:",working
                print "port:","22"
                print "stdout:",stdout
                print "stderr:",stderr
                print "modules",modules
                print "password:",creds['password']
            pp = ssh.Run.run(usercert,command,username,host,working,port="22",stdout=stdout,stderr=stderr,password=creds['password'], modules=modules)
            client_stream.write("Running\n")
            stackless.schedule()
            
            while not pp.isDone():
                stackless.schedule()
                
            if pp.exitcode==0:
                # success
                client_stream.write("Done\n")
                client_stream.finish()
                return
                
            # error
            if DEBUG:
                print "SSH Job error:"
                print "OUT:",pp.out
                print "ERR:",pp.err
            client_stream.write("Error\n")
            client_stream.finish()
            return
                    
        except Exception, ee:
            import traceback
            traceback.print_exc()
            client_stream.write("Error\n")
            client_stream.finish()
            return
        