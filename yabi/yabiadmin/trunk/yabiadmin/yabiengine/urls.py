# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabiengine.views',
    (r'^task[/]*$', 'task'),
    (r'^status/(?P<model>\w+)/(?P<id>\d+)[/]*$', 'status'),
    (r'^remote_id/(?P<id>\d+)[/]*$', 'remote_id'),
    (r'^remote_info/(?P<id>\d+)[/]*$', 'remote_info'),
    (r'^error/(?P<table>\w+)/(?P<id>\d+)[/]*$', 'error'),
    (r'^job/(?P<workflow>\d+)/(?P<order>\d+)[/]*$', 'job'),
    url(r'^workflow_summary/(?P<workflow_id>\d+)/$', 'workflow_summary', name='workflow_summary'),
    url(r'^task_json/(?P<task>\d+)[/]*$', 'task_json', name='task_json'),
)
