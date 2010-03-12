#!/usr/bin/python
# -*- coding: utf-8 -*-

# scp equivalent, that uses streams and ssh to copy a stream based file to a remote server

import sys, re, os
from optparse import OptionParser
import subprocess
import pexpect

del os.environ['DISPLAY']

SSH = "/usr/bin/ssh"
BLOCK_SIZE = 8192

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

print "options",options
print "args",args

if len(args)!=2:
    print "Error: Must have input and output file specified"
    sys.exit(2)
    
infile, outfile = args

if options.l2r and options.r2l:
    print "ERROR: copy can only be remote-to-local or local-to-remote, not both"
    sys.exit(1)
    
if not options.l2r and not options.r2l:
    # attempt to guess direction
    re_remote = re.compile("^.+@.+:.+$")
    if re_remote.search(infile) and not re_remote.search(outfile):
        direction = R2L
    elif re_remote.search(outfile) and not re_remote.search(infile):
        direction = L2R
    else:
        print "ERROR: cannot guess copy direction. please specify on command line"
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
    
if direction == L2R:
    # 
    # Local to Remote
    #
    hostpart, path = outfile.split(':',1)
    user, host = hostpart.split('@',1)
        
    command = [SSH] + extra_args + [ "%s@%s"%(user,host), "cat >'%s'"%path]
    print command
    
    command = "/usr/bin/ssh "+(" ".join(extra_args))+" %s@%s"%(user,host)+" \"cat >'%s'\""%path+"</dev/null"
    print command
    
    child = pexpect.spawn(command)
    res = 0
    while res!=2:
        res = child.expect(["passphrase for key","password:",pexpect.EOF, pexpect.TIMEOUT],timeout=5)
        if res<=1:
            # send password
            print "RES:",res
            child.sendline("lollipop")
        elif res==2:
            # EOF! connection closed
            print "EOF!"
            
            # write input file in
            fh = open(infile,'rb')
            reading = True
            while reading:
                dat=fh.read(BLOCK_SIZE)
                if len(dat):
                    print "writing:",len(dat)
                    child.write(dat)
                else:
                    reading=False
            child.sendeof()           
            
            sys.exit(1)
    
    # timeout waiting, lets send our data
    print "logged in"
    sys.exit(0)
    #proc = subprocess.Popen( command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False )

    # write input file in
    fh = open(infile,'rb')
    reading = True
    while reading:
        dat=fh.read(BLOCK_SIZE)
        if len(dat):
            proc.stdin.write(dat)
        else:
            reading=False
    proc.stdin.close()

    if proc.wait() != 0:
        print "ERROR:",proc.stdout.read(),proc.stderr.read()
        sys.exit(3)
    else:
        print proc.stdout.read()
        sys.exit(0)
        
elif direction == R2L:
    #
    # Remote to Local
    #
    hostpart, path = infile.split(':',1)
    user, host = hostpart.split('@',1)
    
    proc = subprocess.Popen( [SSH] + extra_args + [ "%s@%s"%(user,host), "cat '%s'"%path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True )
    proc.stdin.close()
    
    # read file outfile
    fh = open(outfile, 'wb')
    reading = True
    while reading:
        dat=proc.stdout.read(BLOCK_SIZE)
        if len(dat):
            fh.write(dat)
        else:
            reading=False
    fh.close()

    if proc.wait() != 0:
        print "ERROR:",proc.stdout.read(),proc.stderr.read()
        sys.exit(4)
    else:
        print proc.stdout.read()
        sys.exit(0)