from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabiengine.views',
    (r'^task[/]*$', 'task'),
    (r'^status/(?P<model>\w+)/(?P<id>\d+)[/]*$', 'status'),
    (r'^error/(?P<table>\w+)/(?P<id>\d+)[/]*$', 'error'),
    url(r'^workflow_summary/(?P<workflow_id>\d+)/$', 'workflow_summary', name='workflow_summary'),
)
