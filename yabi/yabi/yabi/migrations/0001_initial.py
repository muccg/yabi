# -*- coding: utf-8 -*-
# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Backend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=512, blank=True)),
                ('scheme', models.CharField(max_length=64)),
                ('hostname', models.CharField(help_text=b'Hostname must not end with a /. For dynamic backends set to "DYNAMIC".', max_length=512)),
                ('port', models.IntegerField(null=True, blank=True)),
                ('path', models.CharField(help_text=b'Path must start and end with a /.<br/><br/>Execution backends must only have / in the path field.<br/><br/>\n    For filesystem backends, Yabi will take the value in path and combine it with any path snippet in Backend Credential to form a URI. <br/>\n    i.e. http://myserver.mydomain/home/ would be entered here and then on the Backend Credential for UserX you would enter <br/>\n    their home directory in the User Directory field i.e. UserX/. This would then combine to form a valid URI: http://myserver.mydomain/home/UserX/', max_length=512)),
                ('lcopy_supported', models.BooleanField(default=True, help_text=b"Backend supports 'cp' localised copies.")),
                ('link_supported', models.BooleanField(default=True, help_text=b"Backend supports 'ln' localised symlinking.")),
                ('submission', models.TextField(help_text=b'Mako script to be used to generate the submission script. (Variables: walltime, memory, cpus, working, modules, command, etc.)', blank=True)),
                ('tasks_per_user', models.PositiveIntegerField(help_text=b'The number of simultaneous tasks the backends should execute for each user. 0 means do not execute jobs for this backend. Blank means no limits.', null=True, blank=True)),
                ('dynamic_backend', models.BooleanField(default=False, help_text=b'Is this Backend dynamic? Dynamic backends can be created dynamically on demand. For example Amazon EC2 or LXC (Linux Containers).')),
                ('temporary_directory', models.CharField(help_text=b'Only to be set on execution backends. Temporary directory used for temporary execution scripts. Blank means "/tmp".', max_length=512, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BackendCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('homedir', models.CharField(help_text=b'This must not start with a / but must end with a /.<br/>This value will be combined with the Backend path field to create a valid URI.', max_length=512, null=True, verbose_name=b'User Directory', blank=True)),
                ('visible', models.BooleanField(default=False)),
                ('default_stageout', models.BooleanField(default=False, help_text=b'There must be only one default_stageout per yabi user.')),
                ('submission', models.TextField(help_text=b'Mako script to be used to generate a custom submission script. (Variables: walltime, memory, cpus, working, modules, command, etc.)', blank=True)),
                ('backend', models.ForeignKey(to='yabi.Backend')),
            ],
            options={
                'verbose_name_plural': 'Backend Credentials',
            },
        ),
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=512, blank=True)),
                ('security_state', models.PositiveSmallIntegerField(default=0, blank=True, choices=[(0, b'Plaintext'), (1, b'Protected with secret key'), (2, b'Encrypted with user password')])),
                ('username', models.CharField(help_text=b'The username on the backend this credential is for.', max_length=512)),
                ('password', models.CharField(help_text=b"Password for backend auth. Doesn't apply to all backends.", max_length=512, blank=True)),
                ('cert', models.TextField(help_text=b'Certificate for backend auth, if required.', blank=True)),
                ('key', models.TextField(help_text=b'Key for backend auth, if required.', blank=True)),
                ('expires_on', models.DateTimeField(null=True)),
                ('backends', models.ManyToManyField(to='yabi.Backend', through='yabi.BackendCredential', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DynamicBackendConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('configuration', models.TextField(help_text=b'JSON of the configuration dictionary to be used when creating this Dynamic Backend')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FileExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('pattern', models.CharField(unique=True, max_length=64)),
            ],
            options={
                'ordering': ('pattern',),
            },
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HostKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('hostname', models.CharField(max_length=512)),
                ('key_type', models.CharField(max_length=32)),
                ('fingerprint', models.CharField(max_length=64)),
                ('data', models.TextField(max_length=16384)),
                ('allowed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParameterSwitchUse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('display_text', models.CharField(max_length=30)),
                ('formatstring', models.CharField(help_text=b'Example: %(switch)s %(value)s', max_length=256, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('path', models.CharField(help_text=b'The path to the binary for this file. Will normally just be binary name.', max_length=512, blank=True)),
                ('display_name', models.CharField(help_text=b"Optional text visible to users. If blank, then tool definition's name is used.", max_length=255, blank=True)),
                ('enabled', models.BooleanField(default=True, help_text=b'Enable tool in frontend.')),
                ('use_same_dynamic_backend', models.BooleanField(default=True, help_text=b"If checked, and both FS and Exec Backend's are dynamic, create just one instance and use that for both FS and Exec Backends.")),
                ('cpus', models.CharField(max_length=64, null=True, blank=True)),
                ('walltime', models.CharField(max_length=64, null=True, blank=True)),
                ('module', models.TextField(help_text=b'Comma separated list of modules to load.', null=True, blank=True)),
                ('queue', models.CharField(default=b'normal', max_length=50, null=True, blank=True)),
                ('max_memory', models.CharField(max_length=64, null=True, blank=True)),
                ('job_type', models.CharField(default=b'single', max_length=40, null=True, blank=True)),
                ('submission', models.TextField(help_text=b'Mako script to be used to generate the submission script. (Variables: walltime, memory, cpus, working, modules, command, etc.)', blank=True)),
                ('lcopy_supported', models.BooleanField(default=True, help_text=b'If this tool should use local copies on supported backends where appropriate.')),
                ('link_supported', models.BooleanField(default=True, help_text=b'If this tool should use symlinks on supported backends where appropriate.')),
                ('backend', models.ForeignKey(verbose_name=b'Exec Backend', to='yabi.Backend', help_text=b'The execution backend for this tool.')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolDesc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(help_text=b'Unique tool name.', unique=True, max_length=255)),
                ('description', models.TextField(help_text=b'The description that will be sent to the frontend for the user.', null=True, blank=True)),
                ('accepts_input', models.BooleanField(default=False, help_text=b'If checked, this tool will accept inputs from prior tools rather than presenting file select widgets.')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'tool description',
            },
        ),
        migrations.CreateModel(
            name='ToolGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolGrouping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolOutputExtension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('must_exist', models.NullBooleanField(default=False)),
                ('must_be_larger_than', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('switch', models.CharField(help_text=b'The actual command line switch that should be passed to the tool i.e. -i or --input-file', max_length=64)),
                ('rank', models.IntegerField(help_text=b'The order in which the switches should appear on the command line. Leave blank if order is unimportant.', null=True, blank=True)),
                ('fe_rank', models.IntegerField(help_text=b'The order in which the switches should appear in the frontend. Leave blank if order is unimportant.', null=True, verbose_name=b'Frontend rank', blank=True)),
                ('mandatory', models.BooleanField(default=False, help_text=b'Select if the switch is required as input.')),
                ('common', models.BooleanField(default=False, help_text=b'Commonly used parameters will not hidden by default in the frontend.', verbose_name=b'Commonly used')),
                ('sensitive_data', models.BooleanField(default=False, help_text=b"Don't show the value of this field in clear text in the frontend.")),
                ('hidden', models.BooleanField(default=False, help_text=b'Select if the switch should be hidden from users in the frontend.')),
                ('output_file', models.BooleanField(default=False, help_text=b'Select if the switch is specifying an output file.')),
                ('possible_values', models.TextField(help_text=b'Json snippet for html select. See blast tool for examples.', null=True, blank=True)),
                ('default_value', models.TextField(help_text=b'Value that will appear in field. If possible values is populated this should match one of the values so the select widget defaults to that option.', null=True, blank=True)),
                ('helptext', models.TextField(help_text=b'Help text that is passed to the frontend for display to the user.', null=True, blank=True)),
                ('batch_bundle_files', models.BooleanField(default=False, help_text=b'When staging in files, stage in every file that is in the same source location as this file. Useful for bringing along other files that are associated, but not specified.')),
                ('file_assignment', models.CharField(help_text=b'Specifies how to deal with files that match the accepted filetypes setting...<br/><br/>\n        <i>No input files:</i> This parameter does not take any input files as an argument<br/>\n        <i>Single input file:</i> This parameter can only take a single input file, and batch jobs will need to be created for multiple files if the user passes them in<br/>\n        <i>Multiple input file:</i> This parameter can take a whole string of input files, one after the other. All matching filetypes will be passed into it', max_length=5, choices=[(b'none', b'No input files'), (b'batch', b'Single input file'), (b'all', b'Multiple input files')])),
                ('accepted_filetypes', models.ManyToManyField(help_text=b'The extensions of accepted filetypes for this switch.', to='yabi.FileType', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ToolSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('user_option_access', models.BooleanField(default=True)),
                ('credential_access', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(related_name='user_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', models.ForeignKey(related_name='user_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='YabiCache',
            fields=[
                ('cache_key', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('expires', models.DateTimeField(db_index=True)),
            ],
            options={
                'db_table': 'yabi_cache',
            },
        ),
        migrations.AddField(
            model_name='toolset',
            name='created_by',
            field=models.ForeignKey(related_name='toolset_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolset',
            name='last_modified_by',
            field=models.ForeignKey(related_name='toolset_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolset',
            name='users',
            field=models.ManyToManyField(related_name='users', db_table=b'yabi_user_toolsets', to='yabi.User', blank=True),
        ),
        migrations.AddField(
            model_name='toolparameter',
            name='created_by',
            field=models.ForeignKey(related_name='toolparameter_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolparameter',
            name='extension_param',
            field=models.ForeignKey(blank=True, to='yabi.FileExtension', help_text=b'If an extension is selected then this extension will be appended to the filename. This should only be set for specifying output files.', null=True),
        ),
        migrations.AddField(
            model_name='toolparameter',
            name='last_modified_by',
            field=models.ForeignKey(related_name='toolparameter_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolparameter',
            name='switch_use',
            field=models.ForeignKey(help_text=b'The way the switch should be combined with the value.', to='yabi.ParameterSwitchUse'),
        ),
        migrations.AddField(
            model_name='toolparameter',
            name='tool',
            field=models.ForeignKey(to='yabi.ToolDesc'),
        ),
        migrations.AddField(
            model_name='toolparameter',
            name='use_output_filename',
            field=models.ForeignKey(blank=True, to='yabi.ToolParameter', null=True),
        ),
        migrations.AddField(
            model_name='tooloutputextension',
            name='created_by',
            field=models.ForeignKey(related_name='tooloutputextension_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tooloutputextension',
            name='file_extension',
            field=models.ForeignKey(to='yabi.FileExtension'),
        ),
        migrations.AddField(
            model_name='tooloutputextension',
            name='last_modified_by',
            field=models.ForeignKey(related_name='tooloutputextension_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tooloutputextension',
            name='tool',
            field=models.ForeignKey(to='yabi.ToolDesc'),
        ),
        migrations.AddField(
            model_name='toolgrouping',
            name='created_by',
            field=models.ForeignKey(related_name='toolgrouping_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolgrouping',
            name='last_modified_by',
            field=models.ForeignKey(related_name='toolgrouping_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolgrouping',
            name='tool',
            field=models.ForeignKey(to='yabi.Tool'),
        ),
        migrations.AddField(
            model_name='toolgrouping',
            name='tool_group',
            field=models.ForeignKey(to='yabi.ToolGroup'),
        ),
        migrations.AddField(
            model_name='toolgrouping',
            name='tool_set',
            field=models.ForeignKey(to='yabi.ToolSet'),
        ),
        migrations.AddField(
            model_name='toolgroup',
            name='created_by',
            field=models.ForeignKey(related_name='toolgroup_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='toolgroup',
            name='last_modified_by',
            field=models.ForeignKey(related_name='toolgroup_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tooldesc',
            name='created_by',
            field=models.ForeignKey(related_name='tooldesc_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tooldesc',
            name='last_modified_by',
            field=models.ForeignKey(related_name='tooldesc_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tooldesc',
            name='output_filetypes',
            field=models.ManyToManyField(to='yabi.FileExtension', through='yabi.ToolOutputExtension', blank=True),
        ),
        migrations.AddField(
            model_name='tool',
            name='created_by',
            field=models.ForeignKey(related_name='tool_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='tool',
            name='desc',
            field=models.ForeignKey(verbose_name=b'Tool', to='yabi.ToolDesc', help_text=b'The tool definition'),
        ),
        migrations.AddField(
            model_name='tool',
            name='fs_backend',
            field=models.ForeignKey(related_name='fs_backends', verbose_name=b'FS Backend', to='yabi.Backend', help_text=b'The filesystem backend for this tool.'),
        ),
        migrations.AddField(
            model_name='tool',
            name='groups',
            field=models.ManyToManyField(to='yabi.ToolGroup', through='yabi.ToolGrouping', blank=True),
        ),
        migrations.AddField(
            model_name='tool',
            name='last_modified_by',
            field=models.ForeignKey(related_name='tool_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='parameterswitchuse',
            name='created_by',
            field=models.ForeignKey(related_name='parameterswitchuse_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='parameterswitchuse',
            name='last_modified_by',
            field=models.ForeignKey(related_name='parameterswitchuse_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='hostkey',
            name='created_by',
            field=models.ForeignKey(related_name='hostkey_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='hostkey',
            name='last_modified_by',
            field=models.ForeignKey(related_name='hostkey_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='filetype',
            name='created_by',
            field=models.ForeignKey(related_name='filetype_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='filetype',
            name='extensions',
            field=models.ManyToManyField(to='yabi.FileExtension', blank=True),
        ),
        migrations.AddField(
            model_name='filetype',
            name='last_modified_by',
            field=models.ForeignKey(related_name='filetype_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fileextension',
            name='created_by',
            field=models.ForeignKey(related_name='fileextension_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fileextension',
            name='last_modified_by',
            field=models.ForeignKey(related_name='fileextension_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='dynamicbackendconfiguration',
            name='created_by',
            field=models.ForeignKey(related_name='dynamicbackendconfiguration_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='dynamicbackendconfiguration',
            name='last_modified_by',
            field=models.ForeignKey(related_name='dynamicbackendconfiguration_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='credential',
            name='created_by',
            field=models.ForeignKey(related_name='credential_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='credential',
            name='last_modified_by',
            field=models.ForeignKey(related_name='credential_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='credential',
            name='user',
            field=models.ForeignKey(help_text=b'Yabi username.', to='yabi.User'),
        ),
        migrations.AddField(
            model_name='backendcredential',
            name='created_by',
            field=models.ForeignKey(related_name='backendcredential_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='backendcredential',
            name='credential',
            field=models.ForeignKey(to='yabi.Credential'),
        ),
        migrations.AddField(
            model_name='backendcredential',
            name='last_modified_by',
            field=models.ForeignKey(related_name='backendcredential_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='backend',
            name='created_by',
            field=models.ForeignKey(related_name='backend_creators', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='backend',
            name='dynamic_backend_configuration',
            field=models.ForeignKey(blank=True, to='yabi.DynamicBackendConfiguration', help_text=b'The configuration used to create the Dynamic Backend.Set on Dynamic Backends only!', null=True),
        ),
        migrations.AddField(
            model_name='backend',
            name='last_modified_by',
            field=models.ForeignKey(related_name='backend_modifiers', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.CreateModel(
            name='LDAPBackendUserProfile',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('yabi.user',),
        ),
        migrations.CreateModel(
            name='ModelBackendUserProfile',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('yabi.user',),
        ),
    ]
