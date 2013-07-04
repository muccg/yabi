import sys
import os
from tests.support import conf
from yabiadmin.yabi import models

'''
Module providing helper methods for creating data in yabi admin from tests
'''

def create_tool(name, display_name=None, path=None, ex_backend_name='Local Execution', fs_backend_name='Yabi Data Local Filesystem'):
    sys.stderr.write('Creating {0} tool\n'.format(name))
    if display_name is None: display_name = name
    if path is None: path = name
    lfs = models.Backend.objects.get(name=fs_backend_name)
    lex = models.Backend.objects.get(name=ex_backend_name)
    models.Tool.objects.create(name=name, display_name=display_name, path=path, backend=lex, fs_backend=lfs)

def add_tool_to_all_tools(toolname): 
    sys.stderr.write('Adding tool {0} to all tools\n'.format(toolname))
    tool = models.Tool.objects.get(name=toolname)
    tg = models.ToolGroup.objects.get(name='select data')
    alltools = models.ToolSet.objects.get(name='alltools')
    tg.toolgrouping_set.create(tool=tool, tool_set=alltools)

def remove_tool_from_all_tools(toolname):
    sys.stderr.write('Removing tool {0} from all tools\n'.format(toolname))
    models.ToolGrouping.objects.filter(tool__name=toolname, tool_set__name='alltools', tool_group__name='select data').delete()

def create_exploding_backend():
    sys.stderr.write('Creating exploding backend\n')
    exploding_backend = models.Backend.objects.create(name='Exploding Backend', scheme='explode', hostname='localhost.localdomain', path='/', submission='${command}\n')
    null_credential = models.Credential.objects.get(description='null credential')
    models.BackendCredential.objects.create(backend=exploding_backend, credential=null_credential, homedir='')

def create_torque_backend():
    sys.stderr.write('Creating torque backend\n')
    torque_backend = models.Backend.objects.create(
        name='Torque Backend', 
        scheme='torque', 
        hostname='localhost.localdomain', 
        path='/', 
        submission='${command}\n'
    )
    cred = models.Credential.objects.create( 
        description='Test TORQUE Credential', 
        username='ccg-user',
        password='password',
        cert='cert',
        key='key',
        user=models.User.objects.get(name='demo')
    )
    models.BackendCredential.objects.create(backend=torque_backend, credential=cred, homedir='')

def create_sshtorque_backend():
    sys.stderr.write('Creating ssh+torque backend\n')
    sshtorque_backend = models.Backend.objects.create(
        name='SSHTorque Backend', 
        scheme='ssh+torque', 
        hostname='localhost.localdomain', 
        path='/', 
        submission='${command}\n'
    )
    cred = models.Credential.objects.create( 
        description='Test SSHTorque Credential', 
        username=os.environ.get('USER'),
        password='',
        cert='cert',
        key=private_key,
        user=models.User.objects.get(name='demo')
    )
    models.BackendCredential.objects.create(backend=sshtorque_backend, credential=cred, homedir='')

def create_sshpbspro_backend():
    sys.stderr.write('Creating ssh+pbspro backend\n')
    sshpbspro_backend = models.Backend.objects.create(
        name='SSHPBSPro Backend', 
        scheme='ssh+pbspro', 
        hostname='localhost.localdomain', 
        path='/', 
        submission='${command}\n'
    )
    cred = models.Credential.objects.create( 
        description='Test SSHPBSPro Credential', 
        username=os.environ.get('USER'),
        password='',
        cert='cert',
        key=private_key,
        user=models.User.objects.get(name='demo')
    )
    models.BackendCredential.objects.create(backend=sshpbspro_backend, credential=cred, homedir='')

def create_ssh_backend():
    sys.stderr.write('Creating ssh backend\n')
    ssh_backend = models.Backend.objects.create(
        name='SSH Backend', 
        scheme='ssh', 
        hostname='localhost', 
        path='/', 
        submission='${command}'
    )
    cred = models.Credential.objects.create( 
        description='Test SSH Credential', 
        username=os.environ.get('USER'),
        password='',
        cert='cert',
        key=private_key,
        user=models.User.objects.get(name='demo')
    )
    models.BackendCredential.objects.create(backend=ssh_backend, credential=cred, homedir='')

