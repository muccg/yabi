#!/usr/bin/env python

#
# configure ssh+qsub backend
#

import django
import settings

def print_settings():
    db = settings.DATABASES['default']
    print "Using settings %s: %s"%(db['ENGINE'],db['NAME']) + ("@%s"%(db['HOST']) if db['HOST'] else "")
    
from yabi.models import Backend, Credential, BackendCredential
from yabi.models import User
from django.contrib.auth.models import User as DjangoUser

def make_be_title(string,variable):
    """tries to make a nice backend name without clobbering existing names"""
    be = Backend.objects.filter(**{'%s__contains'%variable:string})
    be_set = [b for b in be if getattr(b,variable).startswith(string)]
    if not be_set:
        # empty set. Unique name
        return string
    return string+" (%d)"%(len(be_set))

def make_be_name(template):
    """make a name"""
    return make_be_title(template,'name')

def make_be_desc(template):
    """make a description"""
    return make_be_title(template,'description')

def add_yabi_backend(name,desc,scheme,host,port,path,script):
    be=Backend()
    be.name = name
    be.description = desc
    be.scheme = scheme
    be.hostname = host
    be.port = port
    be.path = path
    be.submission = script
    be.save()
    return be
    
def add_sshqsub_backend(host,path=None,port=None,name=None,description=None):
    name = name or make_be_name("ssh+qsub@%s"%(host))
    port = port or 22
    path = path or '/'
    script = """#!/bin/sh
% for module in modules:
    module load ${module}
% endfor
cd '${working}'
${command}
"""
    description = description or make_be_desc("ssh+qsub host @ %s on port %d path %s"%(host,port,path))
    return add_yabi_backend(name,description,"ssh+qsub", host, port, path, script)
   
def add_backend():
    print "URI?",
    uri = raw_input()
    
    from urlparse import urlparse
    up = urlparse(uri)
    
    scheme = up.scheme
    netloc = up.netloc
    path = up.path
    
    if ':' not in netloc:
        hostname = netloc
        port = None
    else:
        hostname, port = netloc.spit(":")
        port = int(port)
        
    print "Backend name [return for default]?",
    name = raw_input()
    if not name:
        name = make_be_name("%s@%s"%(scheme,hostname))
    
    print "Description [return for default]?",
    desc = raw_input()
    if not desc:
        desc = make_be_desc("Backend for uri %s"%(uri))
        
    add_yabi_backend(name,desc,scheme,hostname,port,path,"")

def make_cred_title(string,variable):
    """tries to make a nice backend name without clobbering existing names"""
    be = Credential.objects.filter(**{'%s__contains'%variable:string})
    be_set = [b for b in be if getattr(b,variable).startswith(string)]
    if not be_set:
        # empty set. Unique name
        return string
    return string+" (%d)"%(len(be_set))
   
def add_yabi_credential(desc,username="",password="",cert="",key="",yabiuser=None):
    cred = Credential()
    desc = desc or "Credential %s for yabi user %s"%(username,yabiuser)
    cred.description = make_cred_title(desc,"description")
    cred.username = username
    cred.password = password
    cred.cert = cert
    cred.key = key
    cred.user = User.objects.get(name=yabiuser)
    cred.save()
    return cred
    
def add_credential():
    print "Remote username?",
    username = raw_input()
    print "Password/Passphrase [return for no password]?",
    password = raw_input()
    print "Certificate [return for no cert. ctrl-d to end]?",
    cert = multi_input()
    print "Key [return for no key. ctrl-d to end]?",
    key = multi_input()
    print "Yabi username to own credential?",
    yabiuser = raw_input()
    print "Description [return for autogenerate]?",
    desc = raw_input()
    
    desc = desc or "Credential %s for yabi user %s"%(username,yabiuser)
    
    add_yabi_credential(desc,username,password,cert,key,yabiuser=User.objects.get(name=yabiuser))
    
def add_backendcredential():
    print "Credentials"
    print "==========="
    list_credentials()
    
    print "Enter credential id?",
    cid = int(raw_input())
    
    print
    print "Backends"
    print "========"
    list_backends()
    
    print "Enter backend id?",
    bid = int(raw_input())
    
    print
    print "Enter homedir path for BackendCredential?",
    homedir = raw_input()
    
    print "Stageout path?",
    stageout = raw_input()
    
    print "visible?",
    visible = raw_input()[0] in "yY"
    
    print "Enter a submission script [Press return for none]?",
    submission=multi_input()
    
    # create the BackendCredential now
    return add_yabi_backendcredential(Backend.objects.get(id=bid), Credential.objects.get(id=cid), homedir=homedir, visible=visible, default_stageout=stageout, submission=submission)
    

