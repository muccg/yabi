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

from ExecConnector import ExecConnector, ExecutionError, JobPollGeneratorDefault,rerun_delays
import traceback

# a list of system environment variables we want to "steal" from the launching environment to pass into our execution environments.
ENV_CHILD_INHERIT = ['PATH']

# a list of environment variables that *must* be present for this connector to function
ENV_CHECK = []

# the schema we will be registered under. ie. schema://username@hostname:port/path/
SCHEMA = "ssh+sge"

DEBUG = False

from twistedweb2 import http, responsecode, http_headers, stream

import os
import uuid
import json
import gevent

from utils.geventtools import sleep
from utils.protocol import ssh
from utils.RetryController import SSHSGEQsubRetryController, SSHSGEQstatRetryController, SSHSGEQacctRetryController, HARD

from conf import config

# where we temporarily store the submission scripts on the submission host
TMP_DIR = config.config['backend']['temp']
REMOTE_TMP_DIR = '/tmp'

from TaskManager.TaskTools import RemoteInfo
from SubmissionTemplate import make_script

from twisted.python import log

sshauth = ssh.SSHAuth.SSHAuth()
qsubretry = SSHSGEQsubRetryController()
qstatretry = SSHSGEQstatRetryController()
qacctretry = SSHSGEQacctRetryController()


# now we inherit our particular errors
class SSHQsubException(Exception):
    pass


class SSHQstatException(Exception):
    pass


class SSHTransportException(Exception):
    pass


# and further inherit hard and soft under those
class SSHQsubSoftException(Exception):
    pass


class SSHQstatSoftException(Exception):
    pass


class SSHQsubHardException(Exception):
    pass


class SSHQstatHardException(Exception):
    pass


class SSHQacctSoftException(Exception):
    pass


class SSHQacctHardException(Exception):
    pass


