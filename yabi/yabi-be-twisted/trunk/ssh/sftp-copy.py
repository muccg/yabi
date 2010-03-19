#!/usr/bin/python
# -*- coding: utf-8 -*-

# scp equivalent, that uses streams and ssh to copy a stream based file to a remote server

import sys, re, os
from optparse import OptionParser
import subprocess
import pexpect
import StringIO

for delkey in ['DISPLAY','SSH_AGENT_PID','SSH_AUTH_SOCK']:
    if delkey in os.environ:
        del os.environ[delkey]

SFTP = "/usr/bin/sftp"
BLOCK_SIZE = 1024
TIMEOUT = 0.2

L2R = 1
R2L = 2
direction = None

parser = OptionParser()
parser.add_option( "-i", "--identity", dest="identity", help="RSA keyfile" )
parser.add_option( "-P", "--port", dest="port", help="port to connect to ssh on" )
parser.add_option( "-L", "--local-to-remote", dest="l2r", help="force local to remote" )
parser.add_option( "-R", "--remote-to-local", dest="r2l", help="force remote to local" )

(options, args) = parser.parse_args()

def eprint(*args, **kwargs):
    sys.stderr.write(*args,**kwargs)
    sys.stderr.write("\r\n")

if len(args)!=2:
    eprint("Error: Must have input and output file specified")
    sys.exit(2)
    
infile, outfile = args

if options.l2r and options.r2l:
    eprint("ERROR: copy can only be remote-to-local or local-to-remote, not both")
    sys.exit(1)
    
if not options.l2r and not options.r2l:
    # attempt to guess direction
    re_remote = re.compile("^.+@.+:.+$")
    if re_remote.search(infile) and not re_remote.search(outfile):
        direction = R2L
    elif re_remote.search(outfile) and not re_remote.search(infile):
        direction = L2R
    else:
        eprint ("ERROR: cannot guess copy direction. please specify on command line")
        sys.exit(2)
elif options.l2r:
    direction = L2R
elif options.r2l:
    direction = R2L
    
extra_args = []
if options.identity:
    extra_args.extend(["-oIdentityFile=%s"%options.identity])
if options.port:
    extra_args.extend(["-oPort=%s"%options.port])
    
password = sys.stdin.readline().rstrip('\n')

if direction == L2R:
    # 
    # Local to Remote
    #
    hostpart, path = outfile.split(':',1)
    user, host = hostpart.split('@',1)
        
    command = SFTP+" "+(" ".join(extra_args))+" %s@%s"%(user,host)
    
    child = pexpect.spawn(command)
    child.setecho(False)
    res = 0
    while res!=2:
        res = child.expect(["passphrase for key .+:","password:", "Permission denied","sftp>",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
        if res<=1:
            # send password
            child.sendline(password)
        elif res==2:
            # password failure
            eprint("Access denied")
            sys.exit(1)
            
        elif res==3:
            #child.delaybeforesend=0
            
            # save our output for results
            log = StringIO.StringIO()
            child.logfile_read = log
            
            # send put command
            child.sendline("put '%s' '%s'"%(infile,path))
            
            # now lets wait until the upload is finished, or the task fails.
            res = 2
            while res==2:
                res = child.expect( ['sftp>',pexpect.EOF,pexpect.TIMEOUT], timeout=TIMEOUT )
            
            if res==1:
                eprint("Error. Premature EOF in pty of sftp client")
                sys.exit(1)
                
            result = log.getvalue()
            resultlines = [X.strip() for X in result.split("\r") if not 'sftp>' in X and len(X.strip())]
            status = resultlines[-1]
            
            child.sendline("quit")
            child.wait()
                       
            if "100%" in status and status.startswith(infile):
                eprint("OK %s"%status)
                sys.exit(0)
            else:
                eprint("ERROR %s"%status)
                sys.exit(1)
        
        elif res==4:
            # EOF
            eprint("Error. Premature EOF in pty of sftp client")
            sys.exit(1) 
        
        elif res==5:
            # Timeout
            pass
        
elif direction == R2L:
    #
    # Remote to Local
    #
    hostpart, path = infile.split(':',1)
    user, host = hostpart.split('@',1)
    
    command = SFTP+" "+(" ".join(extra_args))+" %s@%s"%(user,host)
    
    child = pexpect.spawn(command)
    child.setecho(False)
    res = 0
    while res!=2:
        res = child.expect(["passphrase for key .+:","password:", "Permission denied","sftp>",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
        if res<=1:
            # send password
            child.sendline(password)
        elif res==2:
            # password failure
            eprint("Access denied")
            sys.exit(1)
            
        elif res==3:
            #child.delaybeforesend=0
            
            # save our output for results
            log = StringIO.StringIO()
            child.logfile_read = log
            
            # send get command
            child.sendline("get '%s' '%s'"%(path,outfile))
            
            # now lets wait until the upload is finished, or the task fails.
            res = 2
            while res==2:
                res = child.expect( ['sftp>',pexpect.EOF,pexpect.TIMEOUT], timeout=TIMEOUT )
                eprint("RES:%s"%res)
            
            if res==1:
                eprint("Error. Premature EOF in pty of sftp client")
                sys.exit(1)
                
            result = log.getvalue()
            eprint("RESULT")
            eprint(result)
            resultlines = [X.strip() for X in result.split("\r") if not 'sftp>' in X and len(X.strip())]
            status = resultlines[-1]
            
            child.sendline("quit")
            child.wait()
                       
            if "100%" in status and status.startswith(path):
                eprint("OK %s"%status)
                sys.exit(0)
            else:
                eprint("ERROR %s"%status)
                sys.exit(1)
        
        elif res==4:
            # EOF
            eprint("Error. Premature EOF in pty of sftp client")
            sys.exit(1) 
        
        elif res==5:
            # Timeout
            pass
        
          