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
parser.add_option( "-o", "--stdout", dest="stdout", help="filename for standard out", default="STDOUT.txt" )
parser.add_option( "-e", "--stderr", dest="stderr", help="filename for standard error",default="STDERR.txt" )
parser.add_option( "-x", "--execute", dest="execute", help="command to execute", default="hostname" )

(options, args) = parser.parse_args()

#print "options",options
#print "args",args

if len(args)!=2:
    eprint("Error: Must have input and output file specified")
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

# 
# Local to Remote
#
hostpart, path = outfile.split(':',1)
user, host = hostpart.split('@',1)

ssh_command = ("%s "+(" ".join(extra_args))+" %s@%s"%(user,host)+" '%s 1>%s 2>%s'")%(SSH,remote_command,stdout,stderr)

child = pexpect.spawn(ssh_command)
res = 0
while res!=2:
    res = child.expect(["passphrase for key .+:","password:", "Permission denied",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
    if res<=1:
        # send password
        #print "sending",password
        child.sendline(password)
    elif res==2:
        # password failure
        eprint("Access denied")
        sys.exit(1)
        
    elif res==3:
        child.delaybeforesend=0
        child.sendeof()
        if child.isalive():
            child.wait()
        
        sys.exit(child.exitstatus)
    
    else:
        # EOF or timeout
        pass
