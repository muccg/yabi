# -*- coding: utf-8 -*-
import base64
import binascii
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):
    def forwards(self, orm):
        for job in orm['yabiengine.Job'].objects.all():
            if job.command_template is not None:
                job.command_template = base64.encodestring(job.command_template)
                job.save()

    def backwards(self, orm):
        for job in orm['yabiengine.Job'].objects.all():
            job.command_template = base64.decodestring(job.command_template)
            job.save()

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'yabi.backend': {
            'Meta': {'object_name': 'Backend'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backend_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'dynamic_backend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dynamic_backend_configuration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.DynamicBackendConfiguration']", 'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backend_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'lcopy_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'port': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'temporary_directory': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
        },
        u'yabi.dynamicbackendconfiguration': {
            'Meta': {'object_name': 'DynamicBackendConfiguration'},
            'configuration': ('django.db.models.fields.TextField', [], {}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dynamicbackendconfiguration_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dynamicbackendconfiguration_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'yabi.fileextension': {
            'Meta': {'ordering': "('pattern',)", 'object_name': 'FileExtension'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fileextension_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fileextension_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'yabi.tool': {
            'Meta': {'object_name': 'Tool'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.Backend']"}),
            'cpus': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tool_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.ToolDesc']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fs_backend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fs_backends'", 'to': u"orm['yabi.Backend']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_type': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tool_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'lcopy_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'link_supported': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'max_memory': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'module': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'queue': ('django.db.models.fields.CharField', [], {'default': "'normal'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'use_same_dynamic_backend': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'walltime': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        u'yabi.tooldesc': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ToolDesc'},
            'accepts_input': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooldesc_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['yabi.ToolGroup']", 'null': 'True', 'through': u"orm['yabi.ToolGrouping']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooldesc_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'output_filetypes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['yabi.FileExtension']", 'null': 'True', 'through': u"orm['yabi.ToolOutputExtension']", 'blank': 'True'})
        },
        u'yabi.toolgroup': {
            'Meta': {'object_name': 'ToolGroup'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgroup_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgroup_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'yabi.toolgrouping': {
            'Meta': {'object_name': 'ToolGrouping'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgrouping_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolgrouping_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.ToolDesc']"}),
            'tool_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.ToolGroup']"}),
            'tool_set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.ToolSet']"})
        },
        u'yabi.tooloutputextension': {
            'Meta': {'object_name': 'ToolOutputExtension'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooloutputextension_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_extension': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.FileExtension']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tooloutputextension_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'must_be_larger_than': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'must_exist': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.ToolDesc']"})
        },
        u'yabi.toolset': {
            'Meta': {'object_name': 'ToolSet'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolset_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'toolset_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'users'", 'blank': 'True', 'db_table': "'yabi_user_toolsets'", 'to': u"orm['yabi.User']"})
        },
        u'yabi.user': {
            'Meta': {'ordering': "('name',)", 'object_name': 'User'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_creators'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credential_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifiers'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'user_option_access': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'yabiengine.dynamicbackendinstance': {
            'Meta': {'object_name': 'DynamicBackendInstance'},
            'configuration': ('django.db.models.fields.TextField', [], {}),
            'created_for_job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Job']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'destroyed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_handle': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'yabiengine.job': {
            'Meta': {'object_name': 'Job'},
            'command': ('django.db.models.fields.TextField', [], {}),
            'command_template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cpus': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'dynamic_backends': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['yabiengine.DynamicBackendInstance']", 'null': 'True', 'through': u"orm['yabiengine.JobDynamicBackend']", 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'exec_backend': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'fs_backend': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_type': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'max_memory': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'module': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'preferred_stagein_method': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'preferred_stageout_method': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'queue': ('django.db.models.fields.CharField', [], {'default': "'normal'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'stageout': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'task_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tool': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.Tool']", 'null': 'True'}),
            'walltime': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Workflow']"})
        },
        u'yabiengine.jobdynamicbackend': {
            'Meta': {'object_name': 'JobDynamicBackend'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.Backend']"}),
            'be_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.DynamicBackendInstance']"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Job']"})
        },
        u'yabiengine.queuedworkflow': {
            'Meta': {'object_name': 'QueuedWorkflow'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Workflow']"})
        },
        u'yabiengine.savedworkflow': {
            'Meta': {'object_name': 'SavedWorkflow'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'yabiengine.stagein': {
            'Meta': {'object_name': 'StageIn'},
            'dst': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'src': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Task']"})
        },
        u'yabiengine.syslog': {
            'Meta': {'object_name': 'Syslog'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'table_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'table_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'})
        },
        u'yabiengine.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'yabiengine.task': {
            'Meta': {'object_name': 'Task'},
            'command': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'envvars_json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'error_msg': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_retrying': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Job']"}),
            'job_identifier': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'percent_complete': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'remote_info': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'retry_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_aborted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_blocked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_cleaning': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_complete': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_error': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_active': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_cleanup': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_done': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_error': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_pending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_running': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_exec_unsubmitted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_mkdir': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_pending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_ready': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_requested': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_stagein': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status_stageout': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'task_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'working_dir': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'yabiengine.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'abort_requested_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aborted_workflows'", 'null': 'True', 'to': u"orm['yabi.User']"}),
            'abort_requested_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'original_json': ('django.db.models.fields.TextField', [], {}),
            'stageout': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'max_length': '64', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabi.User']"})
        },
        u'yabiengine.workflowtag': {
            'Meta': {'object_name': 'WorkflowTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Tag']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['yabiengine.Workflow']"})
        }
    }

    complete_apps = ['yabiengine']
    symmetrical = True
