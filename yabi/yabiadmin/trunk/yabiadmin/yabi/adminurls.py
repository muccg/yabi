from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabi.adminviews',
    url(r'^user/(?P<user_id>\d+)/tools/$', 'user_tools', name='user_tools_view'),
    url(r'^user/(?P<user_id>\d+)/backends/$', 'user_backends', name='user_backends_view'),
    url(r'^tool/(?P<tool_id>\d+)/$', 'tool', name='tool_view'),
    url(r'^addtool/$', 'add_tool', name='add_tool_view'),
    url(r'^backend/(?P<backend_id>\d+)/$', 'backend', name='backend_view'),
    url(r'^backend_cred_test/(?P<backend_cred_id>\d+)/$', 'backend_cred_test', name='backend_cred_test_view'),                       
    url(r'^ldap_users/$', 'ldap_users', name='ldap_users_view'),
    url(r'^test_exception/$', 'test_exception', name='test_exception_view'),                       
)
