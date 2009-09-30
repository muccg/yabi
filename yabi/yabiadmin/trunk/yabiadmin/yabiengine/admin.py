from yabiadmin.yabiengine.models import *

from django.contrib import admin

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name']

class QueuedWorkflowAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'created_on']

class SyslogAdmin(admin.ModelAdmin):
    list_display = ['message', 'table_name', 'table_id', 'created_on']
    search_fields = ['table_name', 'table_id']


## def link_to_tasks(obj):
##     return '<a href="%s?job__workflow__exact=%d">%s</a>' % (url('/admin/yabiengine/task/'), obj.id, "Tasks")
## link_to_tasks.allow_tags = True
## link_to_tasks.short_description = "Tasks"


class JobAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'command', 'commandparams', 'start_time', 'end_time', 'cpus', 'walltime', 'stageout']
    list_filter = ['workflow']




class TaskAdmin(admin.ModelAdmin):
    list_display = ['status', 'job', 'start_time', 'end_time', 'job_identifier', 'command', 'error_msg']
    list_filter = ['job__workflow']
    
class StageInAdmin(admin.ModelAdmin):
    list_display = ['src', 'dst', 'order', 'task']



admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(QueuedWorkflow, QueuedWorkflowAdmin)
admin.site.register(Syslog, SyslogAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(StageIn, StageInAdmin)
