from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabmin.adminviews',
    url(r'^user/(?P<user_id>\d+)/tools/$', 'user_tools', name='user_tools_view'),
    url(r'^tool/(?P<tool_id>\d+)/$', 'tool', name='tool_view'),
    url(r'^backend/(?P<backend_id>\d+)/$', 'backend', name='backend_view'),
    url(r'^backend_test_cred/(?P<backend_cred_id>\d+)/$', 'backend_test_cred', name='backend_test_cred_view'),                       
    url(r'^ldap_users/$', 'ldap_users', name='ldap_users_view'),
)
