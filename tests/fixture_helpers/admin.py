from tests.support import conf

'''
Module providing helper methods for creating data in yabi admin from tests
'''

def create_tool(name, display_name=None, path=None, ex_backend_name='Local Execution', fs_backend_name='Yabi Data Local Filesystem'):
    from yabiadmin.yabi import models
    if display_name is None: display_name = name
    if path is None: path = name
    lfs = models.Backend.objects.get(name=fs_backend_name)
    lex = models.Backend.objects.get(name=ex_backend_name)
    models.Tool.objects.create(name=name, display_name=display_name, path=path, backend=lex, fs_backend=lfs)

def add_tool_to_all_tools(toolname):
    from yabiadmin.yabi import models
    tool = models.Tool.objects.get(name=toolname)
    tg = models.ToolGroup.objects.get(name='select data')
    alltools = models.ToolSet.objects.get(name='alltools')
    tg.toolgrouping_set.create(tool=tool, tool_set=alltools)

def remove_tool_from_all_tools(toolname):
    from yabiadmin.yabi import models
    models.ToolGrouping.objects.filter(tool__name=toolname, tool_set__name='alltools', tool_group__name='select data').delete()

def create_exploding_backend():
    from yabiadmin.yabi import models
    exploding_backend = models.Backend.objects.create(name='Exploding Backend', scheme='explode', hostname='localhost.localdomain', path='/', submission='${command}\n')
    null_credential = models.Credential.objects.get(description='null credential')
    models.BackendCredential.objects.create(backend=exploding_backend, credential=null_credential, homedir='')

def create_torque_backend():
    from yabiadmin.yabi import models
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

def create_backend(scheme="ssh", hostname="localhost.localdomain",path="/",submission="${command}"):
    from yabiadmin.yabi import models
    backend = models.Backend.objects.create(name='Test %s Backend'%scheme.upper(), scheme=scheme, hostname=hostname, path=path, submission=submission)
    # continue this...
    
def create_localfs_backend(scheme="localfs", hostname="localhost.localdomain", path="/tmp/yabi-localfs-test/"):
    from yabiadmin.yabi import models
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
    from yabiadmin.yabi import models
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
    from yabiadmin.yabi import models
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
    from yabiadmin.yabi import models
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
    from yabiadmin.yabi import models
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

def create_ssh_exec_backend(scheme="ssh", hostname="localhost.localdomain", path="/", submission=None, port=None):
    from yabiadmin.yabi import models
    
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
    from yabiadmin.yabi import models
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
    from yabiadmin.yabi import models
    backend = models.Backend.objects.get(scheme=scheme,hostname=hostname)
    for key,arg in kwargs.iteritems():
        setattr(backend,key,arg)
    backend.save()
    
    
