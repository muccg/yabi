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
SCHEMA = "torque"

DEBUG = False

TMP_DIR = "/tmp"

from twisted.web2 import http, responsecode, http_headers, stream

from utils.stacklesstools import sleep, POST
from utils.torquetools import qsub, qstat

import json, uuid, os

from SubmissionTemplate import make_script
from TaskManager.TaskTools import RemoteInfo

# for Job status updates, poll this often
def JobPollGeneratorDefault():
    """Generator for these MUST be infinite. Cause you don't know how long the job will take. Default is to hit it pretty hard."""
    delay = 1.0
    while delay<10.0:
        yield delay
        delay *= 1.05           # increase by 5%
    
    while True:
        yield 10.0

class TorqueConnector(ExecConnector):
    def __init__(self):
        print "TorqueConnector::__init__() debug setting is",DEBUG
        ExecConnector.__init__(self)
    
    def run(self, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, submission, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None):
        print "RUNNNNNN"
        modules = [] if not module else [X.strip() for X in module.split(",")]
        
        submission_script = os.path.join(TMP_DIR,str(uuid.uuid4())+".sh")
        if DEBUG:
            print "submission script path is %s"%(submission_script)
            print "input script is",repr(submission)
        
        script_string = make_script(submission,working,command,modules,cpus,memory,walltime,yabiusername,username,host,queue,stdout,stderr)    
        
        if DEBUG:
            print "torque"
            print "command:",command
            print "username:",username
            print "host:",host
            print "working:",working
            print "port:","22"
            print "stdout:",stdout
            print "stderr:",stderr
            print "modules",modules
            print "script:",repr(script_string)
        
        with open(submission_script,'w') as fh:
            fh.write(script_string)
        
        try:
            if DEBUG:
                print "QSUB",command,"WORKING:",working
            jobid = qsub("jobname", submission_script=submission_script, user=username, workingdir=working)
            if DEBUG:
                print "JOB ID",jobid
        
        except ExecutionError, ee:
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = str(ee) ))
            return
        
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        
        # now the job is submitted, lets remember it
        self.add_running(jobid, {'username':username})
        
        # lets report our id to the caller
        client_stream.write("id=%s\n"%jobid)
        
        self.main_loop(client_stream, username, jobid, remoteurl)
            
        # delete finished job
        self.del_running(jobid)
            
        client_stream.finish()

    def resume(self, jobid, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None):
    #def resume(self,yabiusername, eprfile, scheme, username, host, **creds):
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        
        try:
            username = self.get_running(jobid)['username']
        except KeyError, ke:
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = "No such jobid resumable: %s"%jobid ))
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))

        self.main_loop( client_stream, username, jobid )
        
        # delete finished job
        self.del_running(jobid)
            
        client_stream.finish()

    def main_loop(self, client_stream, username, jobid, remoteurl=None ):
        newstate = state = None
        delay = JobPollGeneratorDefault()
        while state!="Done":
            # pause
            sleep(delay.next())
            
            jobsummary = qstat(jobid, username)
            self.update_running(jobid,jobsummary)
            
            if jobid in jobsummary:
                # job has not finished
                status = jobsummary[jobid]['job_state']
                
                if status == 'C':
                    #print "STATUS IS C <=============================================================",jobsummary[jobid]['exit_status']
                    # state 'C' means complete OR error
                    if 'exit_status' in jobsummary[jobid] and jobsummary[jobid]['exit_status'] == '0':
                        newstate = "Done"
                    else:
                        newstate = "Error"
                else:
                    newstate = dict(Q="Unsubmitted", E="Running", H="Pending", R="Running", T="Pending", W="Pending", S="Pending")[status]
                
                
            else:
                # job has finished
                sleep(15.0)                      # deal with SGE flush bizarreness (files dont flush from remote host immediately. Totally retarded)
                print "ERROR: jobid %s not in jobsummary"%jobid
                print "jobsummary is",jobsummary
                
                # if there is standard error from the qstat command, report that!
                
                
                newstate = "Error"
            if DEBUG:
                print "Job summary:",jobsummary
                
            
            if state!=newstate:
                state=newstate
                #print "Writing state",state
                client_stream.write("%s\n"%state)
                
                # report the full status to the remote_url
                if remoteurl:
                    if jobid in jobsummary:
                        RemoteInfo(remoteurl,json.dumps(jobsummary[jobid]))
                    else:
                        print "Cannot call RemoteInfo call for job",jobid
                
            if state=="Error":
                #print "CLOSING STREAM"
                client_stream.finish()
                return
        
    def info(self, jobid, username):
        jobsummary = qstat(user=username)
        print jobsummary
        
