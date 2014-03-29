# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
import six


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'User.last_modified_by'
        db.alter_column(six.u('yabi_user'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'User.created_by'
        db.alter_column(six.u('yabi_user'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'BackendCredential.created_by'
        db.alter_column(six.u('yabi_backendcredential'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'BackendCredential.last_modified_by'
        db.alter_column(six.u('yabi_backendcredential'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolGroup.last_modified_by'
        db.alter_column(six.u('yabi_toolgroup'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolGroup.created_by'
        db.alter_column(six.u('yabi_toolgroup'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'FileType.last_modified_by'
        db.alter_column(six.u('yabi_filetype'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'FileType.created_by'
        db.alter_column(six.u('yabi_filetype'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Tool.last_modified_by'
        db.alter_column(six.u('yabi_tool'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Tool.created_by'
        db.alter_column(six.u('yabi_tool'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Backend.created_by'
        db.alter_column(six.u('yabi_backend'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Backend.last_modified_by'
        db.alter_column(six.u('yabi_backend'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'HostKey.last_modified_by'
        db.alter_column(six.u('yabi_hostkey'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'HostKey.created_by'
        db.alter_column(six.u('yabi_hostkey'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolParameter.last_modified_by'
        db.alter_column(six.u('yabi_toolparameter'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolParameter.created_by'
        db.alter_column(six.u('yabi_toolparameter'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolGrouping.last_modified_by'
        db.alter_column(six.u('yabi_toolgrouping'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolGrouping.created_by'
        db.alter_column(six.u('yabi_toolgrouping'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ParameterSwitchUse.last_modified_by'
        db.alter_column(six.u('yabi_parameterswitchuse'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ParameterSwitchUse.created_by'
        db.alter_column(six.u('yabi_parameterswitchuse'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Credential.created_by'
        db.alter_column(six.u('yabi_credential'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Credential.last_modified_by'
        db.alter_column(six.u('yabi_credential'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolOutputExtension.last_modified_by'
        db.alter_column(six.u('yabi_tooloutputextension'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolOutputExtension.created_by'
        db.alter_column(six.u('yabi_tooloutputextension'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'FileExtension.last_modified_by'
        db.alter_column(six.u('yabi_fileextension'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'FileExtension.created_by'
        db.alter_column(six.u('yabi_fileextension'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolSet.last_modified_by'
        db.alter_column(six.u('yabi_toolset'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'ToolSet.created_by'
        db.alter_column(six.u('yabi_toolset'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

    def backwards(self, orm):

        # Changing field 'User.last_modified_by'
        db.alter_column(six.u('yabi_user'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'User.created_by'
        db.alter_column(six.u('yabi_user'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'BackendCredential.created_by'
        db.alter_column(six.u('yabi_backendcredential'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'BackendCredential.last_modified_by'
        db.alter_column(six.u('yabi_backendcredential'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolGroup.last_modified_by'
        db.alter_column(six.u('yabi_toolgroup'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolGroup.created_by'
        db.alter_column(six.u('yabi_toolgroup'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'FileType.last_modified_by'
        db.alter_column(six.u('yabi_filetype'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'FileType.created_by'
        db.alter_column(six.u('yabi_filetype'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Tool.last_modified_by'
        db.alter_column(six.u('yabi_tool'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Tool.created_by'
        db.alter_column(six.u('yabi_tool'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Backend.created_by'
        db.alter_column(six.u('yabi_backend'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Backend.last_modified_by'
        db.alter_column(six.u('yabi_backend'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'HostKey.last_modified_by'
        db.alter_column(six.u('yabi_hostkey'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'HostKey.created_by'
        db.alter_column(six.u('yabi_hostkey'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolParameter.last_modified_by'
        db.alter_column(six.u('yabi_toolparameter'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolParameter.created_by'
        db.alter_column(six.u('yabi_toolparameter'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolGrouping.last_modified_by'
        db.alter_column(six.u('yabi_toolgrouping'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolGrouping.created_by'
        db.alter_column(six.u('yabi_toolgrouping'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ParameterSwitchUse.last_modified_by'
        db.alter_column(six.u('yabi_parameterswitchuse'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ParameterSwitchUse.created_by'
        db.alter_column(six.u('yabi_parameterswitchuse'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Credential.created_by'
        db.alter_column(six.u('yabi_credential'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Credential.last_modified_by'
        db.alter_column(six.u('yabi_credential'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolOutputExtension.last_modified_by'
        db.alter_column(six.u('yabi_tooloutputextension'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolOutputExtension.created_by'
        db.alter_column(six.u('yabi_tooloutputextension'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'FileExtension.last_modified_by'
        db.alter_column(six.u('yabi_fileextension'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'FileExtension.created_by'
        db.alter_column(six.u('yabi_fileextension'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolSet.last_modified_by'
        db.alter_column(six.u('yabi_toolset'), 'last_modified_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'ToolSet.created_by'
        db.alter_column(six.u('yabi_toolset'), 'created_by_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

    models = {
        six.u('auth.group'): {
            'Meta': {'object_name': 'Group'},
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': six.u("orm['auth.Permission']"), 'symmetrical': 'False', 'blank': 'True'})
        },
        six.u('auth.permission'): {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['contenttypes.ContentType']")}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        six.u('auth.user'): {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': six.u("orm['auth.Group']"), 'symmetrical': 'False', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': six.u("orm['auth.Permission']"), 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        six.u('contenttypes.contenttype'): {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        six.u('yabi.backend'): {
            'Meta': {'object_name': 'Backend'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backend_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backend_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'lcopy_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_connections': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tasks_per_user': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        six.u('yabi.backendcredential'): {
            'Meta': {'object_name': 'BackendCredential'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.Backend']")}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backendcredential_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credential': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.Credential']")}),
            'default_stageout': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'homedir': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backendcredential_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        six.u('yabi.credential'): {
            'Meta': {'object_name': 'Credential'},
            'backends': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': six.u("orm['yabi.Backend']"), 'null': 'True', 'through': six.u("orm['yabi.BackendCredential']"), 'blank': 'True'}),
            'cert': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credential_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'expires_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credential_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.User']")}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        six.u('yabi.fileextension'): {
            'Meta': {'object_name': 'FileExtension'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fileextension_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fileextension_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        six.u('yabi.filetype'): {
            'Meta': {'object_name': 'FileType'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filetype_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extensions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': six.u("orm['yabi.FileExtension']"), 'null': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'filetype_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        six.u('yabi.hostkey'): {
            'Meta': {'object_name': 'HostKey'},
            'allowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hostkey_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'max_length': '16384'}),
            'fingerprint': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hostkey_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        six.u('yabi.parameterswitchuse'): {
            'Meta': {'object_name': 'ParameterSwitchUse'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameterswitchuse_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'formatstring': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameterswitchuse_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        six.u('yabi.tool'): {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tool'},
            'accepts_input': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.Backend']")}),
            'cpus': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tool_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fs_backend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fs_backends'", 'to': six.u("orm['yabi.Backend']")}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': six.u("orm['yabi.ToolGroup']"), 'null': 'True', 'through': six.u("orm['yabi.ToolGrouping']"), 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_type': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tool_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'lcopy_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_memory': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'module': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'output_filetypes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': six.u("orm['yabi.FileExtension']"), 'null': 'True', 'through': six.u("orm['yabi.ToolOutputExtension']"), 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'queue': ('django.db.models.fields.CharField', [], {'default': "'normal'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'walltime': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        six.u('yabi.toolgroup'): {
            'Meta': {'object_name': 'ToolGroup'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgroup_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgroup_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        six.u('yabi.toolgrouping'): {
            'Meta': {'object_name': 'ToolGrouping'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgrouping_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgrouping_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.Tool']")}),
            'tool_group': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.ToolGroup']")}),
            'tool_set': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.ToolSet']")})
        },
        six.u('yabi.tooloutputextension'): {
            'Meta': {'object_name': 'ToolOutputExtension'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooloutputextension_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_extension': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.FileExtension']")}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooloutputextension_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'must_be_larger_than': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'must_exist': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.Tool']")})
        },
        six.u('yabi.toolparameter'): {
            'Meta': {'object_name': 'ToolParameter'},
            'accepted_filetypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': six.u("orm['yabi.FileType']"), 'symmetrical': 'False', 'blank': 'True'}),
            'batch_bundle_files': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolparameter_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'extension_param': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.FileExtension']"), 'null': 'True', 'blank': 'True'}),
            'file_assignment': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'helptext': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolparameter_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'output_file': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'possible_values': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'switch': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'switch_use': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.ParameterSwitchUse']")}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.Tool']")}),
            'use_output_filename': ('django.db.models.fields.related.ForeignKey', [], {'to': six.u("orm['yabi.ToolParameter']"), 'null': 'True', 'blank': 'True'})
        },
        six.u('yabi.toolset'): {
            'Meta': {'object_name': 'ToolSet'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolset_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolset_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'db_table': "'yabi_user_toolsets'", 'to': six.u("orm['yabi.User']")})
        },
        six.u('yabi.user'): {
            'Meta': {'ordering': "('name',)", 'object_name': 'User'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credential_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            six.u('id'): ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': six.u("orm['auth.User']")}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': six.u("orm['auth.User']"), 'unique': 'True'}),
            'user_option_access': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        six.u('yabi.yabicache'): {
            'Meta': {'object_name': 'YabiCache', 'db_table': "'yabi_cache'"},
            'cache_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'primary_key': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['yabi']