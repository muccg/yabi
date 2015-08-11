# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yabi.yabiengine.models


class Migration(migrations.Migration):

    dependencies = [
        ('yabi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicBackendInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('configuration', models.TextField()),
                ('instance_handle', models.CharField(max_length=256)),
                ('hostname', models.CharField(max_length=512, blank=True)),
                ('destroyed_on', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True)),
                ('cpus', models.CharField(max_length=64, null=True, blank=True)),
                ('walltime', models.CharField(max_length=64, null=True, blank=True)),
                ('module', models.TextField(null=True, blank=True)),
                ('queue', models.CharField(default=b'normal', max_length=50, null=True, blank=True)),
                ('max_memory', models.CharField(max_length=64, null=True, blank=True)),
                ('job_type', models.CharField(default=b'single', max_length=40, null=True, blank=True)),
                ('status', models.CharField(max_length=64, blank=True)),
                ('exec_backend', models.CharField(max_length=256)),
                ('fs_backend', models.CharField(max_length=256)),
                ('task_total', models.IntegerField(null=True, blank=True)),
                ('command', models.TextField()),
                ('command_template', models.TextField(null=True, blank=True)),
                ('stageout', models.CharField(max_length=1000, null=True)),
                ('preferred_stagein_method', models.CharField(max_length=5, choices=[(b'copy', b'remote copy'), (b'lcopy', b'local copy'), (b'link', b'symbolic link')])),
                ('preferred_stageout_method', models.CharField(max_length=5, choices=[(b'copy', b'remote copy'), (b'lcopy', b'local copy'), (b'link', b'symbolic link')])),
            ],
            bases=(models.Model, yabi.yabiengine.models.Editable, yabi.yabiengine.models.Status),
        ),
        migrations.CreateModel(
            name='JobDynamicBackend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('be_type', models.CharField(max_length=2, choices=[(b'fs', b'filesystem'), (b'ex', b'execution')])),
                ('backend', models.ForeignKey(to='yabi.Backend')),
                ('instance', models.ForeignKey(to='yabiengine.DynamicBackendInstance')),
                ('job', models.ForeignKey(to='yabiengine.Job')),
            ],
        ),
        migrations.CreateModel(
            name='SavedWorkflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('json', models.TextField()),
                ('creator', models.ForeignKey(to='yabi.User')),
            ],
            options={
                'get_latest_by': 'created_on',
            },
            bases=(models.Model, yabi.yabiengine.models.Editable),
        ),
        migrations.CreateModel(
            name='StageIn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('src', models.CharField(max_length=256)),
                ('dst', models.CharField(max_length=256)),
                ('order', models.IntegerField()),
                ('method', models.CharField(max_length=5, choices=[(b'copy', b'remote copy'), (b'lcopy', b'local copy'), (b'link', b'symbolic link')])),
            ],
            bases=(models.Model, yabi.yabiengine.models.Editable),
        ),
        migrations.CreateModel(
            name='Syslog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(blank=True)),
                ('table_name', models.CharField(max_length=64, null=True)),
                ('table_id', models.IntegerField(null=True)),
                ('created_on', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('job_identifier', models.TextField(blank=True)),
                ('command', models.TextField(blank=True)),
                ('error_msg', models.CharField(max_length=1000, null=True, blank=True)),
                ('is_retrying', models.BooleanField(default=False)),
                ('retry_count', models.IntegerField(default=0)),
                ('task_num', models.IntegerField(null=True, blank=True)),
                ('status_pending', models.DateTimeField(null=True, blank=True)),
                ('status_ready', models.DateTimeField(null=True, blank=True)),
                ('status_requested', models.DateTimeField(null=True, blank=True)),
                ('status_stagein', models.DateTimeField(null=True, blank=True)),
                ('status_mkdir', models.DateTimeField(null=True, blank=True)),
                ('status_exec', models.DateTimeField(null=True, blank=True)),
                ('status_exec_unsubmitted', models.DateTimeField(null=True, blank=True)),
                ('status_exec_pending', models.DateTimeField(null=True, blank=True)),
                ('status_exec_active', models.DateTimeField(null=True, blank=True)),
                ('status_exec_running', models.DateTimeField(null=True, blank=True)),
                ('status_exec_cleanup', models.DateTimeField(null=True, blank=True)),
                ('status_exec_done', models.DateTimeField(null=True, blank=True)),
                ('status_exec_error', models.DateTimeField(null=True, blank=True)),
                ('status_stageout', models.DateTimeField(null=True, blank=True)),
                ('status_cleaning', models.DateTimeField(null=True, blank=True)),
                ('status_complete', models.DateTimeField(null=True, blank=True)),
                ('status_error', models.DateTimeField(null=True, blank=True)),
                ('status_aborted', models.DateTimeField(null=True, blank=True)),
                ('status_blocked', models.DateTimeField(null=True, blank=True)),
                ('percent_complete', models.FloatField(null=True, blank=True)),
                ('remote_id', models.CharField(max_length=256, null=True, blank=True)),
                ('remote_info', models.CharField(max_length=2048, null=True, blank=True)),
                ('working_dir', models.CharField(max_length=256, null=True, blank=True)),
                ('name', models.CharField(max_length=256, null=True, blank=True)),
                ('envvars_json', models.TextField(blank=True)),
                ('job', models.ForeignKey(to='yabiengine.Job')),
            ],
            bases=(models.Model, yabi.yabiengine.models.Editable, yabi.yabiengine.models.Status),
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('status', models.TextField(max_length=64, blank=True)),
                ('abort_requested_on', models.DateTimeField(null=True)),
                ('stageout', models.CharField(max_length=1000)),
                ('shared', models.BooleanField(default=False)),
                ('original_json', models.TextField()),
                ('abort_requested_by', models.ForeignKey(related_name='aborted_workflows', to='yabi.User', null=True)),
                ('user', models.ForeignKey(to='yabi.User')),
            ],
            options={
                'get_latest_by': 'created_on',
            },
            bases=(models.Model, yabi.yabiengine.models.Editable, yabi.yabiengine.models.Status),
        ),
        migrations.CreateModel(
            name='WorkflowTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.ForeignKey(to='yabiengine.Tag')),
                ('workflow', models.ForeignKey(to='yabiengine.Workflow')),
            ],
        ),
        migrations.AddField(
            model_name='stagein',
            name='task',
            field=models.ForeignKey(to='yabiengine.Task'),
        ),
        migrations.AddField(
            model_name='job',
            name='dynamic_backends',
            field=models.ManyToManyField(to='yabiengine.DynamicBackendInstance', through='yabiengine.JobDynamicBackend', blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='tool',
            field=models.ForeignKey(to='yabi.Tool', null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='workflow',
            field=models.ForeignKey(to='yabiengine.Workflow'),
        ),
        migrations.AddField(
            model_name='dynamicbackendinstance',
            name='created_for_job',
            field=models.ForeignKey(to='yabiengine.Job'),
        ),
        migrations.CreateModel(
            name='EngineJob',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('yabiengine.job',),
        ),
        migrations.CreateModel(
            name='EngineTask',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('yabiengine.task',),
        ),
        migrations.CreateModel(
            name='EngineWorkflow',
            fields=[
            ],
            options={
                'verbose_name': 'workflow',
                'proxy': True,
                'verbose_name_plural': 'workflows',
            },
            bases=('yabiengine.workflow',),
        ),
    ]
