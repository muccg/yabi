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

SSH = "/usr/bin/ssh"
BLOCK_SIZE = 1024
TIMEOUT = 0.2
FULL_TIMEOUT = 10.0

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
    
#password = sys.stdin.readline().rstrip('\n')
password = "lollipop"
print "PASS<",password,">"

if direction == L2R:
    # 
    # Local to Remote
    #
    hostpart, path = outfile.split(':',1)
    user, host = hostpart.split('@',1)
        
    command = [SSH] + extra_args + [ "%s@%s"%(user,host), "cat >'%s'"%path]
    print command
    
    command = "/usr/bin/ssh "+(" ".join(extra_args))+" %s@%s"%(user,host)+" \"echo -BEGIN- && base64 -w 0 -d > '%s' \""%path
    #command = "/usr/bin/ssh "+(" ".join(extra_args))+" %s@%s"%(user,host)+" \"echo -BEGIN- ; cat>'%s' \""%path
    #command = "/usr/bin/ssh "+(" ".join(extra_args))+" %s@%s"%(user,host)+" \"/bin/cat>/dev/null\""
    print command
    
    child = pexpect.spawn(command)
    child.setecho(False)
    child.logfile_read = sys.stdout
    res = 0
    while res!=2:
        res = child.expect(["passphrase for key .+:","password:", "Permission denied","-BEGIN-",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
        print "RES:",res
        if res<=1:
            # send password
            print "sending",password
            child.sendline(password)
        elif res==2:
            # password failure
            print "Access denied"
            sys.exit(1)
            
        elif res==3:
            child.delaybeforesend=0
            
            # encode input file
            proc = subprocess.Popen("base64 -w 0 '%s'"%infile, bufsize=BLOCK_SIZE, shell=True, stdout=subprocess.PIPE)
            fh = proc.stdout
            print "!!!"
            print child.isalive()
            
            reading = True
            while reading:
                dat=fh.read(BLOCK_SIZE)
                if len(dat):
                    print "==="
                    print dat
                    print child.send(dat+"\r\n")
                    #print child.isalive()
                else:
                    reading = False
            
            child.sendcontrol('d')
            child.sendeof()
            fh.close()
            
            child.wait()
            
                       
            print "RESULT",child.exitstatus
            sys.exit(0)
        
        elif res==4:
            # EOF
            pass
        
        elif res==5:
            # Timeout
            pass
        
elif direction == R2L:
    #
    # Remote to Local
    #
    hostpart, path = infile.split(':',1)
    user, host = hostpart.split('@',1)
    
    command = [SSH] + extra_args + [ "%s@%s"%(user,host), "cat '%s'"%path]
    print command
    
    command = "/usr/bin/ssh "+(" ".join(extra_args))+" %s@%s"%(user,host)+" \"echo -BEGIN- && base64 -w 0 '%s' && echo -END-\""%path
    print command
    
    child = pexpect.spawn(command)
    child.logfile_read = StringIO.StringIO()
    data_flow = False                           # once dataflow begins, set this to true
    timeout_count = 0                           # how many times weve hit a timeout
    res = 0
    while res!=2:
        res = child.expect(["passphrase for key .+:","password:","Permission denied","-BEGIN-",pexpect.EOF,pexpect.TIMEOUT],timeout=TIMEOUT)
        print "RES:",res
        if res<=1:
            # send password
            print "sending",password
            child.sendline(password)
            child.logfile_read = StringIO.StringIO()            # reset data buffer
            
            data_flow = True
            
        elif res==3:
            # BEGIN
            child.delaybeforesend=0             # switch off echo selay so we can stream the data fullspeed
            
            # write input file in
            #fh = open(outfile,'wb')
            proc = subprocess.Popen("base64 -w 0 -d > '%s'"%outfile, bufsize=BLOCK_SIZE, shell=True, stdin=subprocess.PIPE)
            fh = proc.stdin
            
            reading = True
            dat=""
            while reading:
                dat+=child.read(BLOCK_SIZE)
                if len(dat):
                    if dat.count("-")==1:
                        # half a tag! we have to join this with the next block to get the full tag
                        continue
                    print "writing:",len(dat)
                    fh.write(dat.replace("\r\n","").replace(" ","").replace("-BEGIN-","").replace("-END-",""))
                    dat=""
                else:
                    reading=False
            child.sendeof()  
            fh.close()
            
            if proc.wait()!=0:
                print "There were ERRORS"
                sys.exit(1)
            
            sys.exit(0)
            
        elif res==5:
            if data_flow:
                if timeout_count > FULL_TIMEOUT/TIMEOUT:
                    print "Access denied"
                    sys.exit(2)
                else:
                    timeout_count += 1
        elif res==2:
            # password failure!
            print "Access denied"
            sys.exit(1)
        elif res==4:
            # EOF. the whole file may have been delivered just then!
            data = child.logfile_read.getvalue()
            assert data[0:2]=="\r\n", "echod back carridge return from password input is missing!"
                        
            fh = open(outfile,'wb')
            fh.write(data[2:].replace("\r\n","").replace(" ","").replace("-BEGIN-","").replace("-END-",""))
            fh.close()
            child.sendeof()
            sys.exit(0)
        
            
          