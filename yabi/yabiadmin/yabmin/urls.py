from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^user/(?P<user_id>\d+)/tools/$', 'yabiadmin.yabmin.views.tools', name='user_tools_view'),
)
