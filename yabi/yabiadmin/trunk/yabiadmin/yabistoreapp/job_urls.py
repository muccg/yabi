from django.conf.urls.defaults import *

urlpatterns = patterns('yabistore.yabistoreapp.job_views',

    (r'^(?P<username>\w+)[/]*$', 'job'),
    (r'^(?P<username>\w+)/(?P<id>\d+)[/]*$', 'job_id'),
                       
)
