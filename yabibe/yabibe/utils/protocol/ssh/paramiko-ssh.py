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
import os, sys, select, stat, time, json, uuid, urlparse
import requests
import binascii
import base64
import hmac
   
# read() blocksize
BLOCK_SIZE = 512

KNOWN_HOSTS_FILE = "~/.ssh/known_hosts"

CHECK_KNOWN_HOSTS = True

#disable any SSH agent that was lingering on the terminal when this is run
if 'SSH_AUTH_SOCK' in os.environ:
    del os.environ['SSH_AUTH_SOCK']
    
# get the yabiadmin url to connect to if its present
yabiadmin = os.environ.get('YABIADMIN',None)

# get the setting that tells us to check the ssl cert chain or to ignore it
SSL_CERT_CHECK = os.environ.get("SSL_CERT_CHECK","true").lower() == "true"

assert 'HMAC' in os.environ
hmac_key = os.environ['HMAC']

def main():
    options, arguments = parse_args()
    sanity_check(options)
    
    # load our known hosts
    if yabiadmin:
        known_hosts = load_known_hosts_from_admin(options.hostname)
    else:
        known_hosts = load_known_hosts(os.path.expanduser(KNOWN_HOSTS_FILE))

    # pre copy local to remote
    precopy(options, known_hosts)
    
    # make sure both script and exec is not set simultaneously
    if options.script is not None and options.execute is not None:
        sys.stderr.write("-x (--exec) and -s (--script) set simultaneously. Must choose one or the other.\n")
        sys.exit(3)

    # if we are running a script... copy it...
    if options.script:
        remote_script_path=precopy_script(options, known_hosts)

    # execute our remote command joining pipes with present shell
    # connect and authenticate
    exit_status = 0
    if options.listfolder:
        ssh = transport_connect_login(options, known_hosts)
        output = list_folder(ssh, options)
        print json.dumps(output)
    elif options.listfolderrecurse:
        ssh = transport_connect_login(options, known_hosts)
        output = list_folder_recurse(ssh, options)
        print json.dumps(output)
    else:
        ssh = ssh_connect_login(options, known_hosts)
        if options.execute:
            exit_status = execute(ssh, options)
        elif options.script:
            exit_status = execute(ssh, options, ex="bash -c \"%s\""%(remote_script))
            remote_unlink(options, known_hosts, remote_script)
    ssh.close()
    
    # post copy remote to local
    postcopy(options, known_hosts)

    if exit_status:
        sys.exit(exit_status)

def load_known_hosts(filename):
    """Load the known hosts file into the paramiko object"""
    return paramiko.hostkeys.HostKeys(filename)
    
def make_known_hosts(keylist):
    """Make a known hosts paramiko object from an array of hashes describing the known host keys"""
    hosts = paramiko.hostkeys.HostKeys()
    for key in keylist:
        hostname = key['hostname']
        key_type = key['key_type']
        hosts.add(hostname, key_type, {'ssh-rsa':paramiko.rsakey.RSAKey, 'ssh-dss':paramiko.dsskey.DSSKey}[key_type](data=base64.decodestring(key['data'])))
    return hosts

def sign_uri(uri):
    hmac_digest = hmac.new(hmac_key)
    hmac_digest.update( make_path(uri) )
    return hmac_digest.hexdigest()

def make_path(uri):
    parse = urlparse.urlparse(uri)
    if parse.query:
        return parse.path + "?" + parse.query
    else:
        return parse.path

