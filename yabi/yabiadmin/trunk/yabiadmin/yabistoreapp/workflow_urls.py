from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabistoreapp.workflow_views',

    (r'^[/]*$', 'workflows_for_user'),
    (r'^(?P<workflow_id>\d+)[/]*$', 'get_add_or_update_workflow'),

    # tags
    (r'^(?P<id>\d+)/tags[/]*$', 'workflow_id_tags'),
    (r'^(?P<id>\d+)/tags/add[/]*$', 'workflow_id_tags_add'),
    (r'^(?P<id>\d+)/tags/remove[/]*$', 'workflow_id_tags_remove'),
    (r'^tags/search[/]*$', 'workflow_id_tags_search'),
    (r'^tag/(?P<tag>[a-zA-Z0-9_ %\-*]+)[/]*$', 'workflow_tag'),           # all workflows for a tag
    (r'^tag[/]*$', 'workflow_all_tags'),                                  # all tags

    ## date search
    (r'^datesearch[/]*$', 'workflow_date_search'),

    ## keyword search
    (r'^search[/]*$', 'workflow_search'),
)