def create_sftp_backend():
    sys.stderr.write('Creating sftp backend\n')
    sftp_backend = models.Backend.objects.create(
        name='SFTP Backend', 
        scheme='sftp', 
        hostname='localhost', 
        path='/', 
        submission='${command}'
    )
    cred = models.Credential.objects.create( 
        description='Test SFTP Credential', 
        username=os.environ.get('USER'),
        password='',
        cert='cert',
        key=private_key,
        user=models.User.objects.get(name='demo')
    )
    models.BackendCredential.objects.create(
        backend=sftp_backend, 
        credential=cred, 
        homedir=os.path.expanduser("~")[1:] + '/',
        visible = True,
    )


def create_backend(scheme="ssh", hostname="localhost.localdomain",path="/",submission="${command}"):
    sys.stderr.write('Creating {0} backend\n'.format(scheme))
    backend = models.Backend.objects.create(name='Test %s Backend'%scheme.upper(), scheme=scheme, hostname=hostname, path=path, submission=submission)
    # continue this...
    
def create_localfs_backend(scheme="localfs", hostname="localhost.localdomain", path="/tmp/yabi-localfs-test/"):
    backend = models.Backend.objects.create(
        name='Test %s Backend'%scheme.upper(),
        description="Test %s Backend"%scheme.upper(),
        scheme=scheme, 
        hostname=hostname,
        port=None,
        path=path, 
        submission=""
    )
    cred = models.Credential.objects.create( 
        description='Test %s Credential'%scheme.upper(), 
        username='username',
        password='password',
        cert='cert',
        key='key',
        user=models.User.objects.get(name="demo")
    )
    
    #join them
    backend_cred = models.BackendCredential.objects.create(
        backend = backend,
        credential = cred,
        homedir = "",
        visible = True,
        default_stageout = False,
        submission = ""
    )
    import os
    try:
        os.mkdir("/tmp/yabi-localfs-test/")
    except OSError, ose:
        if ose.errno != 17:
            raise
        #directory already exists... leave it
    
def destroy_localfs_backend(scheme="localfs", hostname="localhost.localdomain", path="/tmp/yabi-localfs-test/"):
    backend = models.Backend.objects.filter(
        name='Test %s Backend'%scheme.upper(),
        description="Test %s Backend"%scheme.upper(),
        scheme=scheme, 
        hostname=hostname,
        port=None,
        path=path, 
        submission=""
    ).delete()
    cred = models.Credential.objects.filter( 
        description='Test %s Credential'%scheme.upper(), 
        username='username',
        password='password',
        cert='cert',
        key='key',
        user=models.User.objects.get(name="demo")
    ).delete()
    
    #join them
    backend_cred = models.BackendCredential.objects.filter(
        backend = backend,
        credential = cred,
        homedir = "",
        visible = True,
        default_stageout = False,
        submission = ""
    ).delete()
    
    import shutil
    
    try:
        shutil.rmtree("/tmp/yabi-localfs-test/")    
    except OSError, ose:
        pass

def create_fakes3_backend(scheme="s3", hostname="localhost.localdomain", path="/" ):
    backend = models.Backend.objects.create(
        name='Test %s Backend'%scheme.upper(),
        description="Test %s Backend"%scheme.upper(),
        scheme=scheme, 
        hostname=hostname,
        port=conf.s3_port,
        path=path, 
        submission=""
    )
    cred = models.Credential.objects.create( 
        description='Test %s Credential'%scheme.upper(), 
        username='username',
        password='password',
        cert='cert',
        key='key',
        user=models.User.objects.get(name="demo")
    )
    
    #join them
    backend_cred = models.BackendCredential.objects.create(
        backend = backend,
        credential = cred,
        homedir = "",
        visible = True,
        default_stageout = False,
        submission = ""
    )
        

