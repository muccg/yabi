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

from django.contrib import admin, messages
from django.core import urlresolvers

from ccg_django_utils.webhelpers import url

from yabi.yabi.models import User
from yabi.yabiengine.models import DynamicBackendInstance, Job, StageIn, SavedWorkflow, Syslog, Task
from yabi.yabiengine.enginemodels import EngineWorkflow
from yabi.backend.celerytasks import request_workflow_abort


def link_to_jobs(obj):
    return '<a href="%s?workflow__exact=%d">%s</a>' % (url('/admin-pane/yabiengine/job/'), obj.workflowid, "Jobs")
link_to_jobs.allow_tags = True
link_to_jobs.short_description = "Jobs"


def link_to_tasks(obj):
    return '<a href="%s?job__workflow__exact=%d">%s</a>' % (url('/admin-pane/yabiengine/task/'), obj.workflowid, "Tasks")
link_to_tasks.allow_tags = True
link_to_tasks.short_description = "Tasks"


def link_to_tasks_from_job(obj):
    return '<a href="%s?job__workflow__exact=%d&job__exact=%d">%s</a>' % (url('/admin-pane/yabiengine/task/'), obj.workflowid, obj.id, "Tasks")
link_to_tasks_from_job.allow_tags = True
link_to_tasks_from_job.short_description = "Tasks"


def link_to_stageins(obj):
    return '<a href="%s?task__job__workflow__exact=%d">%s</a>' % (url('/admin-pane/yabiengine/stagein/'), obj.workflowid, "Stageins")
link_to_stageins.allow_tags = True
link_to_stageins.short_description = "Stageins"


def link_to_stageins_from_task(obj):
    return '<a href="%s?task__job__workflow__exact=%d&task__exact=%d">%s</a>' % (url('/admin-pane/yabiengine/stagein/'), obj.workflowid, obj.id, "Stageins")
link_to_stageins_from_task.allow_tags = True
link_to_stageins_from_task.short_description = "Stageins"


def link_to_syslog_from_task(obj):
    return '<a href="%s?table_name=task&table_id=%d">%s</a>' % (url('/admin-pane/yabiengine/syslog/'), obj.id, "Syslog")
link_to_syslog_from_task.allow_tags = True
link_to_syslog_from_task.short_description = "Syslog"


class BaseModelAdmin(admin.ModelAdmin):
    """
    Allows for whitelisting filters to be passed in via query string
    See: http://www.hoboes.com/Mimsy/hacks/fixing-django-124s-suspiciousoperation-filtering/
    """
    valid_lookups = ()

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup.startswith(self.valid_lookups):
            return True
        return super(BaseModelAdmin, self).lookup_allowed(lookup, *args, **kwargs)


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['summary_link', 'status', 'stageout', 'change_link', link_to_jobs, link_to_tasks, link_to_stageins, 'shared', 'is_aborting', 'highest_retry_count']
    list_filter = ['status', 'user']
    search_fields = ['name']
    actions = ['abort_workflow']
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'shared', 'start_time', 'end_time', 'status', 'stageout')
        }),
    )

    def summary_link(self, workflow):
        return '<a href="%s">%s</a>' % (workflow.summary_url(), workflow.name)
    summary_link.short_description = 'Summary'
    summary_link.allow_tags = True

    def change_link(self, workflow):
        change_url = urlresolvers.reverse('admin:yabiengine_engineworkflow_change', args=(workflow.id,))
        return '<a href="%s">Change</a>' % change_url
    change_link.short_description = 'Change'
    change_link.allow_tags = True

    def abort_workflow(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        counter = 0
        for id in selected:
            yabiuser = User.objects.get(name=request.user.username)
            if request_workflow_abort(id, yabiuser):
                counter += 1

        if counter == 1:
            message_bit = "1 workflow was requested to abort."
        else:
            message_bit = "%s workflows were requested to abort." % counter
        messages.success(request, message_bit)

    abort_workflow.short_description = "Abort selected Workflows."


class SyslogAdmin(admin.ModelAdmin):
    list_display = ['message', 'table_name', 'table_id', 'created_on']
    search_fields = ['table_name', 'table_id']


class JobAdmin(admin.ModelAdmin):

    def workflow_name(obj):
        return obj.workflow.name

    list_display = [workflow_name, 'order', 'status', 'command', 'start_time', 'end_time', 'cpus', 'walltime', link_to_tasks_from_job]
    ordering = ['order']
    fieldsets = (
        (None, {
            'fields': ('workflow', 'order', 'start_time', 'cpus', 'walltime', 'module', 'queue', 'max_memory', 'job_type', 'status', 'exec_backend', 'fs_backend', 'command', 'stageout', 'preferred_stagein_method', 'preferred_stageout_method', 'task_total')
        }),
    )
    raw_id_fields = ['workflow']


class TaskAdmin(BaseModelAdmin):
    valid_lookups = ('job__workflow__exact',)

    def workflow(task):
        workflow = task.job.workflow
        return '<a href="/admin-pane/yabiengine/engineworkflow/%s">%s</a>' % (workflow.pk, workflow.name)
    workflow.allow_tags = True

    list_display = ['id', workflow, 'start_time', 'end_time', 'job_identifier', 'error_msg', 'command', link_to_stageins_from_task, link_to_syslog_from_task, 'retry_count']
    list_filter = ['job__workflow__user']
    search_fields = ['id']
    raw_id_fields = ['job']
    fieldsets = (
        (None, {
            'fields': ('job', 'start_time', 'end_time', 'job_identifier', 'command', 'task_num', 'error_msg', 'retry_count')
        }),
        ('Remote Information', {
            'classes': ('collapse',),
            'fields': ('remote_id', 'remote_info', 'working_dir', 'name')
        }),
        ('Status Information', {
            'classes': ('collapse',),
            'fields': ('status_pending', 'status_ready', 'status_requested', 'status_stagein', 'status_mkdir', 'status_exec',
                       'status_exec_unsubmitted', 'status_exec_pending', 'status_exec_active', 'status_exec_running', 'status_exec_cleanup',
                       'status_exec_done', 'status_exec_error', 'status_stageout', 'status_cleaning', 'status_complete', 'status_error', 'status_aborted', 'status_blocked')
        }),
    )


class StageInAdmin(BaseModelAdmin):
    valid_lookups = ('task__job__workflow__exact',)
    list_display = ['src', 'dst', 'order', 'method']
    raw_id_fields = ['task']


class DynamicBackendInstanceAdmin(BaseModelAdmin):
    def job_link(self, dynbeinst):
        job = dynbeinst.created_for_job
        job_url = urlresolvers.reverse('admin:yabiengine_job_change', args=(job.pk,))
        return 'Created for job <a href="%s">%s</a>' % (job_url, job)
    job_link.allow_tags = True

    list_display = ['hostname', 'instance_handle', 'job_link', 'created_on', 'destroyed_on']


def register(site):
    site.register(EngineWorkflow, WorkflowAdmin)
    site.register(Syslog, SyslogAdmin)
    site.register(Job, JobAdmin)
    site.register(Task, TaskAdmin)
    site.register(StageIn, StageInAdmin)
    site.register(SavedWorkflow, BaseModelAdmin)
    site.register(DynamicBackendInstance, DynamicBackendInstanceAdmin)
