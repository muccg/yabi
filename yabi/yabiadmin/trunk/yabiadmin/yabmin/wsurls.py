from django.conf.urls.defaults import *

# frontend webservices
urlpatterns = patterns('yabiadmin.yabmin.wsviews',
    url(r'^tool/(?P<toolname>[\w.-]+)[/]*$', 'tool', name='tool'),
    url(r'^menu/(?P<username>\w+)[/]*$', 'menu', name='menu'),
    url(r'^fs/list[/]*$', 'ls', name='ls'),                       
    url(r'^submitworkflow[/]*$', 'submitworkflow', name='submitworkflow')
)

# backend webservices
urlpatterns += patterns('yabiadmin.yabmin.ws_backend_views',
    url(r'^credential/(?P<username>\w+)/(?P<backend>\w+)[/]*$', 'credential', name='credential'),
    url(r'^credential/(?P<username>\w+)/(?P<backend>\w+)/(?P<detail>\w+)[/]*$', 'credential_detail', name='credential_detail'),                       
)
