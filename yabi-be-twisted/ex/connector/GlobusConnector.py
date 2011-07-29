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
from ExecConnector import ExecConnector

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['GLOBUS_LOCATION','LD_LIBRARY_PATH','LIBPATH','GLOBUS_PATH','DYLD_LIBRARY_PATH','SHLIB_PATH','PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = ['GLOBUS_LOCATION']

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "globus"

import shlex
from utils.protocol import globus
import stackless
import tempfile
import os

from utils.stacklesstools import sleep, POST

import json

from twisted.web2 import stream, http, responsecode, http_headers

# import conf so we can get the location our tempfiles should be stored in
from conf import config

from TaskManager.TaskTools import RemoteInfo, Sleep

from Exceptions import NoCredentials, AuthException

# for Job status updates, poll this often
def JobPollGeneratorDefault():
    """Generator for these MUST be infinite. Cause you don't know how long the job will take. Default is to hit it pretty hard."""
    delay = 1.0
    while delay<10.0:
        yield delay
        delay *= 1.05           # increase by 5%
    
    while True:
        yield 10.0

class GlobusConnector(ExecConnector, globus.Auth.GlobusAuth):
    task_info = {}                                                  # here is where we store information about the executing task for inquiries from yabiengine. Keys are taskids
    
    def __init__(self):
        ExecConnector.__init__(self)
        globus.Auth.GlobusAuth.__init__(self)
        self.CreateAuthProxy()

    def run(self, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None):
        # use shlex to parse the command into executable and arguments
        lexer = shlex.shlex(command, posix=True)
        lexer.wordchars += r"-.:;/="
        arguments = list(lexer)
        
        rsl = globus.ConstructRSL(
            command = arguments[0],
            args = arguments[1:],
            directory = working,
            stdout = stdout,
            stderr = stderr,
            address = host,
            maxWallTime = walltime,
            maxMemory = memory,
            cpus = cpus,
            queue = queue,
            jobType = jobtype,
            modules = [] if not module else [X.strip() for X in module.split(",")]
        )
        
        # store the rsl in a file
        rslfile = globus.writersltofile(rsl)
        
        # first we need to auth the proxy
        try:
            if creds:
                self.EnsureAuthedWithCredentials(host, creds)
            else:
                # TODO: how to fix the globus credential gather if we dont have a path here?
                self.EnsureAuthed(yabiusername,scheme,username,host,"/")
        except globus.Auth.AuthException, ae:
            # connection problems.
            channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, stream = "Could not get auth credentials for %s://%s@%s. %s\n"%(scheme,username,host,str(ae)) ))
            return
        
        # now submit the job via globus
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        # TODO: what if our proxy has expired in the meantime? (rare, but possible)
        processprotocol = globus.Run.run( usercert, rslfile, host)
        
        while not processprotocol.isDone():
            stackless.schedule()
            
        if processprotocol.exitcode!=0:
            channel.callback(http.Response( responsecode.SERVICE_UNAVAILABLE, {'content-type': http_headers.MimeType('text', 'plain')}, stream = processprotocol.err ))
            return
                
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        
        # now we want to continually check the status of the job
        job_id = processprotocol.job_id
        epr = processprotocol.epr
        
        # now the job is submitted, lets remember it
        self.add_running(job_id, {'host':host,'username':username,'epr':epr})
        
        # lets report our id to the caller
        client_stream.write("id=%s\n"%job_id)
        
        # save the epr to a tempfile so we can use it again and again
        temp = tempfile.NamedTemporaryFile(suffix=".epr",dir=config.config['backend']['temp'],delete=False)
        temp.write(epr)
        temp.close()
            
        eprfile = temp.name
            
        state = None
        delay = JobPollGeneratorDefault()
        warningcount=0
        while state!="Done":
            # pause
            sleep(delay.next())
            
            if creds:
                self.EnsureAuthedWithCredentials(host, creds)
            else:
                try:
                    self.EnsureAuthed(yabiusername, scheme,username,host,"/")
                except AuthException, ae:
                    # auth exception while looking for status. We should wait and try again.
                    # TODO: turn this into resume???? or not?
                    Sleep(30.0)
            processprotocol = globus.Run.status( usercert, eprfile, host )
            
            while not processprotocol.isDone():
                stackless.schedule()
                
            #print "STATE:",processprotocol.jobstate, processprotocol.exitcode
                
            if processprotocol.exitcode and processprotocol.jobstate!="Done":
                if warningcount<5 and "no valid proxy credential was found" in processprotocol.err:
                    warningcount+=1
                    print "Warning: Failure #",warningcount,"running globus status command for",job_id,":",processprotocol.err
                else:
                    # error occured running statecheck... sometimes globus just fails cause its a fucktard.
                    print "Job status check for %s Failed (%d) - %s / %s\n"%(job_id,processprotocol.exitcode,processprotocol.out,processprotocol.err)
                    client_stream.write("Error - %s\n"%(processprotocol.err))
                    client_stream.finish()
                    self.del_running(job_id)
                    os.unlink(eprfile)
                    return
            
            newstate = processprotocol.jobstate
            if state!=newstate:
                state=newstate
                client_stream.write("%s\n"%state)
                
                if remoteurl and job_id in self.get_all_running():
                    RemoteInfo(remoteurl,json.dumps(self.get_running(job_id)))
            
        client_stream.finish()
        
        # job is finished, lets forget about it
        self.del_running(job_id)
        os.unlink(eprfile)
               
    def resume(self, jobid, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None):
        # first we need to auth the proxy
        try:
            if creds:
                self.EnsureAuthedWithCredentials(host, creds)
            else:
                # TODO: how to fix the globus credential gather if we dont have a path here?
                try:
                    self.EnsureAuthed(yabiusername, scheme,username,host,"/")
                except AuthException, ae:
                    # auth exception while looking for status. We should wait and try again.
                    # TODO: turn this into resume???? or not?
                    Sleep(30.0)
        except globus.Auth.AuthException, ae:
            # connection problems.
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = "Could not get auth credentials for %s://%s@%s. %s\n"%(scheme,username,host,str(ae)) ))
            return
        
        # now submit the job via globus
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))

        # TODO: cleanup so unused variables aren't passed in
        info = self.get_running(jobid)
        (host,username,epr) = [info[X] for X in ('host','username','epr')]

        # save the epr to a tempfile so we can use it again and again
        temp = tempfile.NamedTemporaryFile(suffix=".epr",dir=config.config['backend']['temp'],delete=False)
        temp.write(epr)
        temp.close()

        eprfile = temp.name

        state = None
        delay = JobPollGeneratorDefault()
        while state!="Done":
            # pause
            sleep(delay.next())
            
            if creds:
                self.EnsureAuthedWithCredentials(host, creds)
            else:
                self.EnsureAuthed(yabiusername, scheme,username,host,"/")
            processprotocol = globus.Run.status( usercert, eprfile, host )
            
            while not processprotocol.isDone():
                stackless.schedule()
                
            #print "STATE:",processprotocol.jobstate, processprotocol.exitcode
                
            if processprotocol.exitcode and processprotocol.jobstate!="Done":
                # error occured running statecheck... sometimes globus just fails cause its a fucktard.
                print "Job status check for %s Failed (%d) - %s / %s\n"%(jobid,processprotocol.exitcode,processprotocol.out,processprotocol.err)
                client_stream.write("Failed - %s\n"%(processprotocol.err))
                client_stream.finish()
                
                # job is finished, lets forget about it
                self.del_running(jobid)
                os.unlink(eprfile)
                return
            
            newstate = processprotocol.jobstate
            if state!=newstate:
                state=newstate
                client_stream.write("%s\n"%state)
            
        client_stream.finish()

        # job is finished, lets forget about it
        self.del_running(jobid)
        os.unlink(eprfile)