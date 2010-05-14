# -*- coding: utf-8 -*-
from yabiadmin.ghettoq.models import *
from django.contrib import admin

class QueueAdmin(admin.ModelAdmin):
    list_display = ['name']
    
class MessageAdmin(admin.ModelAdmin):
    list_display = ['visible','timestamp','payload','queue']
    filter_by = ['queue']

admin.site.register(Queue, QueueAdmin)
admin.site.register(Message, MessageAdmin)
