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

# s3 copying script, that uses streams to copy a stream based file to an s3 bucket

import sys, re, os, time
from optparse import OptionParser
from boto.s3.connection import S3Connection 
from boto.s3.key import Key

def eprint(text):
    sys.stderr.write(text)
    sys.stderr.write("\n")

DEBUG = True

CHUNKSIZE = 4096

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
    conn = S3Connection(accesskey, secretkey)
    
    k = Key(bucket)
    k.key = path
    k.set_contents_from_filename(infile)
    
    # success.
    eprint("OK")
    sys.exit(0)
        
    # report error
    #eprint("copy to s3 bucket '%s' on host '%s' key '%s' from local file '%s' failed: %s"%(bucket,host,path,infile,response.message))
    #sys.exit(1)
    
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
    conn = S3Connection(accesskey,secretkey)
    
    k = Key(bucket)
    k.key = path
    k.get_contents_to_filename(outfile)
    
    eprint("OK")
    sys.exit(0)
        
    #report error
    #eprint("copy from s3 bucket '%s' on host '%s' key '%s' to local file '%s' failed: %s"%(bucket,host,path,outfile,response.message))
    #sys.exit(1)
        
            
          
