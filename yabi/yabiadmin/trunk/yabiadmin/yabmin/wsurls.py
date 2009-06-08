from django.conf.urls.defaults import *

urlpatterns = patterns('yabiadmin.yabmin.wsviews',
#    url(r'^user/(?P<user_id>\d+)/tools/$', 'user_tools', name='user_tools_view'),
    url(r'^tool/(?P<toolname>\w+)[/]*$', 'tool', name='tool'),
    url(r'^credential/(?P<username>\w+)/(?P<backend>\w+)[/]*$', 'credential', name='credential'),
#    url(r'^ldap_users/$', 'ldap_users', name='ldap_users_view'),
)
