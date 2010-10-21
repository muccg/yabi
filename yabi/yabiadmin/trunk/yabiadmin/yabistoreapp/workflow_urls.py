from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabistoreapp.workflow_views',

    (r'^[/]*$', 'workflows_for_user'),
    (r'^(?P<workflow_id>\d+)[/]*$', 'get_add_or_update_workflow'),
    (r'^datesearch[/]*$', 'workflow_date_search'),

    (r'^(?P<id>\d+)/tags[/]*$', 'workflow_id_tags'),
)
