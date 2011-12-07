# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
import os

from ..migrationutils import *

class Migration(DataMigration):

    def forwards(self, orm):
        # all calls to this orm
        set_default_orm(orm)
        
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
   
        yabi_backend_1=yabi_backend('nullbackend','Use this backend when tools should not be run ie fileselector','null','localhost.localdomain',None,'/')
        yabi_backend_1.save()
        
        yabi_tool_1 = yabi_tool(name = 'fileselector', display_name='select file', path='', description='Select a file from your workspace directory.',
                                backend=yabi_backend_1, fs_backend=yabi_backend_1,
                                accepts_input=False,
                                cpus='',
                                walltime='',module='',queue='',max_memory='',job_type='',lcopy=False, link=False )
        yabi_tool_1.save()
        
        yabi_tooloutputextension_1 = yabi_tooloutputextension( yabi_tool_1, yabi_fileextension_1 )
        
        yabi_toolgroup_1 = yabi_toolgroup('select data')
        yabi_toolgroup_1.save()

        yabi_toolset_1 = yabi_toolset('alltools')
        yabi_toolset_1.save()
       
        yabi_toolgrouping_1 = yabi_toolgrouping( yabi_toolgroup_1, yabi_tool_1, yabi_toolset_1 )
        yabi_toolgrouping_1.save()

        yabi_tooloutputextension_1.save()

        yabi_credential_1 = yabi_credential(yabi_user_1,'null credential',username='demo')
        yabi_credential_1.save()

        yabi_backend_2 = yabi_backend('Local Filesystem','This backend gives access to the file system on the machine running Yabi.','localfs','localhost',None,'/')
        yabi_backend_2.save()

        yabi_backend_3 = yabi_backend('Local Execution','This backend gives access to execution on the machine running Yabi.','localex','localhost',None,'/')
        yabi_backend_3.save()

        yabi_backendcredential_1 = yabi_backendcredential(yabi_backend_1, yabi_credential_1, homedir='')
        yabi_backendcredential_1.save()

        yabi_backendcredential_2 = yabi_backendcredential(yabi_backend_3, yabi_credential_1, '/home/cwellington/')
        yabi_backendcredential_2.save()

        yabi_backendcredential_3 = yabi_backendcredential(yabi_backend_2, yabi_credential_1, '/home/cwellington/', visible=True, default_stageout=True)
        yabi_backendcredential_3.save()

        yabi_userprofile_1 = orm.UserProfile()
        yabi_userprofile_1.user = django_user_1
        yabi_userprofile_1.save()

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

        yabi_toolparameter_1 = yabi_toolparameter(yabi_tool_1,'files',yabi_parameterswitchuse_1,
                                                    rank = 1,
                                                    mandatory = True,
                                                    hidden = False,
                                                    output_file = False,
                                                    extension_param = None,
                                                    possible_values = None,
                                                    default_value = u'selected files',
                                                    helptext = None,
                                                    batch_bundle_files = False,
                                                    file_assignment = 'batch',
                                                    use_output_filename = None )
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
