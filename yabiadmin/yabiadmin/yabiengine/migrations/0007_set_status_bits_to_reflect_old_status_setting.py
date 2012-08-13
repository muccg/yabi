# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

STATUS_PROGRESS_MAP = {
    'pending':0.0,
    'ready':0.0,
    'requested':0.01,
    'stagein':0.05,
    'mkdir':0.1,
    'exec':0.11,
    'exec:unsubmitted':0.12,
    'exec:pending':0.13,
    'exec:active':0.2,
    'exec:running':0.2,
    'exec:cleanup':0.7,
    'exec:done':0.75,
    #'exec:error':0.0,                      # handle errors separately in the migration
    'stageout':0.8,
    'cleaning':0.9,
    'complete':1.0,
    #'error':0.0,                           # handle errors separately in the migration
    }

STATUS_PROGRESS_ORDER = STATUS_PROGRESS_MAP.keys()
STATUS_PROGRESS_ORDER.sort(cmp=lambda a,b: int( (STATUS_PROGRESS_MAP[a]-STATUS_PROGRESS_MAP[b])*100.) )

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for task in orm.Task.objects.all():
            print "processing task:",task.id,'...',
            task_status = task.status
            
            if task.status:
                if 'error' not in task_status and 'blocked' not in task_status and 'resume' not in task_status:
                    #normal status
                    statuses = STATUS_PROGRESS_ORDER[:STATUS_PROGRESS_ORDER.index(task_status)+1]
                    timestamps = {}
                    
                    if len(statuses):
                        # set the first time stamp to start time if there is one
                        timestamps[ statuses[0] ] = task.start_time or datetime.datetime.now()
                    
                    if len(statuses)>1:
                        # set the last time stamp to end time if there is one
                        timestamps[ statuses[-1] ] = task.end_time or datetime.datetime.now()
                        
                    if len(statuses)>2:
                        if task.end_time:
                            # fill in the intermediate points with an even distribution of fake timestamps
                            delta = (task.end_time - task.start_time)/(len(statuses)-1)
                        else:
                            delta = datetime.timedelta(seconds=1.0)
                        
                        print 'spreading status timestamps using delta %s'%(str(delta))
                        
                        # fill in the times
                        t = timestamps[ statuses[0] ]
                        for key in statuses[1:-1]:
                            t+=delta
                            timestamps[ key ] = t
                    else:
                        print 'setting start/stop times'
                        
                    for prestat in statuses:
                        # mark this status boolean with now.
                        varname = "status_"+prestat.replace(':','_')
                        setattr(task,varname,timestamps[ prestat ])
                elif 'error' in task_status:
                    # handle errors... we just mark the error state (cause we don't actually know how we came to this error)
                    print "setting error time"
                    task.status_error = task.end_time
                else:
                    # handle blocked tasks
                    print "setting blocked time"
                    task.status_blocked = task.start_time       # just use start time for simplicity
                    
                # save the task
                task.save()
                    
    def backwards(self, orm):
        "Write your backwards methods here."
        # find the most recent datetimed status, and set the status to that
        raise Exception("cannot migrate backwards")
            

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
            'submission': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tasks_per_user': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'expires_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credential_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.User']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'yabi.user': {
            'Meta': {'ordering': "('name',)", 'object_name': 'User'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_creators'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credential_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_modifiers'", 'null': 'True', 'to': "orm['auth.User']"}),
            'last_modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'user_option_access': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
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
            'execution_backend_credential': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabi.BackendCredential']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabiengine.Job']"}),
            'job_identifier': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'percent_complete': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'remote_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'remote_info': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
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
            'tasktag': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'working_dir': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'yabiengine.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
