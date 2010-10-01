from yabiadmin.yabistoreapp.models import *
from django.contrib import admin

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Workflow, WorkflowAdmin)
