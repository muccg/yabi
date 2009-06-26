from yabiadmin.yabiengine.models import *

from django.contrib import admin

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name']

class QueuedWorkflowAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'created_on']

class SyslogAdmin(admin.ModelAdmin):
    list_display = ['message', 'table_name', 'table_id']

class JobAdmin(admin.ModelAdmin):
    list_display = ['order', 'command', 'commandparams', 'start_time', 'end_time', 'cpus', 'walltime', 'stageout']

class TaskAdmin(admin.ModelAdmin):
    list_display = ['job', 'start_time', 'end_time', 'job_identifier', 'command', 'error_msg', 'status']

class StageInAdmin(admin.ModelAdmin):
    list_display = ['src_backend', 'src_path', 'dst_backend', 'dst_path', 'order', 'task']

class StageInAdmin(admin.ModelAdmin):
    list_display = ['src_backend', 'src_path', 'dst_backend', 'dst_path', 'order', 'task']


admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(QueuedWorkflow, QueuedWorkflowAdmin)
admin.site.register(Syslog, SyslogAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(StageIn, StageInAdmin)
