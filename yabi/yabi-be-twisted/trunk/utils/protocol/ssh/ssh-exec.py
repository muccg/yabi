#!/usr/bin/python
# -*- coding: utf-8 -*-

# ssh execution helper. Can deal with passphrased keys and passwords and stuff

import sys, re, os
from optparse import OptionParser
import subprocess
import pexpect
import StringIO

for delkey in ['DISPLAY','SSH_AGENT_PID','SSH_AUTH_SOCK']:
    if delkey in os.environ:
        del os.environ[delkey]

def eprint(text):
    sys.stderr.write(text)
    sys.stderr.write("\n")

SSH = "/usr/bin/ssh"
BLOCK_SIZE = 1024
TIMEOUT = 0.2

L2R = 1
R2L = 2
direction = None

parser = OptionParser()
parser.add_option( "-i", "--identity", dest="identity", help="RSA keyfile" )
parser.add_option( "-C", "--compress", dest="compress", help="use ssh stream compression", action="store_true", default=False )
parser.add_option( "-P", "--port", dest="port", help="port to connect to ssh on" )
parser.add_option( "-o", "--stdout", dest="stdout", help="filename for standard out", default=None )
parser.add_option( "-e", "--stderr", dest="stderr", help="filename for standard error",default=None )
parser.add_option( "-x", "--execute", dest="execute", help="command to execute", default="hostname" )
parser.add_option( "-w", "--working", dest="working", help="working directory", default=None )

(options, args) = parser.parse_args()

#print "options",options
#print "args",args

if len(args)!=1:
    eprint("Error: Must specify user@host on command line")
    sys.exit(2)
    
remote_command = options.execute
stdout = options.stdout
stderr = options.stderr
    
extra_args = []
if options.identity:
    extra_args.extend(["-i",options.identity])
if options.compress:
    extra_args.extend(["-C"])
if options.port:
    extra_args.extend(["-p",options.port])
    
password = sys.stdin.readline().rstrip('\n')

user, host = args[0].split('@',1)

# sanity check out command. If there are quotes (that are unescaped) the outermost ones must be doubles
quotes = [X for N,X in enumerate(remote_command) if (X=='"' or X=="'") and N>=1 and remote_command[N-1]!='\\']

#if len(quotes):
    #assert quotes[0]=='"' and quotes[-1]=='"', "Quotes in command must be doublequote outermost"

if stdout or stderr:
    ssh_command = extra_args+["%s@%s"%(user,host),"cd \"%s\" && %s 1>%s 2>%s"%(options.working,remote_command,stdout,stderr)]
else:
    if options.working:
        ssh_command = extra_args+["%s@%s"%(user,host),+"cd \"%s\" && %s"%(options.working,remote_command)]
    else:
        ssh_command = extra_args+["%s@%s"%(user,host),remote_command]

eprint("SSH Command: %s"%(ssh_command))

child = pexpect.spawn(SSH, args=ssh_command)
child.logfile_read = sys.stdout
res = 0
while res!=2:
    res = child.expect(["passphrase for key .+:","password:", "Permission denied",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
    if res<=1:
        # send password
        #eprint("sending password")
        child.sendline(password)
    elif res==2:
        # password failure
        eprint("Access denied")
        sys.exit(1)
        
    elif res==3:
        child.delaybeforesend=0
        #eprint("sending EOF")
        child.sendeof()
        if child.isalive():
            #eprint("waiting")
            child.wait()
        
        sys.exit(child.exitstatus)
    
    else:
        # EOF or timeout
        pass
