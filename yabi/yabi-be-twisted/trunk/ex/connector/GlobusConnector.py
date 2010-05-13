# -*- coding: utf-8 -*-
from ExecConnector import ExecConnector

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['GLOBUS_LOCATION','LD_LIBRARY_PATH','LIBPATH','GLOBUS_PATH','DYLD_LIBRARY_PATH','SHLIB_PATH','PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = ['GLOBUS_LOCATION']

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "globus"

import shlex
import globus
import stackless
import tempfile

from utils.stacklesstools import sleep

from twisted.web2 import stream, http, responsecode, http_headers

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
    def __init__(self):
        ExecConnector.__init__(self)
        globus.Auth.GlobusAuth.__init__(self)
        self.CreateAuthProxy()
    
    def run(self, yabiusername, command, working, scheme, username, host, channel, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, max_memory=1024, cpus=1, queue="testing", job_type="single", module=None, **creds):
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
            maxMemory = max_memory,
            cpus = cpus,
            queue = queue,
            jobType = job_type,
            modules = [] if not module else [X.strip() for X in module.split(",")]
        )
        
        # store the rsl in a file
        rslfile = globus.writersltofile(rsl)
        
        # first we need to auth the proxy
        try:
            if creds:
                self.EnsureAuthedWithCredentials(host, **creds)
            else:
                # TODO: how to fix the globus credential gather if we dont have a path here?
                self.EnsureAuthed(yabiusername,scheme,username,host,"/")
        except globus.Auth.AuthException, ae:
            # connection problems.
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = "Could not get auth credentials for %s://%s@%s. %s\n"%(scheme,username,host,str(ae)) ))
            return
        
        # now submit the job via globus
        usercert = self.GetAuthProxy(host).ProxyFile(username)
        
        # TODO: what if our proxy has expired in the meantime? (rare, but possible)
        processprotocol = globus.Run.run( usercert, rslfile, host)
        
        while not processprotocol.isDone():
            stackless.schedule()
            
        if processprotocol.exitcode!=0:
            channel.callback(http.Response( responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream = processprotocol.err ))
            return
        
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response( responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream = client_stream ))
        
        # now we want to continually check the status of the job
        job_id = processprotocol.job_id
        epr = processprotocol.epr
        
        # save the epr to a tempfile so we can use it again and again
        temp = tempfile.NamedTemporaryFile(suffix=".epr",delete=False)
        temp.write(epr)
        temp.close()
            
        eprfile = temp.name
            
        state = None
        delay = JobPollGeneratorDefault()
        while state!="Done":
            # pause
            sleep(delay.next())
            
            if creds:
                self.EnsureAuthedWithCredentials(host, **creds)
            else:
                self.EnsureAuthed(yabiusername, scheme,username,host,"/")
            processprotocol = globus.Run.status( usercert, eprfile, host )
            
            while not processprotocol.isDone():
                stackless.schedule()
                
            #print "STATE:",processprotocol.jobstate, processprotocol.exitcode
                
            if processprotocol.exitcode and processprotocol.jobstate!="Done":
                # error occured running statecheck... sometimes globus just fails cause its a fucktard.
                print "Job status check for %s Failed (%d) - %s / %s\n"%(job_id,processprotocol.exitcode,processprotocol.out,processprotocol.err)
                client_stream.write("Failed - %s\n"%(processprotocol.err))
                client_stream.finish()
                return
            
            newstate = processprotocol.jobstate
            if state!=newstate:
                state=newstate
                client_stream.write("%s\n"%state)
            
            
        client_stream.finish()
       