class SSHSGEConnector(ExecConnector, ssh.KeyStore.KeyStore):

    def __init__(self):
        ExecConnector.__init__(self)

        configdir = config.config['backend']['certificates']
        ssh.KeyStore.KeyStore.__init__(self, dir=configdir)

    def _ssh_qsub(self,
                  yabiusername,
                  creds,
                  command,
                  working,
                  username,
                  host,
                  remoteurl,
                  submission,
                  stdout,
                  stderr,
                  modules,
                  walltime,
                  memory,
                  cpus,
                  queue,
                  tasknum,
                  tasktotal):
        """This submits via ssh the qsub command. This returns the jobid, or raises an exception on an error"""
        assert type(modules) is not str and type(modules) is not unicode, "parameter modules should be sequence or None, not a string or unicode"

        submission_script = os.path.join(REMOTE_TMP_DIR, str(uuid.uuid4()) + ".sh")

        qsub_submission_script = "'%s' -N '%s' -e '%s' -o '%s' -wd '%s' '%s'" % (
            config.config[SCHEMA]['qsub'],
            "yabi-" + remoteurl.rsplit('/')[-1],
            os.path.join(working, stderr),
            os.path.join(working, stdout),
            working,
            submission_script
        )

        # build up our remote qsub command
        ssh_command = "cat >'%s' && " % (submission_script)
        ssh_command += qsub_submission_script
        ssh_command += " ; EXIT=$? "
        ssh_command += " ; rm '%s'" % (submission_script)
        #ssh_command += " ; echo $EXIT"
        ssh_command += " ; exit $EXIT"

        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, "/", credtype="exec")

        usercert = self.save_identity(creds['key'])

        script_string = make_script(submission, working, command, modules, cpus, memory, walltime, yabiusername, username, host, queue, stdout, stderr, tasknum, tasktotal)

        # hande log setting
        if config.config['execution']['logcommand']:
            print SCHEMA + " attempting submission command: " + qsub_submission_script

        if config.config['execution']['logscripts']:
            print SCHEMA + " submission script:"
            print script_string

        if DEBUG:
            print "usercert:", usercert
            print "command:", command
            print "username:", username
            print "host:", host
            print "working:", working
            print "port:", "22"
            print "stdout:", stdout
            print "stderr:", stderr
            print "modules", modules
            print "password:", "*" * len(creds['password'])
            print "script:", script_string

        pp = ssh.Run.run(usercert, ssh_command, username, host, working=None, port="22", stdout=None, stderr=None, password=creds['password'], modules=modules, streamin=script_string)
        while not pp.isDone():
            gevent.sleep()

        if DEBUG:
            print "EXITCODE:", pp.exitcode
            print "STDERR:", pp.err
            print "STDOUT:", pp.out

        if pp.exitcode == 0:
            # success
            jobid_string = pp.out.strip().split("\n")[-1]
            return jobid_string.split('("')[-1].split('")')[0]
        else:
            error_type = qsubretry.test(pp.exitcode, pp.err)
            if error_type == HARD:
                # hard error
                raise SSHQsubHardException("Error: SSH exited %d with message %s" % (pp.exitcode, pp.err))

        #soft error
        raise SSHQsubSoftException("Error: SSH exited: %d with message %s" % (pp.exitcode, pp.err))

    def _ssh_qstat(self, yabiusername, creds, command, working, username, host, stdout, stderr, modules, jobid):
        """This submits via ssh the qstat command. This takes the jobid"""
        assert type(modules) is not str and type(modules) is not unicode, "parameter modules should be sequence or None, not a string or unicode"

        ssh_command = "cat > /dev/null && '%s' -f -j '%s'" % (config.config[SCHEMA]['qstat'], jobid)

        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, "/", credtype="exec")

        usercert = self.save_identity(creds['key'])

        if DEBUG:
            print "usercert:", usercert
            print "command:", command
            print "username:", username
            print "host:", host
            print "working:", working
            print "port:", "22"
            print "stdout:", stdout
            print "stderr:", stderr
            print "modules", modules
            print "password:", "*" * len(creds['password'])

        pp = ssh.Run.run(usercert, ssh_command, username, host, working=None, port="22", stdout=None, stderr=None, password=creds['password'], modules=modules)
        while not pp.isDone():
            gevent.sleep()

        if pp.exitcode == 0:
            # success. lets process our qstat results
            output = {}

            for line in pp.out.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    output[key] = value.strip()

            return {jobid: output}
        else:
            # otherwise we need to analyse the result to see if its a hard or soft failure
            error_type = qstatretry.test(pp.exitcode, pp.err)
            if error_type == HARD:
                # hard error.
                raise SSHQstatHardException("Error: SSH exited %d with message %s" % (pp.exitcode, pp.err))

        # everything else is soft
        raise SSHQstatSoftException("Error: SSH exited %d with message %s" % (pp.exitcode, pp.err))

    def _ssh_qacct(self, yabiusername, creds, command, working, username, host, stdout, stderr, modules, jobid):
        """This submits via ssh the qstat command. This takes the jobid"""
        assert type(modules) is not str and type(modules) is not unicode, "parameter modules should be sequence or None, not a string or unicode"

        ssh_command = "cat > /dev/null && '%s' -j '%s'" % (config.config[SCHEMA]['qacct'], jobid)

        if not creds:
            creds = sshauth.AuthProxyUser(yabiusername, SCHEMA, username, host, "/", credtype="exec")

        usercert = self.save_identity(creds['key'])

        if DEBUG:
            print "usercert:", usercert
            print "command:", command
            print "username:", username
            print "host:", host
            print "working:", working
            print "port:", "22"
            print "stdout:", stdout
            print "stderr:", stderr
            print "modules", modules
            print "password:", "*" * len(creds['password'])

        pp = ssh.Run.run(usercert, ssh_command, username, host, working=None, port="22", stdout=None, stderr=None, password=creds['password'], modules=modules)
        while not pp.isDone():
            gevent.sleep()

        if pp.exitcode == 0:
            # success. lets process our qstat results
            output = {}

            for line in pp.out.split("\n"):
                line = line.strip()
                if " " in line:
                    key, value = line.split(None, 1)
                    output[key] = value.strip()

            return {jobid: output}
        else:
            # otherwise we need to analyse the result to see if its a hard or soft failure
            error_type = qacctretry.test(pp.exitcode, pp.err)
            if error_type == HARD:
                # hard error.
                raise SSHQacctHardException("SSHQacct Error: SSH exited %d with message %s" % (pp.exitcode, pp.err))

        # everything else is soft
        raise SSHQacctSoftException("SSHQacct Error: SSH exited %d with message %s" % (pp.exitcode, pp.err))

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

        modules = [] if not module else [X.strip() for X in module.split(",")]
        delay_gen = rerun_delays()

        while True:
            try:
                jobid = self._ssh_qsub(yabiusername, creds, command, working, username, host, remoteurl, submission, stdout, stderr, modules, walltime, memory, cpus, queue, tasknum, tasktotal)
                break               # success... escape retry loop
            except (SSHQsubHardException, ExecutionError), ee:
                traceback.print_exc()
                channel.callback(http.Response(responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream=str(ee)))
                return
            except SSHQsubSoftException, softexc:
                print "Retrying qsub " + str(softexc)
                #delay then retry
                try:
                    sleep(delay_gen.next())
                except StopIteration:
                    print "No more retries for qsub soft exception"
                    # run out of retries
                    channel.callback(http.Response(responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream=str(softexc)))
                    return

        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        channel.callback(http.Response(responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=client_stream))

        # now the job is submitted, lets remember it
        self.add_running(jobid, {'username': username})

        # lets report our id to the caller
        client_stream.write("id=%s\n" % jobid)

        try:
            self.main_loop(yabiusername, creds, command, working, username, host, remoteurl, client_stream, stdout, stderr, modules, jobid)
        except (ExecutionError, SSHQstatException):
            traceback.print_exc()
            client_stream.write("Error\n")
        finally:

            # delete finished job
            self.del_running(jobid)

            client_stream.finish()

    def resume(self, jobid, yabiusername, creds, command, working, scheme, username, host, remoteurl, channel, stdout="STDOUT.txt", stderr="STDERR.txt", walltime=60, memory=1024, cpus=1, queue="testing", jobtype="single", module=None, tasknum=None, tasktotal=None):
        # send an OK message, but leave the stream open
        client_stream = stream.ProducerStream()
        modules = [] if not module else [X.strip() for X in module.split(",")]

        try:
            username = self.get_running(jobid)['username']
        except KeyError:
            channel.callback(http.Response(responsecode.INTERNAL_SERVER_ERROR, {'content-type': http_headers.MimeType('text', 'plain')}, stream="No such jobid resumable: %s" % jobid))

        channel.callback(http.Response(responsecode.OK, {'content-type': http_headers.MimeType('text', 'plain')}, stream=client_stream))

        self.main_loop(yabiusername, creds, command, working, username, host, remoteurl, client_stream, stdout, stderr, modules, jobid)

        # delete finished job
        self.del_running(jobid)

        client_stream.finish()

    def main_loop(self, yabiusername, creds, command, working, username, host, remoteurl, client_stream, stdout, stderr, modules, jobid):
        newstate = state = None
        delay = JobPollGeneratorDefault()
        while state != "Done":
            # pause
            sleep(delay.next())

            delay_gen = rerun_delays()
            while True:
                try:
                    jobsummary = self._ssh_qstat(yabiusername, creds, command, working, username, host, stdout, stderr, modules, jobid)

                    # TODO HACK FIXME:
                    # SGE code is broken, we don't get a job_state
                    # setting to job_state R, then fall through to qacct when qstat can't find job
                    jobsummary[jobid]['job_state'] = 'R'
                    break           # success
                except (SSHQstatSoftException, SSHTransportException), softexc:
                    # delay and then retry
                    try:
                        sleep(delay_gen.next())
                    except StopIteration:
                        # run out of retries.
                        raise softexc

                except SSHQstatHardException, qse:
                    if "Following jobs do not exist" in str(qse):
                        # job has errored or completed. We now search using qacct
                        qacctdelay_gen = rerun_delays()
                        while True:
                            try:
                                jobsummary = self._ssh_qacct(yabiusername, creds, command, working, username, host, stdout, stderr, modules, jobid)
                                break
                            except (SSHQacctSoftException, SSHTransportException), softexc:
                                # delay and then retry
                                try:
                                    sleep(qacctdelay_gen.next())
                                except StopIteration:
                                    # run out of retries.
                                    raise softexc

                        # TODO HACK FIXME:
                        # SGE code is broken, we don't get a job_state
                        # setting to job_state R, then fall through to qacct when qstat can't find job
                        if 'failed' in jobsummary[jobid] and 'exit_status' in jobsummary[jobid] and \
                                jobsummary[jobid]['failed'] != 'undefined' and jobsummary[jobid]['exit_status'] != 'undefined':
                            jobsummary[jobid]['job_state'] = 'C'
                        else:
                            jobsummary[jobid]['job_state'] = 'R'

                        break

            self.update_running(jobid, jobsummary)

            if jobid in jobsummary:
                # job has not finished
                if 'job_state' not in jobsummary[jobid]:
                    newstate = "Unsubmitted"
                else:
                    status = jobsummary[jobid]['job_state']

                    log_msg = "ssh+sge jobid:%s is status:%s..." % (jobid, status)

                    if status == 'C':
                        #print "STATUS IS C <=============================================================",jobsummary[jobid]['exit_status']
                        # state 'C' means complete OR error
                        if 'exit_status' in jobsummary[jobid]:
                            log_msg += "exit status present and it is %s" % jobsummary[jobid]['exit_status']

                        if 'exit_status' in jobsummary[jobid] and jobsummary[jobid]['exit_status'] == '0':
                            newstate = "Done"
                        else:
                            newstate = "Error"
                    else:
                        newstate = dict(Q="Unsubmitted", E="Running", H="Pending", R="Running", T="Pending", W="Pending", S="Pending")[status]

                    log.msg(log_msg + " thus we are setting state to: %s" % newstate)
            else:
                # job has finished
                sleep(15.0)                      # deal with SGE flush bizarreness (files dont flush from remote host immediately. Totally retarded)
                print "ERROR: jobid %s not in jobsummary" % jobid
                print "jobsummary is", jobsummary

                # if there is standard error from the qstat command, report that!
                newstate = "Error"
            if DEBUG:
                print "Job summary:", jobsummary

            if state != newstate:
                state = newstate
                #print "Writing state",state
                client_stream.write("%s\n" % state)

                # report the full status to the remoteurl
                if remoteurl:
                    if jobid in jobsummary:
                        RemoteInfo(remoteurl, json.dumps(jobsummary[jobid]))
                    else:
                        print "Cannot call RemoteInfo call for job", jobid

            if state == "Error":
                #print "CLOSING STREAM"
                client_stream.finish()
                return
