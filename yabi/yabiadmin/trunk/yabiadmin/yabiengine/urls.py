from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabiengine.views',
    (r'^task[/]*$', 'task')
)