def load_known_hosts_from_admin(hostname):
    """Contact yabiadmin and get the known hosts from it"""
    assert yabiadmin
    path = "ws/hostkeys?hostname=%s"%hostname
    url = yabiadmin + path
    r = requests.get( url, headers={'Hmac-digest':sign_uri( url )}, verify=SSL_CERT_CHECK )
    
    assert r.status_code == 200
    
    keys = json.loads(r.text)
    return make_known_hosts(keys)
    
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def add_rejected_key_to_admin(hostname, hostkey):
    """send the rejected key to yabiadmin"""
    assert yabiadmin
    url = yabiadmin + "ws/hostkey/deny"
    r = requests.post( url,
        data = {
            'hostname': hostname,
            'key': hostkey.get_base64(),
            'key_type': hostkey.get_name(),
            'fingerprint':':'.join(
                (lambda l,n:[l[i:i+n] for i in range(0, len(l), n)])
                (binascii.hexlify(hostkey.get_fingerprint()),2)
            )             # encodes fingerprint into colon seperated hex style of 'ae:52:f4:54:0a:4b:f0:11:ae:52:f4:54:0a:4b:f0:11'
        },
        headers = {
            'Hmac-digest':sign_uri( url )
        },
        verify=SSL_CERT_CHECK
    )
    
    if r.status_code==400:
        raise Exception("Incorrect HMAC")
    
    assert r.status_code==200
    