def create_tool_cksum():
    create_tool('cksum')
    add_tool_to_all_tools('cksum')
    tool = models.Tool.objects.get(name='cksum')
    tool.accepts_input = True
    star_extension = models.FileExtension.objects.get(pattern='*')
    models.ToolOutputExtension.objects.create(tool=tool, file_extension=star_extension)

    value_only = models.ParameterSwitchUse.objects.get(display_text='valueOnly')

    tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=value_only, mandatory=True, rank=99, file_assignment = 'all', switch='files')
    all_files = models.FileType.objects.get(name='all files')
    tool_param.accepted_filetypes.add(all_files)

    tool.save()

def create_tool_dd():
    create_tool('dd')
    add_tool_to_all_tools('dd')
    tool = models.Tool.objects.get(name='dd')
    tool.accepts_input = True
    star_extension = models.FileExtension.objects.get(pattern='*')
    models.ToolOutputExtension.objects.create(tool=tool, file_extension=star_extension)

    combined_eq = models.ParameterSwitchUse.objects.get(display_text='combined with equals')

    if_tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=combined_eq, mandatory=True, rank=1, file_assignment = 'batch', switch='if')
    all_files = models.FileType.objects.get(name='all files')
    if_tool_param.accepted_filetypes.add(all_files)

    of_tool_param = models.ToolParameter.objects.create(tool=tool, switch_use=combined_eq, mandatory=True, rank=2, file_assignment = 'none', switch='of', output_file=True)

    tool.save()

def create_tool_sleep():
    create_tool('sleep')
    tool = models.Tool.objects.get(name='sleep')
    tool.accepts_input = False
    valueOnly = models.ParameterSwitchUse.objects.get(display_text='valueOnly')
    tool.save()

    models.ToolParameter.objects.create(tool=tool, switch_use=valueOnly, mandatory=True, rank=1, file_assignment = 'none', switch='seconds', default_value='1')

    add_tool_to_all_tools('sleep')



def create_ssh_exec_backend(scheme="ssh", hostname="localhost.localdomain", path="/", submission=None, port=None):
    sys.stderr.write('Creating {0} backend\n'.format(scheme))
    
    if submission == None:
        submission = """#!/bin/bash
cd ${working}
${command} 1>${stdout} 2>${stderr}
"""
    
    backend = models.Backend.objects.create(
        name='Test %s Backend'%scheme.upper(),
        description="Test %s Backend"%scheme.upper(),
        scheme=scheme, 
        hostname=hostname,
        port=port,
        path=path, 
        submission=submission
    )
    cred = models.Credential.objects.create( 
        description='Test %s Credential'%scheme.upper(), 
        username='user',
        password='pass',
        cert='',
        key='',
        user=models.User.objects.get(name="demo")
    )
    
    #join them
    backend_cred = models.BackendCredential.objects.create(
        backend = backend,
        credential = cred,
        homedir = path,
        visible = True,
        default_stageout = False,
        submission = ""
    )
    #import os
    #try:
        #os.mkdir(path)
    #except OSError, ose:
        #if ose.errno != 17:
            #raise
        #directory already exists... leave it
        
    create_tool("hostname","hostname","/bin/hostname",backend_name='Test %s Backend'%scheme.upper(), fs_backend_name='Local Filesystem')
    add_tool_to_all_tools('hostname')

    tool = models.Tool.objects.get(name='hostname')
    tool.accepts_input = False
    tool.save()
    
def destroy_ssh_exec_backend(scheme="ssh", hostname="localhost.localdomain", path="/", port=None):
    sys.stderr.write('Destroying {0} backend\n'.format(scheme))
    models.BackendCredential.objects.filter(
        backend__description = 'Test %s Backend'%scheme.upper(),
        credential__description = 'Test %s Credential'%scheme.upper(),
        homedir = path,
        visible = True,
        default_stageout = False
    ).delete()
    models.Backend.objects.filter(
        name='Test %s Backend'%scheme.upper(),
        description="Test %s Backend"%scheme.upper(),
        scheme=scheme, 
        hostname=hostname,
        port=port,
        path=path
    ).delete()
    models.Credential.objects.filter( 
        description='Test %s Credential'%scheme.upper(), 
        username='user',
        password='pass',
        cert='',
        key='',
        user=models.User.objects.get(name="demo")
    ).delete()
    
    #import shutil
    #shutil.rmtree(path)    

