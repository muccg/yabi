#!/usr/bin/env python
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

import setproctitle        
setproctitle.setproctitle("yabi-ssh startup...")

import paramiko
import os, sys, select

# read() blocksize
BLOCK_SIZE = 512

def main():
    options, arguments = parse_args()
    sanity_check(options)
    
    # pre copy local to remote
    precopy(options)

    # execute our remote command joining pipes with present shell
    # connect and authenticate
    ssh = ssh_connect_login(options)
    exit_status = execute(ssh, options)
    ssh.close()
    
    # post copy remote to local
    postcopy(options)

    if exit_status:
        sys.exit(exit_status)

def parse_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option( "-i", "--identity", dest="identity", help="Login using only this RSA keyfile" )
    parser.add_option( "-p", "--password", dest="password", help="Login using only this password. If -i is also specified, login using only the RSA key but use this as the passphrase" )
    parser.add_option( "-u", "--username", dest="username", help="Login as this remote user")
    parser.add_option( "-H", "--hostname", dest="hostname", help="Login to this hostname")
    parser.add_option( "-x", "--exec", dest="execute", help="Execute this remote command")
    parser.add_option( "-l", "--prelocal", dest="prelocal", help="Pre-copy prelocal to preremote")
    parser.add_option( "-r", "--preremote", dest="preremote", help="Pre-copy prelocal to preremote")
    parser.add_option( "-L", "--postlocal", dest="postlocal", help="Post-copy postremote to postlocal")
    parser.add_option( "-R", "--postremote", dest="postremote", help="Post-copy postremote to postlocal")

    return parser.parse_args()

def sanity_check(options):
    if not options.hostname:
        sys.stderr.write("Error: No hostname provided\n")
        sys.exit(128)
        
    if not options.username:
        sys.stderr.write("Error: No username provided\n")
        sys.exit(129)
    
def get_rsa_key(options):
    privatekeyfile = os.path.expanduser(options.identity)
    return paramiko.RSAKey.from_private_key_file(privatekeyfile, password=options.password)

def get_dsa_key(options):
    privatekeyfile = os.path.expanduser(options.identity)
    return paramiko.DSSKey.from_private_key_file(privatekeyfile, password=options.password)

def ssh_connect_login(options):
    if options.identity:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            mykey = get_rsa_key(options)
        except paramiko.SSHException, pe:
            mykey = get_dsa_key(options)
        
        ssh.connect(options.hostname, username=options.username, pkey=mykey)
        return ssh
               
    elif options.password:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(options.hostname, username=options.username, password=options.password)
        return ssh
        
    raise Exception("Unknown login method. Both identity and password are unset")

def transport_connect_login(options):
    if options.identity:
        ssh = paramiko.Transport((options.hostname, 22))
        #ssh.load_system_host_keys()
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            mykey = get_rsa_key(options)
        except paramiko.SSHException, pe:
            mykey = get_dsa_key(options)
        
        ssh.connect(username=options.username, pkey=mykey)
        return ssh
               
    elif options.password:
        ssh = paramiko.Transport((options.hostname, 22))
        #ssh.load_system_host_keys()
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(username=options.username, password=options.password)
        return ssh
        
    raise Exception("Unknown login method. Both identity and password are unset")

def precopy(options):
    if options.preremote and options.prelocal:
        setproctitle.setproctitle("yabi-ssh %s@%s copy local %s to remote %s"%(options.username, options.hostname, options.prelocal, options.preremote))
        transport = transport_connect_login(options)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(options.prelocal,options.preremote,confirm=False)
        sftp.close()
        transport.close()

def postcopy(options):
    if options.postremote and options.postlocal:
        setproctitle.setproctitle("yabi-ssh %s@%s copy remote %s to local %s"%(options.username, options.hostname, options.postremote, options.postlocal))
        transport = transport_connect_login(options) 
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(options.postremote,options.postlocal,confirm=False)
        sftp.close()
        transport.close()

def execute(ssh,options):       
    if options.execute:
        setproctitle.setproctitle("yabi-ssh %s@%s exec %s"%(options.username, options.hostname, options.execute))
        stdin, stdout, stderr = ssh.exec_command(options.execute)
    
        readlist = [sys.stdin,stdout.channel,stderr.channel]
        while not stdout.channel.exit_status_ready():
            rlist,wlist,elist = select.select(readlist,[stdin.channel],[sys.stdin,stdin.channel,stdout.channel,stderr.channel])
            #print "r",rlist,"w",len(wlist),"e",len(elist)
            if sys.stdin in rlist:
                # read stdin and pipe to process
                input = sys.stdin.readline()
                if not input:
                    readlist.remove(sys.stdin)
                    stdin.channel.shutdown(2)
                    stdin.close()
                else:
                    stdin.write( input )
                    stdin.flush()
                    # stdin.close()?
                    
            if stdout.channel in rlist:
                sys.stdout.write( stdout.read(512) )
            if stderr.channel in rlist:
                sys.stderr.write( stderr.read(512) )
            
            if len(elist):
                sys.stderr.write("error! ")
                sys.stderr.write(repr(elist))
                sys.stderr.write("\n")
                
        # exhaust stdout and stderr
        sys.stderr.write( stderr.read() )
        sys.stdout.write( stdout.read() )
                
        return stdout.channel.exit_status


main()