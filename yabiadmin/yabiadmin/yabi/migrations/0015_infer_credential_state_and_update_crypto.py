# -*- coding: utf-8 -*-
import datetime
from itertools import combinations
from south.db import db
from south.v2 import DataMigration
from django.db import models

import logging
import six
logger = logging.getLogger(__name__)

# security_state enum values as at this migration
PLAINTEXT = 0
PROTECTED = 1
ENCRYPTED = 2

class Migration(DataMigration):

    def forwards(self, orm):
        def empty_crypt_to_empty_string(val):
            "we no longer store empty strings in annotated form"            
            if val == '$AESTEMP$$':
                return ''
            if val == '$AES$$':
                return ''
            return val

        def is_encrypted(val):
            if val is None:
                return False
            return val.startswith('$AES$')

        def is_protected(val):
            if val is None:
                return False
            return val.startswith('$AESTEMP$')

        def is_plaintext(val):
            if val is None:
                return False
            return (not is_protected(val)) and \
                (not is_encrypted(val)) and \
                (val != "")

        logger.info("Migrating credentials and inferring credential state...")
        for cred in orm.Credential.objects.all():
            import sys

            to_convert = {
                'password' : cred.password,
                'cert' : cred.cert,
                'key' : cred.key
            }

            for k in to_convert:
                to_convert[k] = empty_crypt_to_empty_string(to_convert[k])

            # infer the security state of this credential
            contains_encrypted_values = any(is_encrypted(t) for t in to_convert.values())
            contains_protected_values = any(is_protected(t) for t in to_convert.values())
            contains_plaintext_values = any(is_plaintext(t) for t in to_convert.values())

            if contains_encrypted_values:
                cred.security_state = ENCRYPTED
            elif contains_protected_values:
                cred.security_state = PROTECTED
            else:
                cred.security_state = PLAINTEXT

            # detect contradictory security state
            if (True, True) in combinations((contains_protected_values, 
                    contains_encrypted_values, 
                    contains_plaintext_values), 2):
                logger.error("Credential %s (id=%d) in inconsistent state - manual attention required" % (str(cred), cred.id))

            # special case; a credential which is empty can be called encrypted
            if all([t == '' for t in to_convert.values()]):
                cred.security_state = ENCRYPTED
            # apply conversions
            for k in to_convert:
                setattr(cred, k, to_convert[k])
            cred.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
            'tasks_per_user': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'temporary_directory': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'})
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
            'security_state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
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
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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
    symmetrical = True