def modify_backend(scheme="localex",hostname="localhost",**kwargs):
    """Apply kwargs to modify the matching backend"""
    backend = models.Backend.objects.get(scheme=scheme,hostname=hostname)
    for key,arg in kwargs.iteritems():
        setattr(backend,key,arg)
    backend.save()
    

private_key = \
"""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAuqrtex+43HRsh2gFZpcdkgJlLG7DyZyhbLLVZsKXPD3E4+a/
YWSj/2iRL/95sYc0X4bCXrFkonVsSdOBawaNNDpx6V8zGgBCkpKtTn1OzgUb4BvZ
b67/pMNsSYrwshvbjZ6xFhR8lt4LUThzl/FiBYItDzR3OhJ5SwWnG3LrFu8YZF/S
oWl9iLS/YBOG1mBphG5ySr7SdNyImg5hzGzF5Q1b+EYSBDJPySgcL1I07GGcegbs
exZftUD64Sjexlizzk+lV/2bmuT9SDPu7tUUhl0Pn6PhmSm+bkOuVwidQ96wLx2Y
B9hJxvStS4bzxBWGZjIzb8/zlYEEq4gbHVhE0QIDAQABAoIBAGkXzIYSMQCk52lA
jjHZCEPo508huUbr0RIiiPTGv2CiIhRxF/RcNdyY4YzVV400Yq8ZbprjYpX4aBQU
aPt5f8wUz4clGt8boF9nBv12nQRuaeg9pag0LSd1AqVQ/Pw5pN1Rp7+XnyFNN6/t
iV7U/mu9g2LZFfry5ajwMMnKZELPOQtM5nCQn2ddUNbuOw8fT0yjazKt7gNbCnIN
PLUVvUlusx1pwNOlONOsjXG4+rJO4j1Juy+pZl5UBkA4lAqbL12SIdv2x8zUALeQ
bYt+UXyh5jolRkkKbKUjPMs34Wyih0OLScprTxRgt0klHny5eg8FUWnPLYxMngZO
ML3b40ECgYEA6ZKBWMHu6DcIwUpgmBf2/e5FnMsmWyVptmnlHEgy2GvCFArdvi3I
qeSHOXuv5n9LDDaiQ56Ugw1CMRd85EzU5GMvd9chSZotqY4GCOm2Qbow8zeKsRII
dyC5xd7EVLSgPy551yukv4yWgjj18EV7XxJJ6w9wvJ1Pw230+HUykbkCgYEAzJdz
EvKu9dDp/4Mn8is4t8aRy/Upva0JuNlb8zhKiQHKPzD8oWzP+9LmDU625y7nVo6I
00kylBrh+83GAkPYmHu0YeLoRQRjR8vnzQBTuHz0sHfdksHWHms9+f4bhhdWcsrE
c3A94aNWeeDBCutmnjCsIdVsOnaLHdlg02+MN9kCgYEAyB/W442GfUBqJ/LqQGaI
IZn92xHUk1PC96BTxZ+2sOfjKfkFdOUVgTtlAUOQuxVl39kPvpAo/wBlLlrJj3Kl
FepFyZBx3PZVGWmukgRtPHOjbUCxfHXO+wL3KSptXYZFptzTWCD0z4pNitXzIyLl
SdgJrXVVSsYeiXu04QzJf0ECgYEAhUvrap35RikePB5syUhFxN64ISWTU4RJAEmF
shqr3UXwSmmVP2tQuua2glcVrdwOV4O4O8jGDl7Re6ie6NzhYr++T8Rxxn3MXXvJ
g/RBl8K5/buq/jISWnFOyPE5Z40PAu1/PyMS/k7YScIYpA+pJUna7JRL1m9jxkfZ
4QgdWEkCgYAQ5sNGuu+lOFW9h7icRUhJ0BbeVb61if8LBMpS8vfE+RrPaIElPByu
2j2kx2wmXeVyLRzSuYRZa21ZqkQbKU8NRjccp1OxNNovP/QUm0hJBBrLXOzUqHob
MtlxESvkl9Uthp61ciuoIDO5yfVyd++Mr+ssM/2J0ddbJiU3zhVIhw==
-----END RSA PRIVATE KEY-----"""
    
