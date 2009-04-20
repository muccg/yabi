from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^user/(?P<user_id>\d+)/tools/$', 'yabiadmin.yabmin.views.user_tools', name='user_tools_view'),
    url(r'^tool/(?P<tool_id>\d+)/$', 'yabiadmin.yabmin.views.tool', name='tool_view'),
)