def parse_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option( "-i", "--identity", dest="identity", help="Login using only this RSA keyfile" )
    parser.add_option( "-p", "--password", dest="password", help="Login using only this password. If -i is also specified, login using only the RSA key but use this as the passphrase" )
    parser.add_option( "-u", "--username", dest="username", help="Login as this remote user")
    parser.add_option( "-H", "--hostname", dest="hostname", help="Login to this hostname")
    parser.add_option( "-x", "--exec", dest="execute", help="Execute this remote command", default=None)
    parser.add_option( "-s", "--script", dest="script", help="Execute this local script file on the remote machine", default=None)
    parser.add_option( "-l", "--prelocal", dest="prelocal", help="Pre-copy prelocal to preremote")
    parser.add_option( "-r", "--preremote", dest="preremote", help="Pre-copy prelocal to preremote")
    parser.add_option( "-L", "--postlocal", dest="postlocal", help="Post-copy postremote to postlocal")
    parser.add_option( "-R", "--postremote", dest="postremote", help="Post-copy postremote to postlocal")
    parser.add_option( "-f", "--list-folder", dest="listfolder", help="Do an ssh list operation on the specified folder")
    parser.add_option( "-F", "--list-folder-recurse", dest="listfolderrecurse", help="Do a recursive list operation on the specified folder")
    parser.add_option( "-O", "--stdout", dest="stdout", help="redirect the --exec option output to local file specified here")
    parser.add_option( "-I", "--stdin", dest="stdin", help="feed this file into stdin of the --exec option instead of reading from stdin")
    parser.add_option( "-N", "--no-stdin", dest="nostdin", help="ignore stdin completely", action="store_true", default=False)
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
    ssh = paramiko.SSHClient()
    if CHECK_KNOWN_HOSTS:
        ssh._system_host_keys = known_hosts
        
        class ReportMissingKeyToAdminPolicy(paramiko.MissingHostKeyPolicy):
            def missing_host_key(self, client, hostname, key):
                add_rejected_key_to_admin(hostname, key)
                raise paramiko.SSHException("Remote host key is denied. Please verify fingerprint and mark as allowed in admin to allow a connection to the host.")
            
        ssh.set_missing_host_key_policy(ReportMissingKeyToAdminPolicy())
    else:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    if options.identity:
        try:
            mykey = get_rsa_key(options)
        except paramiko.SSHException, pe:
            mykey = get_dsa_key(options)
        
        try:
            ssh.connect(options.hostname, username=options.username, pkey=mykey)
        except paramiko.BadHostKeyException, ex:
            if "Unknown server" in ex.message:
                # key failure
                #add_rejected_key_to_admin("null://localhost.localdomain/", ex.key)
                raise Exception("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
            raise ex
        return ssh
               
    elif options.password:
        try:
            ssh.connect(options.hostname, username=options.username, password=options.password)
        except paramiko.SSHException, ex:
            if "Unknown server" in ex.message:
                # key failure
                #add_rejected_key_to_admin("null://localhost.localdomain/", ex.key)
                raise Exception("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
            raise ex
        return ssh
        
    raise Exception("Unknown login method. Both identity and password are unset")

def transport_connect_login(options, known_hosts):
    ssh = paramiko.Transport((options.hostname, 22))
    
    if options.identity:    
        try:
            mykey = get_rsa_key(options)
        except paramiko.SSHException, pe:
            mykey = get_dsa_key(options)
        
        ssh.connect(username=options.username, pkey=mykey)
        
        if CHECK_KNOWN_HOSTS:
            remote_key = ssh.get_remote_server_key()
            known = known_hosts.check(options.hostname,  remote_key)
            
            if not known:
                add_rejected_key_to_admin(options.hostname, remote_key)
                if yabiadmin:
                    raise paramiko.SSHException("Remote host key is denied. Please verify fingerprint and mark as allowed in admin to allow a connection to the host.")
                else:
                    raise paramiko.SSHException("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
        
        return ssh
               
    elif options.password:
        # establish connection
        ssh.connect(username=options.username, password=options.password)
        
        if CHECK_KNOWN_HOSTS:
            remote_key = ssh.get_remote_server_key()
            known = known_hosts.check(options.hostname,  remote_key)
            
            if not known:
                add_rejected_key_to_admin(options.hostname, remote_key)
                if yabiadmin:
                    raise paramiko.SSHException("Remote host key is denied. Please verify fingerprint and mark as allowed in admin to allow a connection to the host.")
                else:
                    raise paramiko.SSHException("Trying to connect to unknown host. Remote host key not found in %s"%(KNOWN_HOSTS_FILE))
           
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
        
def precopy_script(options, known_hosts):
    # copy the named script file to a temporary place on the remote filesystem
    remotepath = "/tmp/"+uuid.uuid4()+".sh"
    setproctitle.setproctitle("yabi-ssh %s@%s copy local script %s to remote path %s"%(options.username,options.hostname,options.script,remotepath))
    transport = transport_connect_login(options, known_hosts)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(options.script,options.remotepath,confirm=False)
    sftp.close()
    transport.close()
    return remotepath

def remote_unlink(options,remote):
    transport = transport_connect_login(options, known_hosts)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.unlink(remote)
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

def execute(ssh,options,shell=True, ex=None):
    if options.execute:
        setproctitle.setproctitle("yabi-ssh %s@%s exec %s"%(options.username, options.hostname, options.execute))
        
        execute = ex or options.execute
        
        if options.stdout:
            stdout_channel = open(options.stdout,'wb')
        else:
            stdout_channel = sys.stdout
            
        if options.stdin:
            stdin_channel = open(options.stdin,'rb')
        elif not options.nostdin:
            stdin_channel = sys.stdin
        
        if shell:
            ex = execute.replace("'","'\\''")        # escape any single quotes
            stdin, stdout, stderr = ssh.exec_command("bash -c '"+ex+"'")
        else:
            stdin, stdout, stderr = ssh.exec_command(execute)
    
        readlist = [stdout.channel]
        if not options.nostdin:
            readlist.append(stdin_channel)
        while not stdout.channel.exit_status_ready():
            rlist,wlist,elist = select.select(readlist,[stdin.channel],[stdin_channel,stdin.channel,stdout.channel])
            #print "r",rlist,"w",len(wlist),"e",len(elist)
            if not options.nostdin and stdin_channel in rlist:
                # read stdin and pipe to process
                input = stdin_channel.readline()
                if not input:
                    readlist.remove(stdin_channel)
                    stdin.channel.shutdown(2)
                    stdin.close()
                else:
                    stdin.write( input )
                    stdin.flush()
                    # stdin.close()?
                    
            if stdout.channel in rlist:
                stdout_channel.write( stdout.read(BLOCK_SIZE) )
            if len(elist):
                sys.stderr.write("error! ")
                sys.stderr.write(repr(elist))
                sys.stderr.write("\n")
                
        # exhaust stdout/stderr
        stdout_channel.write( stdout.read() )
                
        if options.stdout:
            stdout_channel.close()
            
        if options.stdin:
            stdin_channel.close()
                
        return stdout.channel.exit_status

try:
    main()
except Exception, e:
    # all exceptions mean a problem with the SSH code or the paramiko
    # we print the error and exit 255
    import traceback
    traceback.print_exc()
    sys.exit(255)
