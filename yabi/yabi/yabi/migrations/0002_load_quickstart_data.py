# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import models, migrations
from ..migrationutils import *


def homedir():
    if os.environ.get('USER') == 'root':
        homedir = '/tmp'
    else:
        homedir = os.environ.get('HOME', '/tmp')

    return "%s/" % homedir


def create_quickstart_data(apps, schema_editor):
    # all calls to this orm
    set_default_orm(apps)
    
    # first lets just make a first user to own future objects
    django_user_1 = auth_user( username = 'admin', password = 'admin', email="admin@example.com", staff=True, superuser=True )
    django_user_1.save()
    
    # make this the user that owns all the future objects that are created,
    set_default_user(django_user_1)
   
    django_user_2 = auth_user( username = 'demo', password = 'demo', email="user@example.com" )
    django_user_2.save()
    
    yabi_user_1 = yabi_user('admin')
    yabi_user_1.save()
    yabi_user_2 = yabi_user('demo')
    yabi_user_2.save()
    
    yabi_fileextension_1 = yabi_fileextension("*")
    yabi_fileextension_1.save()
    yabi_fileextension_2 = yabi_fileextension("*.fa")
    yabi_fileextension_2.save()
    yabi_fileextension_3 = yabi_fileextension("*.fna")
    yabi_fileextension_3.save()
    yabi_fileextension_4 = yabi_fileextension("*.faa")
    yabi_fileextension_4.save()
    yabi_fileextension_5 = yabi_fileextension("*.fasta")
    yabi_fileextension_5.save()
    yabi_fileextension_6 = yabi_fileextension('*.ffn')
    yabi_fileextension_6.save()
    yabi_fileextension_7 = yabi_fileextension('*.frn')
    yabi_fileextension_7.save()

    yabi_filetype_1 = yabi_filetype('fasta','Fasta bioinformatics file format', [yabi_fileextension_2, yabi_fileextension_3, yabi_fileextension_4, yabi_fileextension_5, yabi_fileextension_6, yabi_fileextension_7])
    yabi_filetype_1.save()

    yabi_filetype_2 = yabi_filetype('all files','All files', [yabi_fileextension_1])
    yabi_filetype_2.save()


    yabi_backend_1=yabi_backend('nullbackend','Use this backend when tools should not be run ie fileselector','null','localhost.localdomain',None,'/')
    yabi_backend_1.save()
    
    yabi_tool_1 = yabi_tool(name = 'fileselector', display_name='select file', path='', description='Select a file from your workspace directory.', backend=yabi_backend_1, fs_backend=yabi_backend_1)
    yabi_tool_1.save()
    
    yabi_tooloutputextension_1 = yabi_tooloutputextension( yabi_tool_1, yabi_fileextension_1 )
    
    yabi_toolgroup_1 = yabi_toolgroup('select data')
    yabi_toolgroup_1.save()

    yabi_toolgroup_2 = yabi_toolgroup('system tools')
    yabi_toolgroup_2.save()


    yabi_toolset_1 = yabi_toolset('alltools')
    yabi_toolset_1.save()
  
    yabi_user_1.users.add(yabi_toolset_1)
    yabi_user_2.users.add(yabi_toolset_1)

    yabi_toolgrouping_1 = yabi_toolgrouping( yabi_toolgroup_1, yabi_tool_1, yabi_toolset_1 )
    yabi_toolgrouping_1.save()

    yabi_tooloutputextension_1.save()

    yabi_credential_1 = yabi_credential(yabi_user_2,'null credential',username='demo')
    yabi_credential_1.save()

    yabi_backend_2 = yabi_backend('Local Filesystem','This backend gives access to the file system on the machine running Yabi.','localfs','localhost',None,'/')
    yabi_backend_2.save()

    yabi_backend_3 = yabi_backend('Yabi Data Local Filesystem','This backend is to be used for stageout and BE tool data.','localfs','localhost',None,'/')
    yabi_backend_3.save()

    yabi_backend_4 = yabi_backend('Local Execution','This backend gives access to execution on the machine running Yabi.','localex','localhost',None, '/', submission="""#!/bin/sh

${command}
""")
    yabi_backend_4.save()

    user_homedir = homedir()
    stageout_dir = user_homedir + "yabi_data_dir/"

    yabi_backendcredential_1 = yabi_backendcredential(yabi_backend_4, yabi_credential_1, homedir="")
    yabi_backendcredential_1.save()

    yabi_backendcredential_2 = yabi_backendcredential(yabi_backend_2, yabi_credential_1, user_homedir, visible=True, default_stageout=False)
    yabi_backendcredential_2.save()

    yabi_backendcredential_3 = yabi_backendcredential(yabi_backend_3, yabi_credential_1, stageout_dir, default_stageout=True)
    yabi_backendcredential_3.save()

    # yabi_userprofile_1 = orm.UserProfile()
    # yabi_userprofile_1.user = django_user_1
    # yabi_userprofile_1.save()

    # yabi_userprofile_2 = orm.UserProfile()
    # yabi_userprofile_2.user = django_user_2
    # yabi_userprofile_2.save()

    yabi_parameterswitchuse_1 = yabi_parameterswitchuse('switchOnly','%(switch)s','Only the switch will be passed in the argument list.')
    yabi_parameterswitchuse_1.save()

    yabi_parameterswitchuse_2 = yabi_parameterswitchuse('valueOnly','%(value)s',"Only the value will be passed in the argument list (ie. the switch won't be used)")
    yabi_parameterswitchuse_2.save()

    yabi_parameterswitchuse_3 = yabi_parameterswitchuse('both','%(switch)s %(value)s','Both the switch and the value will be passed in the argument list. They will be separated by a space.')
    yabi_parameterswitchuse_3.save()

    yabi_parameterswitchuse_4 = yabi_parameterswitchuse('combined','%(switch)s%(value)s','Both the switch and the value will be passed in the argument list. They will be joined together with no space between them.')
    yabi_parameterswitchuse_4.save()

    yabi_parameterswitchuse_5 = yabi_parameterswitchuse('nothing','',"The switch and the value won't be passed in the argument list.")
    yabi_parameterswitchuse_5.save()

    yabi_parameterswitchuse_6 = yabi_parameterswitchuse('pair','pair','The switch and the value passed in to the argument list as a pair.')
    yabi_parameterswitchuse_6.save()

    yabi_parameterswitchuse_7 = yabi_parameterswitchuse('combined with equals','%(switch)s=%(value)s','Both the switch and the value will be passed in the argument list. They will be separated joined with an equals(=) character with no spaces.')
    yabi_parameterswitchuse_7.save()

    yabi_parameterswitchuse_8 = yabi_parameterswitchuse('redirect','>%(value)s','Use this to redirect the output of stdout into a file.')
    yabi_parameterswitchuse_8.save()

    yabi_toolparameter_1 = yabi_toolparameter(
        yabi_tool_1,
        'files',
        yabi_parameterswitchuse_1,
        rank = 1,
        mandatory = True,
        hidden = False,
        output_file = False,
        extension_param = None,
        possible_values = None,
        default_value = 'selected files',
        helptext = None,
        batch_bundle_files = False,
        file_assignment = 'batch',
        use_output_filename = None
        )
    yabi_toolparameter_1.save()

    # make sure stuff is linked together
    yabi_tooloutputextension_1.tool = yabi_tool_1.desc
    yabi_tooloutputextension_1.file_extension = yabi_fileextension_1
    yabi_tooloutputextension_1.save()

    yabi_toolgroup_1.last_modified_by = django_user_1
    yabi_toolgroup_1.created_by = django_user_1
    yabi_toolgroup_1.save()

    yabi_toolgrouping_1.last_modified_by = django_user_1
    yabi_toolgrouping_1.created_by = django_user_1
    yabi_toolgrouping_1.tool = yabi_tool_1
    yabi_toolgrouping_1.tool_set = yabi_toolset_1
    yabi_toolgrouping_1.save()

    # add the cat tool
    yabi_tool_cat = yabi_tool(name = 'cat',
                              display_name='cat',
                              path='cat',
                              description='Concatenate two or more files together.',
                              backend=yabi_backend_4,
                              fs_backend=yabi_backend_2,
                              accepts_input=True,
                              cpus='',
                              walltime='',
                              module='',
                              queue='',
                              max_memory='',
                              job_type='',
                              lcopy=True,
                              link=True
                              )
    yabi_tool_cat.save()

    # add output extension
    yabi_tooloutputextension_for_cat = yabi_tooloutputextension( yabi_tool_cat, yabi_fileextension_1 )
    yabi_tooloutputextension_for_cat.save()

    # add the tool parameters
    yabi_toolparameter_cat = yabi_toolparameter(
        yabi_tool_cat,
        'files',
        yabi_parameterswitchuse_2,
        rank = 1,
        mandatory = True,
        hidden = False,
        output_file = False,
        extension_param = None,
        possible_values = None,
        default_value = None,
        helptext = None,
        batch_bundle_files = False,
        file_assignment = 'all',
        use_output_filename = None
        )
    yabi_toolparameter_cat.save()

    # add accepted filetypes for cat
    yabi_toolparameter_cat.accepted_filetypes.add(yabi_filetype_2)
    yabi_toolparameter_cat.save()
    
    # add to tool groups
    yabi_toolgrouping_for_cat = yabi_toolgrouping( yabi_toolgroup_2, yabi_tool_cat, yabi_toolset_1 )
    yabi_toolgrouping_for_cat.save()


    # add the hostname tool
    yabi_tool_hostname = yabi_tool(name = 'hostname',
                              display_name='hostname',
                              path='hostname',
                              description='Output the hostname where run.',
                              backend=yabi_backend_4,
                              fs_backend=yabi_backend_2,
                              accepts_input=False,
                              cpus='',
                              walltime='',
                              module='',
                              queue='',
                              max_memory='',
                              job_type='',
                              lcopy=True,
                              link=True
                              )
    yabi_tool_hostname.save()

    # add output extension
    yabi_tooloutputextension_for_hostname = yabi_tooloutputextension( yabi_tool_hostname, yabi_fileextension_1 )
    yabi_tooloutputextension_for_hostname.save()

    # add the tool parameters
    yabi_toolparameter_hostname = yabi_toolparameter(
        yabi_tool_hostname,
        'h',
        yabi_parameterswitchuse_1,
        rank = 1,
        mandatory = False,
        hidden = False,
        output_file = False,
        extension_param = None,
        possible_values = None,
        default_value = '',
        helptext = None,
        batch_bundle_files = False,
        file_assignment = 'none',
        use_output_filename = None
        )
    yabi_toolparameter_hostname.save()

    # add to tool groups
    yabi_toolgrouping_for_hostname = yabi_toolgrouping( yabi_toolgroup_2, yabi_tool_hostname, yabi_toolset_1 )
    yabi_toolgrouping_for_hostname.save()


class Migration(migrations.Migration):

    dependencies = [
        ('yabi', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_quickstart_data),
    ]
