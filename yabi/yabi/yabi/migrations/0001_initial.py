# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FileExtension'
        db.create_table('yabi_fileextension', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fileextension_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fileextension_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('pattern', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
        ))
        db.send_create_signal('yabi', ['FileExtension'])

        # Adding model 'FileType'
        db.create_table('yabi_filetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='filetype_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='filetype_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('yabi', ['FileType'])

        # Adding M2M table for field extensions on 'FileType'
        db.create_table('yabi_filetype_extensions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filetype', models.ForeignKey(orm['yabi.filetype'], null=False)),
            ('fileextension', models.ForeignKey(orm['yabi.fileextension'], null=False))
        ))
        db.create_unique('yabi_filetype_extensions', ['filetype_id', 'fileextension_id'])

        # Adding model 'Tool'
        db.create_table('yabi_tool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tool_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tool_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('backend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.Backend'])),
            ('fs_backend', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fs_backends', to=orm['yabi.Backend'])),
            ('accepts_input', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cpus', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('walltime', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('module', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('queue', self.gf('django.db.models.fields.CharField')(default='normal', max_length=50, null=True, blank=True)),
            ('max_memory', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('job_type', self.gf('django.db.models.fields.CharField')(default='single', max_length=40, null=True, blank=True)),
            ('lcopy_supported', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('link_supported', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('yabi', ['Tool'])

        # Adding model 'ParameterSwitchUse'
        db.create_table('yabi_parameterswitchuse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parameterswitchuse_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parameterswitchuse_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('display_text', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('formatstring', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('yabi', ['ParameterSwitchUse'])

        # Adding model 'ToolParameter'
        db.create_table('yabi_toolparameter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolparameter_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolparameter_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.Tool'])),
            ('switch', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('switch_use', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.ParameterSwitchUse'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('mandatory', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('output_file', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('extension_param', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.FileExtension'], null=True, blank=True)),
            ('possible_values', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('default_value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('helptext', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('batch_bundle_files', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('file_assignment', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('use_output_filename', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.ToolParameter'], null=True, blank=True)),
        ))
        db.send_create_signal('yabi', ['ToolParameter'])

        # Adding M2M table for field accepted_filetypes on 'ToolParameter'
        db.create_table('yabi_toolparameter_accepted_filetypes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('toolparameter', models.ForeignKey(orm['yabi.toolparameter'], null=False)),
            ('filetype', models.ForeignKey(orm['yabi.filetype'], null=False))
        ))
        db.create_unique('yabi_toolparameter_accepted_filetypes', ['toolparameter_id', 'filetype_id'])

        # Adding model 'ToolOutputExtension'
        db.create_table('yabi_tooloutputextension', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tooloutputextension_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tooloutputextension_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.Tool'])),
            ('file_extension', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.FileExtension'])),
            ('must_exist', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('must_be_larger_than', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('yabi', ['ToolOutputExtension'])

        # Adding model 'ToolGroup'
        db.create_table('yabi_toolgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolgroup_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolgroup_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('yabi', ['ToolGroup'])

        # Adding model 'ToolGrouping'
        db.create_table('yabi_toolgrouping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolgrouping_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolgrouping_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.Tool'])),
            ('tool_set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.ToolSet'])),
            ('tool_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.ToolGroup'])),
        ))
        db.send_create_signal('yabi', ['ToolGrouping'])

        # Adding model 'ToolSet'
        db.create_table('yabi_toolset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolset_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='toolset_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('yabi', ['ToolSet'])

        # Adding M2M table for field users on 'ToolSet'
        db.create_table('yabi_user_toolsets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('toolset', models.ForeignKey(orm['yabi.toolset'], null=False)),
            ('user', models.ForeignKey(orm['yabi.user'], null=False))
        ))
        db.create_unique('yabi_user_toolsets', ['toolset_id', 'user_id'])

        # Adding model 'User'
        db.create_table('yabi_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('yabi', ['User'])

        # Adding model 'Credential'
        db.create_table('yabi_credential', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='credential_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='credential_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('cert', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('key', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.User'])),
            ('expires_on', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('encrypted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('encrypt_on_login', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('yabi', ['Credential'])

        # Adding model 'Backend'
        db.create_table('yabi_backend', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backend_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backend_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('scheme', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('port', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('max_connections', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lcopy_supported', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('link_supported', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('submission', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('yabi', ['Backend'])

        # Adding model 'BackendCredential'
        db.create_table('yabi_backendcredential', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backendcredential_modifiers', null=True, to=orm['auth.User'])),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backendcredential_creators', null=True, to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('backend', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.Backend'])),
            ('credential', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.Credential'])),
            ('homedir', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('default_stageout', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submission', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('yabi', ['BackendCredential'])

        # Adding model 'UserProfile'
        db.create_table('yabi_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('yabi', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'FileExtension'
        db.delete_table('yabi_fileextension')

        # Deleting model 'FileType'
        db.delete_table('yabi_filetype')

        # Removing M2M table for field extensions on 'FileType'
        db.delete_table('yabi_filetype_extensions')

        # Deleting model 'Tool'
        db.delete_table('yabi_tool')

        # Deleting model 'ParameterSwitchUse'
        db.delete_table('yabi_parameterswitchuse')

        # Deleting model 'ToolParameter'
        db.delete_table('yabi_toolparameter')

        # Removing M2M table for field accepted_filetypes on 'ToolParameter'
        db.delete_table('yabi_toolparameter_accepted_filetypes')

        # Deleting model 'ToolOutputExtension'
        db.delete_table('yabi_tooloutputextension')

        # Deleting model 'ToolGroup'
        db.delete_table('yabi_toolgroup')

        # Deleting model 'ToolGrouping'
        db.delete_table('yabi_toolgrouping')

        # Deleting model 'ToolSet'
        db.delete_table('yabi_toolset')

        # Removing M2M table for field users on 'ToolSet'
        db.delete_table('yabi_user_toolsets')

        # Deleting model 'User'
        db.delete_table('yabi_user')

        # Deleting model 'Credential'
        db.delete_table('yabi_credential')

        # Deleting model 'Backend'
        db.delete_table('yabi_backend')

        # Deleting model 'BackendCredential'
        db.delete_table('yabi_backendcredential')

        # Deleting model 'UserProfile'
        db.delete_table('yabi_userprofile')


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
