# -*- coding: utf-8 -*-
"""All these funcs are done in a blocking manner using a stackless aproach. Not your normal funcs"""

from stackless import schedule, tasklet
from twisted.web import client
from twisted.internet import reactor
import time
import json
import os
from conf import config

COPY_RETRY = 3
COPY_PATH = "/fs/copy"
RCOPY_PATH = "/fs/rcopy"
LIST_PATH = "/fs/ls"
EXEC_PATH = "/exec/run"
MKDIR_PATH = "/fs/mkdir"
RM_PATH = "/fs/rm"

USER_AGENT = "YabiStackless/0.1"

from utils.stacklesstools import GET, POST, GETFailure, CloseConnections

def Sleep(seconds):
    """sleep tasklet for this many seconds. seconds is a float"""
    now = time.time()
    then = now+seconds
    while time.time()<then:
        schedule()

class CopyError(Exception): pass

def Copy(src,dst,retry=COPY_RETRY, **kwargs):
    """Copy src (url) to dst (url) using the fileservice"""
    print "Copying %s to %s"%(src,dst)
    for num in range(retry):
        #print "retry num=",num
        try:
            code,message,data = GET(COPY_PATH,src=src,dst=dst, **kwargs)
            print "code=",repr(code)
            if int(code)==200:
                # success!
                #print "SUCC"
                return True
            else:
                #print "FAIL"
                raise CopyError(data)
        except GETFailure, err:
            print "Post failed with error:",err
            Sleep(5.0)
    
    raise err
    
def RCopy(src, dst, **kwargs):
    #print "RCopying %s to %s"%(src,dst)
    try:
        POST(RCOPY_PATH,src=src,dst=dst, **kwargs)
        # success!
        return True
    except GETFailure, err:
        print "Copy failed with error:",err
        raise
    
def List(path,recurse=False, **kwargs):
    #print "LIST posting",LIST_PATH,path,recurse
    code, message, data = GET(LIST_PATH,uri=path,recurse=recurse, **kwargs)
    #print "RESPONSE",code,message,data
    assert code==200
    #print "LIST:",data
    return json.loads(data)

def Mkdir(path, **kwargs):
    return GET(MKDIR_PATH,uri=path, **kwargs)

def Rm(path, recurse=False, **kwargs):
    code, message, data = GET(RM_PATH,uri=path,recurse=recurse, **kwargs)
    assert code==200
    return data

def Log(logpath,message):
    """Report an error to the webservice"""
    #print "Reporting error to %s"%(logpath)
    #print "Logging to %s"%(logpath)
    print "log=",message
    
    if "://" in logpath:
        from urlparse import urlparse
        parsed = urlparse(logpath)
        #print "LOG:",parsed.path, message,parsed.hostname,parsed.port
        code,msg,data = POST(parsed.path, message=message,host=parsed.hostname,port=parsed.port)              # error exception should bubble up and be caught
    else:
        code,msg,data = POST(logpath, host=config.yabiadminserver,port=config.yabiadminport, message=message)              # error exception should bubble up and be caught
    assert code==200

    
def Status(statuspath, message):
    """Report some status to the webservice"""
    #print "Reporting status to %s"%(statuspath)
    print "status=",message
    
    if "://" in statuspath:
        from urlparse import urlparse
        parsed = urlparse(statuspath)
        
        code,msg,data = POST(parsed.path, status=message,host=parsed.hostname,port=parsed.port)              # error exception should bubble up and be caught
    else:
        code,msg,data = POST(statuspath, host=config.yabiadminserver,port=config.yabiadminport, status=message)              # error exception should bubble up and be caught
    assert code==200
    
def Exec(backend, command, callbackfunc=None, **kwargs):
    # setup the status callback
    #print "backend:",[backend]
    #print "command:",[command]
    #print "callbackfunc:",[callbackfunc]
    #print "kwargs:",kwargs
    
    kwargs['uri']=backend
    
    POST(EXEC_PATH, command=command, datacallback=callbackfunc, **kwargs )
    
def UserCreds(yabiusername, uri):
    """Get a users credentials"""
    # see if we can get the credentials
    #print "UserCreds",scheme,username,hostname
    url = os.path.join(config.yabiadminpath,'ws/credential/%s/'%(yabiusername))
    code, message, data = GET(url, host=config.yabiadminserver, port=config.yabiadminport)
    assert code==200
    print "JSON DATA:",data
    return json.loads(data)
