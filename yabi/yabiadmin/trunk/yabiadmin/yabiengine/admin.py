# -*- coding: utf-8 -*-
from yabiadmin.yabiengine.models import *

from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from yabiadmin.yabiengine import storehelper as StoreHelper


def link_to_jobs(obj):
    return '<a href="%s?workflow__exact=%d">%s</a>' % (url('/admin/yabiengine/job/'), obj.workflowid, "Jobs")
link_to_jobs.allow_tags = True
link_to_jobs.short_description = "Jobs"

def link_to_tasks(obj):
    return '<a href="%s?job__workflow__exact=%d">%s</a>' % (url('/admin/yabiengine/task/'), obj.workflowid, "Tasks")
link_to_tasks.allow_tags = True
link_to_tasks.short_description = "Tasks"

def link_to_stageins(obj):
    return '<a href="%s?task__job__workflow__exact=%d">%s</a>' % (url('/admin/yabiengine/stagein/'), obj.workflowid, "Stageins")
link_to_stageins.allow_tags = True
link_to_stageins.short_description = "Stageins"

def link_to_syslog_from_task(obj):
    return '<a href="%s?table_name=task&table_id=%d">%s</a>' % (url('/admin/yabiengine/syslog/'), obj.id, "Syslog")
link_to_syslog_from_task.allow_tags = True
link_to_syslog_from_task.short_description = "Syslog"


class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'stageout', link_to_jobs, link_to_tasks, link_to_stageins, 'summary_link']
    list_filter = ['status', 'user']
    search_fields = ['name']
    actions = ['purge_workflow']

    def purge_workflow(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        for id in selected:
            wf = Workflow.objects.get(id=id)
            StoreHelper.deleteWorkflow(wf)

        if len(selected):
            if len(selected) == 1:
                message_bit = "1 workflow purged from store."
            else:
                message_bit = "%s workflows were purged from store." % len(selected)
            self.message_user(request, message_bit)

        # pass on to delete action
        return delete_selected(self, request, queryset)

    purge_workflow.short_description = "Purge selected Workflows from Store."


class QueuedWorkflowAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'created_on']

class SyslogAdmin(admin.ModelAdmin):
    list_display = ['message', 'table_name', 'table_id', 'created_on']
    search_fields = ['table_name', 'table_id']

class JobAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'command', 'batch_files', 'start_time', 'end_time', 'cpus', 'walltime', link_to_tasks]
    list_filter = ['workflow']
    ordering = ['order']

class TaskAdmin(admin.ModelAdmin):
    list_display = ['job', 'status', 'remote_id', 'remote_info', 'start_time', 'end_time', 'job_identifier', 'command', 'error_msg', link_to_stageins, link_to_syslog_from_task]
    list_filter = ['status', 'job__workflow__user']
    #readonly_fields = ['remote_id']

    
class StageInAdmin(admin.ModelAdmin):
    list_display = ['src', 'dst', 'order']


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(QueuedWorkflow, QueuedWorkflowAdmin)
admin.site.register(Syslog, SyslogAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(StageIn, StageInAdmin)
