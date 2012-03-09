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
import os, sys, select, stat, time, json

# read() blocksize
BLOCK_SIZE = 512

KNOWN_HOSTS_FILE = "~/.ssh/known_hosts"

def main():
    options, arguments = parse_args()
    sanity_check(options)
    
    # load our known hosts
    known_hosts = load_known_hosts(os.path.expanduser(KNOWN_HOSTS_FILE))

    # pre copy local to remote
    precopy(options, known_hosts)

    # execute our remote command joining pipes with present shell
    # connect and authenticate
    if options.listfolder:
        ssh = transport_connect_login(options, known_hosts)
        output = list_folder(ssh, options)
        print json.dumps(output)
        exit_status = 0
    elif options.listfolderrecurse:
        ssh = transport_connect_login(options, known_hosts)
        output = list_folder_recurse(ssh, options)
        print json.dumps(output)
        exit_status = 0
    else:
        ssh = ssh_connect_login(options, known_hosts)
        exit_status = execute(ssh, options)
    ssh.close()
    
    # post copy remote to local
    postcopy(options, known_hosts)

    if exit_status:
        sys.exit(exit_status)

def load_known_hosts(filename):
    """Load the known hosts file into the paramiko object"""
    return paramiko.hostkeys.HostKeys(filename)

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
    parser.add_option( "-f", "--list-folder", dest="listfolder", help="Do an ssh list operation on the specified folder")
    parser.add_option( "-F", "--list-folder-recurse", dest="listfolderrecurse", help="Do a recursive list operation on the specified folder")
    #parser.add_option( "-Y", "--yes-add-host-key", dest="addhostkey", help="Add unknown host keys to known_hosts")
    
    return parser.parse_args()

def list_folder(ssh, options): 
    sftp = paramiko.SFTPClient.from_transport( ssh )
    return do_stat( sftp, options.listfolder ) or {options.listfolder:do_ls(sftp,options.listfolder)}
    
def do_ls(sftp, path):
    output = {"files":[],"directories":[]}
    for entry in sftp.listdir_attr(path):
        # if not a hidden directory
        if not entry.filename.startswith('.'):
            s = sftp.stat(os.path.join(path,entry.filename))            # stat the destination of any link
            if stat.S_ISDIR(s.st_mode):
                # directory
                output['directories'].append([entry.filename,entry.st_size,time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(entry.st_mtime)),stat.S_ISLNK(entry.st_mode)])
            else:
                # file or symlink to directory
                output['files'].append([entry.filename,entry.st_size,time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(entry.st_mtime)),stat.S_ISLNK(entry.st_mode)])
                
    
    # sort entries
    output['directories'].sort()
    output['files'].sort()
    
    return output
    
def list_folder_recurse(ssh, options):
    sftp = paramiko.SFTPClient.from_transport( ssh )
    return do_stat( sftp, options.listfolderrecurse ) or do_ls_r( sftp, options.listfolderrecurse, {} )

def do_ls_r(sftp,path,output):
    try:
        results = do_ls(sftp,path)
    except IOError, ioe:
        # permissions...
        return output
    output[path] = results
    
    for filename,size,date,link in results['directories']:
        do_ls_r(sftp, os.path.join(path,filename), output)
        
    return output
    
def do_stat(sftp,path):
    # is it a solo file?
    try:
        lresult = sftp.lstat(path)
    except IOError, ioe:
        sys.stderr.write("No such file or directory: %s\n"%path)
        sys.exit(2)
    result = sftp.stat(path)
    if stat.S_ISREG(result.st_mode):
        # regular file
        output = {
            'directories': [],
            'files':       [
                [path.rsplit('/',1)[-1],lresult.st_size, time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(lresult.st_mtime)),stat.S_ISLNK(lresult.st_mode)]
            ] }
            
        return {path:output}
    return None

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

def ssh_connect_login(options, known_hosts):
    if options.identity:
        ssh = paramiko.SSHClient()
        ssh._system_host_keys = known_hosts
        
        try:
            mykey = get_rsa_key(options)
        except paramiko.SSHException, pe:
            mykey = get_dsa_key(options)
        
        try:
            ssh.connect(options.hostname, username=options.username, pkey=mykey)
        except paramiko.SSHException, ex:
            if "Unknown server" in ex.message:
                # key failure
                raise Exception("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
            raise ex
        return ssh
               
    elif options.password:
        ssh = paramiko.SSHClient()
        ssh._system_host_keys = known_hosts
        
        try:
            ssh.connect(options.hostname, username=options.username, password=options.password)
        except paramiko.SSHException, ex:
            if "Unknown server" in ex.message:
                # key failure
                raise Exception("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
            raise ex
        return ssh
        
    raise Exception("Unknown login method. Both identity and password are unset")

def transport_connect_login(options, known_hosts):
    if options.identity:
        ssh = paramiko.Transport((options.hostname, 22))
                
        try:
            mykey = get_rsa_key(options)
        except paramiko.SSHException, pe:
            mykey = get_dsa_key(options)
        
        ssh.connect(username=options.username, pkey=mykey)
        
        # check remote host key with known_hosts...
        remote_key = ssh.get_remote_server_key()
        known = known_hosts.check(options.hostname,  remote_key)
        
        if not known:
            raise Exception("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
        
        return ssh
               
    elif options.password:
        ssh = paramiko.Transport((options.hostname, 22))
        
        # establish connection
        ssh.connect(username=options.username, password=options.password)
        
        # check remote host key with known_hosts...
        remote_key = ssh.get_remote_server_key()
        known = known_hosts.check(options.hostname,  remote_key)
        
        if not known:
            raise Exception("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
        
        return ssh
        
    raise Exception("Unknown login method. Both identity and password are unset")

def precopy(options, known_hosts):
    if options.preremote and options.prelocal:
        setproctitle.setproctitle("yabi-ssh %s@%s copy local %s to remote %s"%(options.username, options.hostname, options.prelocal, options.preremote))
        transport = transport_connect_login(options, known_hosts)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(options.prelocal,options.preremote,confirm=False)
        sftp.close()
        transport.close()

def postcopy(options, known_hosts):
    if options.postremote and options.postlocal:
        setproctitle.setproctitle("yabi-ssh %s@%s copy remote %s to local %s"%(options.username, options.hostname, options.postremote, options.postlocal))
        transport = transport_connect_login(options, known_hosts) 
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(options.postremote,options.postlocal,confirm=False)
        sftp.close()
        transport.close()

def execute(ssh,options,shell=True):
    if options.execute:
        setproctitle.setproctitle("yabi-ssh %s@%s exec %s"%(options.username, options.hostname, options.execute))
        
        if shell:
            ex = options.execute.replace("'","'\\''")        # escape any single quotes
            stdin, stdout, stderr = ssh.exec_command("bash -c '"+ex+"'")
        else:
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

try:
    main()
except Exception, e:
    # all exceptions mean a problem with the SSH code or the paramiko
    # we print the error and exit 255
    import traceback
    traceback.print_exc()
    sys.exit(255)