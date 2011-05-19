#!/usr/bin/python
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

# scp equivalent, that uses streams and ssh to copy a stream based file to a remote server

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
    sys.stdout.write(text)
    sys.stdout.write("\n")
    
def escapequotes(filename):
    # encode these chars into \xNN codes
    CHARS_TO_REPLACE = '\\' + "'" + '"' + "$@!~|<>#;*[]{}?%^&()= "
    for char in CHARS_TO_REPLACE:
        filename=filename.replace(char,"\\x%x"%(ord(char)))
    return filename

DEBUG = False

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
parser.add_option( "-L", "--local-to-remote", dest="l2r", help="force local to remote" )
parser.add_option( "-R", "--remote-to-local", dest="r2l", help="force remote to local" )

(options, args) = parser.parse_args()

#print "options",options
#print "args",args

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
        eprint("ERROR: cannot guess copy direction. please specify on command line")
        sys.exit(2)
elif options.l2r:
    direction = L2R
elif options.r2l:
    direction = R2L
    
extra_args = []
if options.identity:
    extra_args.extend(["-i",options.identity])
if options.compress:
    extra_args.extend(["-C"])
if options.port:
    extra_args.extend(["-p",options.port])
    
password = sys.stdin.readline().rstrip('\n')

if DEBUG:
    print "DIR:",direction
    print "IN:",infile
    print "OUT:",outfile

if direction == L2R:
    # 
    # Local to Remote
    #
    hostpart, path = outfile.split(':',1)
    user, host = hostpart.split('@',1)
        
    ssh_command = ("cat %s | %s "+(" ".join(extra_args))+" %s@%s"%(user,host)+' "cat>\\"%s\\""')%(infile,SSH,escapequotes(path))
    ssh_command = ("cat %s | %s "+(" ".join(extra_args))+" %s@%s"%(user,host)+' "cat > \\"\\`echo -e \'%s\'\\`\\""')%(infile,SSH,escapequotes(path))
    command = '/bin/bash' 
    args = ['-c',ssh_command]
    
    if DEBUG:
        eprint("SSH_COMMAND: %s"%ssh_command)
        eprint("command: %s args: %s"%(command,str(args)))
        eprint("[-1]: %s"%(args[-1]))
    
    child = pexpect.spawn(command,args=args)
    child.logfile_read = StringIO.StringIO()
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
            
            eprint(child.logfile_read.getvalue())
            sys.exit(child.exitstatus)
        
        else:
            # EOF or timeout
            pass
        
elif direction == R2L:
    #
    # Remote to Local
    #
    hostpart, path = infile.split(':',1)
    user, host = hostpart.split('@',1)
    
    ssh_command = ("%s "+(" ".join(extra_args))+" %s@%s"%(user,host)+' "cat \\"%s\\"" > %s')%(SSH,path,escapequotes(outfile))
    command = '/bin/bash'
    args = ['-c',ssh_command]
    
    if DEBUG:
        eprint("SSH_COMMAND: %s"%ssh_command)
        eprint("command: %s args: %s"%(command,str(args)))
        eprint("[-1]: %s"%(args[-1]))
    
    child = pexpect.spawn(command, args=args)
    child.logfile_read = StringIO.StringIO()
    res = 0
    while res!=2:
        res = child.expect(["passphrase for key .+:","password:","Permission denied",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
        if res<=1:
            # send password
            child.sendline(password)
            
        elif res==3:
            child.delaybeforesend=0
            child.sendeof()
            if child.isalive():
                child.wait()
                
            eprint(child.logfile_read.getvalue())
            sys.exit(child.exitstatus)
            
        elif res==2:
            # password failure!
            print "Access denied"
            sys.exit(1)
            
        else:
            pass
        
            
          
