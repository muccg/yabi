#!/usr/bin/python
# -*- coding: utf-8 -*-

# s3 copying script, that uses streams to copy a stream based file to an s3 bucket

import sys, re, os
from optparse import OptionParser
import S3

def eprint(text):
    sys.stderr.write(text)
    sys.stderr.write("\n")

DEBUG = False

L2R = 1
R2L = 2
direction = None

parser = OptionParser()
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
    re_remote = re.compile("^.+@.+:.+$")                                            # bucket@s3host/path
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
        
# read in access key, and then secret key over stdin
accesskey = sys.stdin.readline().rstrip('\n')
secretkey = sys.stdin.readline().rstrip('\n')

if DEBUG:
    print "DIR:",direction
    print "IN:",infile
    print "OUT:",outfile

if direction == L2R:
    # 
    # Local to Remote
    #
    hostpart, path = outfile.split(':',1)
    username, host = hostpart.split('@',1)
    
    bucket = host.split('.')[0]
    
    while len(path) and path[0]=='/':
        path = path[1:]
    
    # create a connection object
    conn = S3.AWSAuthConnection(accesskey, secretkey)
    response = conn.put(bucket,path,open(infile,"rb").read())
    
    if response.http_response.status == 200:
        # success.
        eprint("OK")
        sys.exit(0)
        
    # report error
    eprint("copy to s3 bucket '%s' on host '%s' key '%s' from local file '%s' failed: %s"%(bucket,host,path,infile,response.message))
    sys.exit(1)
    
elif direction == R2L:
    #
    # Remote to Local
    #
    hostpart, path = infile.split(':',1)
    username, host = hostpart.split('@',1)
    
    bucket = host.split('.')[0]
    
    while len(path) and path[0]=='/':
        path = path[1:]
    
    # create connection
    conn = S3.AWSAuthConnection(accesskey,secretkey)
    response = conn.get(bucket,path)
    
    if response.http_response.status == 200:
        # success
        print "response.body=",response.body
        print "dest=",outfile
        fh = open(outfile,"wb")
        print "fh=",fh
        fh.write(response.body)
        fh.close()
        eprint("OK")
        sys.exit(0)
        
    #report error
    eprint("copy from s3 bucket '%s' on host '%s' key '%s' to local file '%s' failed: %s"%(bucket,host,path,outfile,response.message))
    sys.exit(1)
        
            
          