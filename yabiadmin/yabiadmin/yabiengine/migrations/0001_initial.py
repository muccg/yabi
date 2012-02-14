# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Workflow'
        db.create_table('yabiengine_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabi.User'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('last_modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('status', self.gf('django.db.models.fields.TextField')(max_length=64, blank=True)),
            ('stageout', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('json', self.gf('django.db.models.fields.TextField')()),
            ('original_json', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('yabiengine', ['Workflow'])

        # Adding model 'Tag'
        db.create_table('yabiengine_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('yabiengine', ['Tag'])

        # Adding model 'WorkflowTag'
        db.create_table('yabiengine_workflowtag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabiengine.Workflow'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabiengine.Tag'])),
        ))
        db.send_create_signal('yabiengine', ['WorkflowTag'])

        # Adding model 'Job'
        db.create_table('yabiengine_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabiengine.Workflow'])),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('cpus', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('walltime', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('module', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('queue', self.gf('django.db.models.fields.CharField')(default='normal', max_length=50, null=True, blank=True)),
            ('max_memory', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('job_type', self.gf('django.db.models.fields.CharField')(default='single', max_length=40, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('exec_backend', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('fs_backend', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('command', self.gf('django.db.models.fields.TextField')()),
            ('command_template', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('stageout', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('preferred_stagein_method', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('preferred_stageout_method', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('yabiengine', ['Job'])

        # Adding model 'Task'
        db.create_table('yabiengine_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabiengine.Job'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('job_identifier', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('command', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('exec_backend', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('fs_backend', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('error_msg', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('percent_complete', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('remote_id', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('remote_info', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('working_dir', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('tasktag', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('yabiengine', ['Task'])

        # Adding model 'StageIn'
        db.create_table('yabiengine_stagein', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('src', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('dst', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabiengine.Task'])),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('yabiengine', ['StageIn'])

        # Adding model 'QueuedWorkflow'
        db.create_table('yabiengine_queuedworkflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabiengine.Workflow'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('yabiengine', ['QueuedWorkflow'])

        # Adding model 'Syslog'
        db.create_table('yabiengine_syslog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('table_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('table_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal('yabiengine', ['Syslog'])


    def backwards(self, orm):
        
        # Deleting model 'Workflow'
        db.delete_table('yabiengine_workflow')

        # Deleting model 'Tag'
        db.delete_table('yabiengine_tag')

        # Deleting model 'WorkflowTag'
        db.delete_table('yabiengine_workflowtag')

        # Deleting model 'Job'
        db.delete_table('yabiengine_job')

        # Deleting model 'Task'
        db.delete_table('yabiengine_task')

        # Deleting model 'StageIn'
        db.delete_table('yabiengine_stagein')

        # Deleting model 'QueuedWorkflow'
        db.delete_table('yabiengine_queuedworkflow')

        # Deleting model 'Syslog'
        db.delete_table('yabiengine_syslog')


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
        'yabi.user': {
            'Meta': {'object_name': 'User'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'yabiengine.job': {
            'Meta': {'object_name': 'Job'},
            'command': ('django.db.models.fields.TextField', [], {}),
            'command_template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cpus': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'exec_backend': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'fs_backend': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'walltime': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Workflow']"})
        },
        'yabiengine.queuedworkflow': {
            'Meta': {'object_name': 'QueuedWorkflow'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Workflow']"})
        },
        'yabiengine.stagein': {
            'Meta': {'object_name': 'StageIn'},
            'dst': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'src': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Task']"})
        },
        'yabiengine.syslog': {
            'Meta': {'object_name': 'Syslog'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'table_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'table_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'})
        },
        'yabiengine.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'yabiengine.task': {
            'Meta': {'object_name': 'Task'},
            'command': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'error_msg': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'exec_backend': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'fs_backend': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Job']"}),
            'job_identifier': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'percent_complete': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'remote_info': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'tasktag': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'working_dir': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'yabiengine.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('django.db.models.fields.TextField', [], {}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'original_json': ('django.db.models.fields.TextField', [], {}),
            'stageout': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.TextField', [], {'max_length': '64', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.User']"})
        },
        'yabiengine.workflowtag': {
            'Meta': {'object_name': 'WorkflowTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Tag']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Workflow']"})
        }
    }

    complete_apps = ['yabiengine']
