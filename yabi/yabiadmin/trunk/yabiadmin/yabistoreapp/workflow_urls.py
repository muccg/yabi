from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabistoreapp.workflow_views',

    (r'^(?P<username>\w+)[/]*$', 'workflows_for_user'),
    (r'^(?P<username>\w+)/(?P<workflow_id>\d+)[/]*$', 'get_add_or_update_workflow'),
    (r'^delete/(?P<username>\w+)/(?P<workflow_id>\d+)[/]*$', 'delete_workflow'),

    # tags
    (r'^(?P<username>\w+)/(?P<id>\d+)/tags[/]*$', 'workflow_id_tags'),
    (r'^(?P<username>\w+)/(?P<id>\d+)/tags/add[/]*$', 'workflow_id_tags_add'),
    (r'^(?P<username>\w+)/(?P<id>\d+)/tags/remove[/]*$', 'workflow_id_tags_remove'),
    (r'^(?P<username>\w+)/tags/search[/]*$', 'workflow_id_tags_search'),
    (r'^(?P<username>\w+)/tag/(?P<tag>[a-zA-Z0-9_ %\-*]+)[/]*$', 'workflow_tag'),           # all workflows for a tag
    (r'^(?P<username>\w+)/tag[/]*$', 'workflow_all_tags'),                                  # all tags
#
#    ## date search
#    (r'^(?P<username>\w+)/datesearch[/]*$', 'workflow_date_search'),
#
#    ## keyword search
#    (r'^(?P<username>\w+)/search[/]*$', 'workflow_search'),
#
#    ## job state webservices
#    (r'^(?P<username>\w+)/status/?(P<workflow_host>[\w\d\-@]+)/?(P<workflow_id>[\w\d\-@]+)/?(P<job_id>[\w\d\-@]+)[/]*$'),
)
