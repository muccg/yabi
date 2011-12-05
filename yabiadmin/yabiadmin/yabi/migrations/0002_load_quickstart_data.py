# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import os

from ..migrationutils import add_user

class Migration(DataMigration):

    def forwards(self, orm):

        django_user_1 = add_user( orm, username = 'admin', password = 'admin', email="admin@example.com", staff=True, superuser=True )
        django_user_1.save()
        
        django_user_2 = add_user( orm, username = 'demo', password = 'demo', email="user@example.com" )
        django_user_2.save()
        
        yabi_user_1 = orm['yabi.User']()
        yabi_user_1.last_modified_by = django_user_1
        yabi_user_1.last_modified_on = datetime.datetime(2011, 9, 26, 10, 56, 16)
        yabi_user_1.created_by = django_user_1
        yabi_user_1.created_on = datetime.datetime(2011, 9, 26, 10, 56, 16)
        yabi_user_1.name = u'admin'
        
        #yabi_user_1.last_login = "2011-09-26 11:08:44", 
        yabi_user_1.save()
        
        # now set it correctly
        yabi_user_1.last_modified_by = django_user_1
        yabi_user_1.created_by = django_user_1
        yabi_user_1.save()
        
        yabi_user_2 = orm['yabi.User']()
        yabi_user_2.last_modified_by = django_user_1
        yabi_user_2.last_modified_on = datetime.datetime(2011, 9, 26, 10, 56, 16)
        yabi_user_2.created_by = django_user_1
        yabi_user_2.created_on = datetime.datetime(2011, 9, 26, 10, 56, 16)
        yabi_user_2.name = u'demo'
        
        
        
        yabi_user_2.save()
        
        # now set it correctly
        yabi_user_2.last_modified_by = django_user_1
        yabi_user_2.created_by = django_user_1
        yabi_user_2.save()
        
        yabi_fileextension_1 = orm.FileExtension()
        yabi_fileextension_1.last_modified_by = django_user_1
        yabi_fileextension_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_fileextension_1.created_by = django_user_1
        yabi_fileextension_1.created_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_fileextension_1.pattern = u'*'
        yabi_fileextension_1.save()

        yabi_fileextension_2 = orm.FileExtension()
        yabi_fileextension_2.last_modified_by = django_user_1
        yabi_fileextension_2.last_modified_on = datetime.datetime(2009, 6, 26, 12, 44, 17)
        yabi_fileextension_2.created_by = django_user_1
        yabi_fileextension_2.created_on = datetime.datetime(2009, 6, 26, 12, 44, 17)
        yabi_fileextension_2.pattern = u'*.fa'
        yabi_fileextension_2.save()

        yabi_fileextension_3 = orm.FileExtension()
        yabi_fileextension_3.last_modified_by = django_user_1
        yabi_fileextension_3.last_modified_on = datetime.datetime(2009, 6, 26, 12, 44, 17)
        yabi_fileextension_3.created_by = django_user_1
        yabi_fileextension_3.created_on = datetime.datetime(2009, 6, 26, 12, 44, 17)
        yabi_fileextension_3.pattern = u'*.fna'
        yabi_fileextension_3.save()

        yabi_fileextension_4 = orm.FileExtension()
        yabi_fileextension_4.last_modified_by = django_user_1
        yabi_fileextension_4.last_modified_on = datetime.datetime(2009, 6, 26, 12, 44, 17)
        yabi_fileextension_4.created_by = django_user_1
        yabi_fileextension_4.created_on = datetime.datetime(2009, 6, 26, 12, 44, 17)
        yabi_fileextension_4.pattern = u'*.faa'
        yabi_fileextension_4.save()

        yabi_fileextension_5 = orm.FileExtension()
        yabi_fileextension_5.last_modified_by = django_user_1
        yabi_fileextension_5.last_modified_on = datetime.datetime(2009, 6, 26, 12, 44, 20)
        yabi_fileextension_5.created_by = django_user_1
        yabi_fileextension_5.created_on = datetime.datetime(2009, 6, 26, 12, 44, 20)
        yabi_fileextension_5.pattern = u'*.fasta'
        yabi_fileextension_5.save()

        yabi_fileextension_6 = orm.FileExtension()
        yabi_fileextension_6.last_modified_on = datetime.datetime(2011, 4, 27, 14, 22, 31)
        yabi_fileextension_6.created_on = datetime.datetime(2011, 4, 27, 14, 22, 31)
        yabi_fileextension_6.pattern = u'*.ffn'
        yabi_fileextension_6.save()

        yabi_fileextension_7 = orm.FileExtension()
        yabi_fileextension_7.last_modified_on = datetime.datetime(2011, 4, 27, 14, 22, 48)
        yabi_fileextension_7.created_on = datetime.datetime(2011, 4, 27, 14, 22, 48)
        yabi_fileextension_7.pattern = u'*.frn'
        yabi_fileextension_7.save()
        
        
        yabi_backend_1 = orm['yabi.Backend']()
        yabi_backend_1.last_modified_by = django_user_1
        yabi_backend_1.last_modified_on = datetime.datetime(2011, 9, 26, 10, 59, 4)
        yabi_backend_1.created_by = django_user_1
        yabi_backend_1.created_on = datetime.datetime(2011, 9, 26, 10, 59, 4)
        yabi_backend_1.name = u'nullbackend'
        yabi_backend_1.description = u'Use this backend when tools should not be run ie fileselector'
        yabi_backend_1.scheme = u'null'
        yabi_backend_1.hostname = u'localhost.localdomain'
        yabi_backend_1.port = None
        yabi_backend_1.path = u'/'
        yabi_backend_1.max_connections = None
        yabi_backend_1.lcopy_supported = True
        yabi_backend_1.link_supported = True
        yabi_backend_1.submission = u''
        yabi_backend_1.save()
        
        
        yabi_tool_1 = orm.Tool()
        yabi_tool_1.last_modified_by = django_user_1
        yabi_tool_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 10, 5)
        yabi_tool_1.created_by = None
        yabi_tool_1.created_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_tool_1.name = u'fileselector'
        yabi_tool_1.display_name = u'select file'
        yabi_tool_1.path = u''
        yabi_tool_1.description = u'Select a file from your workspace directory.'
        yabi_tool_1.enabled = True
        yabi_tool_1.backend = yabi_backend_1
        yabi_tool_1.fs_backend = yabi_backend_1
        yabi_tool_1.accepts_input = False
        yabi_tool_1.cpus = u''
        yabi_tool_1.walltime = u''
        yabi_tool_1.module = u''
        yabi_tool_1.queue = u''
        yabi_tool_1.max_memory = None
        yabi_tool_1.job_type = u''
        yabi_tool_1.lcopy_supported = False
        yabi_tool_1.link_supported = False
        yabi_tool_1.save()
        
        yabi_tooloutputextension_1 = orm['yabi.ToolOutputExtension']()
        yabi_tooloutputextension_1.last_modified_by = None
        yabi_tooloutputextension_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_tooloutputextension_1.created_by = None
        yabi_tooloutputextension_1.created_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_tooloutputextension_1.must_exist = None
        yabi_tooloutputextension_1.tool = yabi_tool_1
        yabi_tooloutputextension_1.file_extension = yabi_fileextension_1
        yabi_tooloutputextension_1.must_be_larger_than = None
        
        yabi_toolgroup_1 = orm['yabi.ToolGroup']()
        yabi_toolgroup_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 10, 21)
        yabi_toolgroup_1.created_on = datetime.datetime(2011, 9, 26, 10, 57, 23)
        yabi_toolgroup_1.name = u'select data'
        yabi_toolgroup_1.save()

        yabi_toolset_1 = orm['yabi.ToolSet']()
        yabi_toolset_1.last_modified_on = datetime.datetime(2011, 9, 26, 10, 56, 31)
        yabi_toolset_1.created_on = datetime.datetime(2011, 9, 26, 10, 56, 9)
        yabi_toolset_1.name = u'alltools'
        yabi_toolset_1.save()

        
        yabi_toolgrouping_1 = orm['yabi.ToolGrouping']()
        yabi_toolgrouping_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 10, 21)
        yabi_toolgrouping_1.created_on = datetime.datetime(2011, 9, 26, 11, 10, 21)
        yabi_toolgrouping_1.tool_group = yabi_toolgroup_1
        yabi_toolgrouping_1.tool = yabi_tool_1
        yabi_toolgrouping_1.tool_set = yabi_toolset_1
        yabi_toolgrouping_1.save()

        yabi_tooloutputextension_1.save()

        yabi_credential_1 = orm['yabi.Credential']()
        yabi_credential_1.last_modified_by = django_user_1
        yabi_credential_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 8, 52)
        yabi_credential_1.created_by = django_user_1
        yabi_credential_1.created_on = datetime.datetime(2011, 9, 26, 11, 1, 39)
        yabi_credential_1.description = u'null credential'
        yabi_credential_1.username = u'demo'
        yabi_credential_1.password = u''
        yabi_credential_1.cert = u''
        yabi_credential_1.key = u''
        yabi_credential_1.user = yabi_user_1
        yabi_credential_1.expires_on = datetime.datetime(2111, 1, 1, 12, 0)
        yabi_credential_1.encrypted = False
        yabi_credential_1.encrypt_on_login = False
        yabi_credential_1.save()

        yabi_backend_1 = orm.Backend()
        yabi_backend_1.last_modified_by = django_user_1
        yabi_backend_1.last_modified_on = datetime.datetime(2011, 9, 26, 10, 59, 4)
        yabi_backend_1.created_by = django_user_1
        yabi_backend_1.created_on = datetime.datetime(2011, 9, 26, 10, 59, 4)
        yabi_backend_1.name = u'nullbackend'
        yabi_backend_1.description = u'Use this backend when tools should not be run ie fileselector'
        yabi_backend_1.scheme = u'null'
        yabi_backend_1.hostname = u'localhost.localdomain'
        yabi_backend_1.port = None
        yabi_backend_1.path = u'/'
        yabi_backend_1.max_connections = None
        yabi_backend_1.lcopy_supported = True
        yabi_backend_1.link_supported = True
        yabi_backend_1.submission = u''
        yabi_backend_1.save()

        yabi_backend_2 = orm.Backend()
        yabi_backend_2.last_modified_by = django_user_1
        yabi_backend_2.last_modified_on = datetime.datetime(2011, 11, 15, 10, 48, 13)
        yabi_backend_2.created_by = django_user_1
        yabi_backend_2.created_on = datetime.datetime(2011, 11, 15, 10, 47, 24)
        yabi_backend_2.name = u'Local Filesystem'
        yabi_backend_2.description = u'This backend gives access to the file system on the machine running Yabi.'
        yabi_backend_2.scheme = u'localfs'
        yabi_backend_2.hostname = u'localhost'
        yabi_backend_2.port = None
        yabi_backend_2.path = u'/'
        yabi_backend_2.max_connections = None
        yabi_backend_2.lcopy_supported = True
        yabi_backend_2.link_supported = True
        yabi_backend_2.submission = u''
        yabi_backend_2.save()

        yabi_backend_3 = orm.Backend()
        yabi_backend_3.last_modified_by = django_user_1
        yabi_backend_3.last_modified_on = datetime.datetime(2011, 11, 15, 10, 48, 4)
        yabi_backend_3.created_by = django_user_1
        yabi_backend_3.created_on = datetime.datetime(2011, 11, 15, 10, 48, 4)
        yabi_backend_3.name = u'Local Execution'
        yabi_backend_3.description = u'This backend gives access to execution on the machine running Yabi.'
        yabi_backend_3.scheme = u'localex'
        yabi_backend_3.hostname = u'localhost'
        yabi_backend_3.port = None
        yabi_backend_3.path = u'/'
        yabi_backend_3.max_connections = None
        yabi_backend_3.lcopy_supported = True
        yabi_backend_3.link_supported = True
        yabi_backend_3.submission = u''
        yabi_backend_3.save()

        yabi_backendcredential_1 = orm.BackendCredential()
        yabi_backendcredential_1.last_modified_by = django_user_1
        yabi_backendcredential_1.last_modified_on = datetime.datetime(2011, 10, 11, 12, 28, 58)
        yabi_backendcredential_1.created_by = django_user_1
        yabi_backendcredential_1.created_on = datetime.datetime(2011, 10, 11, 12, 28, 4)
        yabi_backendcredential_1.backend = yabi_backend_1
        yabi_backendcredential_1.credential = yabi_credential_1
        yabi_backendcredential_1.homedir = u''
        yabi_backendcredential_1.visible = False
        yabi_backendcredential_1.default_stageout = False
        yabi_backendcredential_1.submission = u''
        yabi_backendcredential_1.save()

        yabi_backendcredential_2 = orm.BackendCredential()
        yabi_backendcredential_2.last_modified_by = django_user_1
        yabi_backendcredential_2.last_modified_on = datetime.datetime(2011, 12, 1, 17, 12, 26, 938282)
        yabi_backendcredential_2.created_by = django_user_1
        yabi_backendcredential_2.created_on = datetime.datetime(2011, 11, 15, 10, 48, 48)
        yabi_backendcredential_2.backend = yabi_backend_3
        yabi_backendcredential_2.credential = yabi_credential_1
        yabi_backendcredential_2.homedir = u'/home/cwellington/'
        yabi_backendcredential_2.visible = False
        yabi_backendcredential_2.default_stageout = False
        yabi_backendcredential_2.submission = u''
        yabi_backendcredential_2.save()

        yabi_backendcredential_3 = orm.BackendCredential()
        yabi_backendcredential_3.last_modified_by = django_user_1
        yabi_backendcredential_3.last_modified_on = datetime.datetime(2011, 12, 1, 17, 12, 26, 947421)
        yabi_backendcredential_3.created_by = django_user_1
        yabi_backendcredential_3.created_on = datetime.datetime(2011, 11, 15, 10, 49, 4)
        yabi_backendcredential_3.backend = yabi_backend_2
        yabi_backendcredential_3.credential = yabi_credential_1
        yabi_backendcredential_3.homedir = u'/home/cwellington/'
        yabi_backendcredential_3.visible = True
        yabi_backendcredential_3.default_stageout = True
        yabi_backendcredential_3.submission = u''
        yabi_backendcredential_3.save()

        yabi_userprofile_1 = orm.UserProfile()
        yabi_userprofile_1.user = django_user_1
        yabi_userprofile_1.save()

        yabi_filetype_1 = orm.FileType()
        yabi_filetype_1.last_modified_on = datetime.datetime(2011, 4, 27, 14, 22, 53)
        yabi_filetype_1.created_by = django_user_1
        yabi_filetype_1.created_on = datetime.datetime(2009, 6, 26, 12, 44, 20)
        yabi_filetype_1.name = u'fasta'
        yabi_filetype_1.description = u''
        yabi_filetype_1.save()

        yabi_filetype_1.extensions.add(yabi_fileextension_2)
        yabi_filetype_1.extensions.add(yabi_fileextension_3)
        yabi_filetype_1.extensions.add(yabi_fileextension_4)
        yabi_filetype_1.extensions.add(yabi_fileextension_5)
        yabi_filetype_1.extensions.add(yabi_fileextension_6)
        yabi_filetype_1.extensions.add(yabi_fileextension_7)

        yabi_parameterswitchuse_1 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_1.last_modified_on = datetime.datetime(2010, 4, 21, 16, 29, 50)
        yabi_parameterswitchuse_1.created_by = django_user_1
        yabi_parameterswitchuse_1.created_on = datetime.datetime(2009, 3, 31, 16, 40, 26)
        yabi_parameterswitchuse_1.display_text = u'switchOnly'
        yabi_parameterswitchuse_1.formatstring = u'%(switch)s'
        yabi_parameterswitchuse_1.description = u'Only the switch will be passed in the argument list.'
        yabi_parameterswitchuse_1.save()

        yabi_parameterswitchuse_2 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_2.last_modified_on = datetime.datetime(2010, 4, 21, 16, 29, 57)
        yabi_parameterswitchuse_2.created_by = django_user_1
        yabi_parameterswitchuse_2.created_on = datetime.datetime(2009, 3, 31, 16, 41, 11)
        yabi_parameterswitchuse_2.display_text = u'valueOnly'
        yabi_parameterswitchuse_2.formatstring = u'%(value)s'
        yabi_parameterswitchuse_2.description = u"Only the value will be passed in the argument list (ie. the switch won't be used)"
        yabi_parameterswitchuse_2.save()

        yabi_parameterswitchuse_3 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_3.last_modified_on = datetime.datetime(2010, 4, 16, 13, 12, 43)
        yabi_parameterswitchuse_3.created_by = django_user_1
        yabi_parameterswitchuse_3.created_on = datetime.datetime(2009, 3, 31, 16, 42, 10)
        yabi_parameterswitchuse_3.display_text = u'both'
        yabi_parameterswitchuse_3.formatstring = u'%(switch)s %(value)s'
        yabi_parameterswitchuse_3.description = u'Both the switch and the value will be passed in the argument list. They will be separated by a space.'
        yabi_parameterswitchuse_3.save()

        yabi_parameterswitchuse_4 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_4.last_modified_on = datetime.datetime(2010, 4, 16, 13, 12, 39)
        yabi_parameterswitchuse_4.created_by = django_user_1
        yabi_parameterswitchuse_4.created_on = datetime.datetime(2009, 3, 31, 16, 43, 22)
        yabi_parameterswitchuse_4.display_text = u'combined'
        yabi_parameterswitchuse_4.formatstring = u'%(switch)s%(value)s'
        yabi_parameterswitchuse_4.description = u'Both the switch and the value will be passed in the argument list. They will be joined together with no space between them.'
        yabi_parameterswitchuse_4.save()

        yabi_parameterswitchuse_5 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_5.last_modified_on = datetime.datetime(2011, 4, 5, 15, 17, 58)
        yabi_parameterswitchuse_5.created_by = django_user_1
        yabi_parameterswitchuse_5.created_on = datetime.datetime(2009, 3, 31, 16, 44, 23)
        yabi_parameterswitchuse_5.display_text = u'nothing'
        yabi_parameterswitchuse_5.formatstring = u''
        yabi_parameterswitchuse_5.description = u"The switch and the value won't be passed in the argument list."
        yabi_parameterswitchuse_5.save()

        yabi_parameterswitchuse_6 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_6.last_modified_by = django_user_1
        yabi_parameterswitchuse_6.last_modified_on = datetime.datetime(2009, 3, 31, 16, 44, 23)
        yabi_parameterswitchuse_6.created_by = django_user_1
        yabi_parameterswitchuse_6.created_on = datetime.datetime(2009, 3, 31, 16, 44, 23)
        yabi_parameterswitchuse_6.display_text = u'pair'
        yabi_parameterswitchuse_6.formatstring = u'pair'
        yabi_parameterswitchuse_6.description = u'The switch and the value passed in to the argument list as a pair.'
        yabi_parameterswitchuse_6.save()

        yabi_parameterswitchuse_7 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_7.last_modified_on = datetime.datetime(2010, 4, 16, 13, 39, 13)
        yabi_parameterswitchuse_7.created_on = datetime.datetime(2010, 4, 16, 13, 32, 55)
        yabi_parameterswitchuse_7.display_text = u'combined with equals'
        yabi_parameterswitchuse_7.formatstring = u'%(switch)s=%(value)s'
        yabi_parameterswitchuse_7.description = u'Both the switch and the value will be passed in the argument list. They will be separated joined with an equals(=) character with no spaces.'
        yabi_parameterswitchuse_7.save()

        yabi_parameterswitchuse_8 = orm.ParameterSwitchUse()
        yabi_parameterswitchuse_8.last_modified_on = datetime.datetime(2010, 12, 2, 13, 23, 44)
        yabi_parameterswitchuse_8.created_on = datetime.datetime(2010, 12, 2, 13, 23, 44)
        yabi_parameterswitchuse_8.display_text = u'redirect'
        yabi_parameterswitchuse_8.formatstring = u'>%(value)s'
        yabi_parameterswitchuse_8.description = u'Use this to redirect the output of stdout into a file.'
        yabi_parameterswitchuse_8.save()

        yabi_toolparameter_1 = orm.ToolParameter()
        yabi_toolparameter_1.last_modified_by = django_user_1
        yabi_toolparameter_1.last_modified_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_toolparameter_1.created_by = django_user_1
        yabi_toolparameter_1.created_on = datetime.datetime(2011, 9, 26, 11, 9, 31)
        yabi_toolparameter_1.tool = yabi_tool_1
        yabi_toolparameter_1.switch = u'files'
        yabi_toolparameter_1.switch_use = yabi_parameterswitchuse_1
        yabi_toolparameter_1.rank = 1
        yabi_toolparameter_1.mandatory = True
        yabi_toolparameter_1.hidden = False
        yabi_toolparameter_1.output_file = False
        yabi_toolparameter_1.extension_param = None
        yabi_toolparameter_1.possible_values = None
        yabi_toolparameter_1.default_value = u'selected files'
        yabi_toolparameter_1.helptext = None
        yabi_toolparameter_1.batch_bundle_files = False
        yabi_toolparameter_1.file_assignment = u'batch'
        yabi_toolparameter_1.use_output_filename = None
        yabi_toolparameter_1.save()

        yabi_tooloutputextension_1.tool = yabi_tool_1
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

        # set the backend credentials to the user's homedir
        ex_bec = orm.BackendCredential.objects.get(id=2)
        ex_bec.homedir = "%s%s" % (os.environ['HOME'], '/')
        ex_bec.save()
        fs_bec = orm.BackendCredential.objects.get(id=3)
        fs_bec.homedir = "%s%s" % (os.environ['HOME'], '/')
        fs_bec.save()

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yabi.backend': {
            'Meta': {'object_name': 'Backend'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backend_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backend_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'lcopy_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_connections': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'yabi.backendcredential': {
            'Meta': {'object_name': 'BackendCredential'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.Backend']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backendcredential_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credential': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.Credential']"}),
            'default_stageout': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'homedir': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backendcredential_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'yabi.credential': {
            'Meta': {'object_name': 'Credential'},
            'backends': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabi.Backend']", 'null': 'True', 'through': "orm['yabi.BackendCredential']", 'blank': 'True'}),
            'cert': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credential_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'encrypt_on_login': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'encrypted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expires_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credential_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.User']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'yabi.fileextension': {
            'Meta': {'object_name': 'FileExtension'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fileextension_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fileextension_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'yabi.filetype': {
            'Meta': {'object_name': 'FileType'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filetype_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extensions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabi.FileExtension']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filetype_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'yabi.parameterswitchuse': {
            'Meta': {'object_name': 'ParameterSwitchUse'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameterswitchuse_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'formatstring': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameterswitchuse_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        'yabi.tool': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tool'},
            'accepts_input': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.Backend']"}),
            'cpus': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tool_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fs_backend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fs_backends'", 'to': "orm['yabi.Backend']"}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabi.ToolGroup']", 'null': 'True', 'through': "orm['yabi.ToolGrouping']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_type': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tool_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'lcopy_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_memory': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'module': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'output_filetypes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabi.FileExtension']", 'null': 'True', 'through': "orm['yabi.ToolOutputExtension']", 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'queue': ('django.db.models.fields.CharField', [], {'default': "'normal'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'walltime': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'yabi.toolgroup': {
            'Meta': {'object_name': 'ToolGroup'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgroup_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgroup_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'yabi.toolgrouping': {
            'Meta': {'object_name': 'ToolGrouping'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgrouping_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgrouping_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.Tool']"}),
            'tool_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.ToolGroup']"}),
            'tool_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.ToolSet']"})
        },
        'yabi.tooloutputextension': {
            'Meta': {'object_name': 'ToolOutputExtension'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooloutputextension_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_extension': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.FileExtension']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooloutputextension_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'must_be_larger_than': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'must_exist': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.Tool']"})
        },
        'yabi.toolparameter': {
            'Meta': {'object_name': 'ToolParameter'},
            'accepted_filetypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yabi.FileType']", 'symmetrical': 'False', 'blank': 'True'}),
            'batch_bundle_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolparameter_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extension_param': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.FileExtension']", 'null': 'True', 'blank': 'True'}),
            'file_assignment': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'helptext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolparameter_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'output_file': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'possible_values': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'switch': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'switch_use': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.ParameterSwitchUse']"}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.Tool']"}),
            'use_output_filename': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.ToolParameter']", 'null': 'True', 'blank': 'True'})
        },
        'yabi.toolset': {
            'Meta': {'object_name': 'ToolSet'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolset_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolset_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'db_table': "'yabi_user_toolsets'", 'to': "orm['yabi.User']"})
        },
        'yabi.user': {
            'Meta': {'object_name': 'User'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'yabi.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['yabi']