def add_yabi_backendcredential(backend, cred, homedir, visible, default_stageout, submission=""):
    bec = BackendCredential()
    bec.backend = backend
    bec.credential = cred
    bec.homedir = homedir
    bec.visible = visible
    bec.default_stageout = default_stageout
    bec.submission = submission
    bec.save()
    return bec

def test():
    print_settings()    
    be=add_sshqsub_backend("175.41.151.98")
    cred=add_yabi_credential(None,"root","","","","demo")
    bec=add_yabi_backendcredential(be,cred,"/",True,"/tmp")

def list_users():
    users = DjangoUser.objects.all()
    for u in users:
        if u.first_name and u.last_name:
            name = "%s %s"%(u.first_name, u.last_name)
        elif u.first_name:
            name=u.first_name
        elif u.last_name:
            name=u.last_name
        else:
            name=""
        print u.id,u, '"%s"'%(name) if name else "", u.email, "staff" if u.is_staff else "", "active" if u.is_active else "", "su" if u.is_superuser else "", "yabiuser" if User.objects.get(name=u.username) else ""




##
## listings
##

def list_credentials():
    creds = Credential.objects.all()
    for cred in creds:
        cred.unprotect()
        print cred.id,"%s:"%cred.user,'"%s"'%cred.description,"username:"+cred.username,"password:%s"%('*'*len(cred.password)) if cred.password else "", "cert" if cred.cert else "", "key" if cred.key else ""

def list_backends():
    backends = Backend.objects.all()
    for be in backends:
        print be.id,be.uri,'"%s" "%s"'%(be.name,be.description),"link" if be.link_supported else "", "lcopy" if be.lcopy_supported else ""

def list_backendcredentials():
    becreds = BackendCredential.objects.all()
    lines = []
    for bec in becreds:
        lines.append("%d [%s]<->[%s] %s %s %s"%(bec.id, bec.credential, bec.backend, bec.homedir, "visible" if bec.visible else "", "submission" if len(bec.submission) else ""))
    for line in lines:
        print line






##
## utils
##

def parse_ranges(st):
    """turns 4,8,11-13,21 into [4,8,11,12,13,21]"""
    parts = st.split(",")
    out = []
    for part in parts:
        if '-' in part:
            s,e = part.split('-')
            out.extend(range(int(s),int(e)+1))
        else:
            out.append(int(part))
        
    return out

def multi_input(ctrld=True, return_term=True):
    """reads multiple lines of input. it ctrld is true, Ctrl-D ends block (allows for blank lines to be entered)
    if its false, a blank line ends input
    
    If return_term is true, a blank single empty line FIRST entered exits
    
    """
    line = "x"
    output = ""
    crlf = "\r\n"
    
    if ctrld:
        try:
            if return_term:
                line = raw_input()
                if not line:
                    return ""
                output = line + crlf
            while True:
                line = raw_input()
                output += line + crlf
        except EOFError, eof:
            print
            return output
    else:
        if return_term:
            line = raw_input()
            if not line:
                return ""
            output = line + crlf
        while line:
            line = raw_input()
            output += line + crlf
        
    return output




##
## delete objects
##
def deleter(modelname, idstring):
    ids = parse_ranges(idstring)
    objs = locals()['modelname'].objects.filter(id__in=ids)
    s='z'
    while s not in 'yn':
        print "Are you sure you want to delete %d %s%s [y/n/?]?"%(len(objs),modelname,"s" if len(objs)>1 else ""),
        s = raw_input()
        if s.lower()=='y':
            objs.delete()
        elif s.lower()=='n':
            pass
        elif s=='?':
            for obj in objs:
                print obj

def delete_backends(beids):
    return deleter("Backend",beids)

def delete_credential(credids):
    return deleter("Credential",credids)
                
def delete_backendcredential(ids):
    return deleter("BackendCredential",ids)
            
            
            
            
            
            

import getopt, sys

def usage():
    print "usage:"
    print sys.argv[0]+" [-h] [--list-users] [--list-credentials]"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", [
            "help",
            "list-users","list-credentials","list-creds","list-backends", "list-backendcredentials",
            "delete-backend=","delete-credential=","delete-backendcredential=",
            "add-backend","add-credential","add-backendcredential"
        ])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        
        elif o in ("--list-users"):
            list_users()
        elif o in ("--list-creds","--list-credentials"):
            list_credentials()
        elif o in ("--list-backends"):
            list_backends()
        elif o in ("--list-backendcredentials"):
            list_backendcredentials()
            
        elif o in ("--delete-backend"):
            delete_backends(a)
        elif o in ("--delete-credential"):
            delete_credential(a)
        elif o in ("--delete-backendcredential"):
            delete_backendcredential(a)
            
        elif o in ("--add-backend"):
            add_backend()
        elif o in ("--add-credential"):
            add_credential()
        elif o in ("--add-backendcredential"):
            add_backendcredential()
        else:
            assert False, "unhandled option"
    # ...

if __name__ == "__main__":
    main()