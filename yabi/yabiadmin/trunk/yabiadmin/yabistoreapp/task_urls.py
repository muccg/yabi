from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabistoreapp.task_views',

    (r'^(?P<username>\w+)[/]*$', 'task'),
    (r'^(?P<username>\w+)/(?P<id>\d+)[/]*$', 'task_id'),
                       
)
