from django.conf.urls.defaults import *

# frontend webservices
urlpatterns = patterns('yabiadmin.yabmin.ws_frontend_views',
    url(r'^tool/(?P<toolname>[\w.-]+)[/]*$', 'tool', name='tool'),
    url(r'^menu/(?P<username>\w+)[/]*$', 'menu', name='menu'),
    url(r'^fs/list[/]*$', 'ls', name='ls'),                       
    url(r'^submitworkflow[/]*$', 'submitworkflow', name='submitworkflow')
)

# backend webservices
urlpatterns += patterns('yabiadmin.yabmin.ws_backend_views',
    url(r'^credential/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w-.]+)[/]*$', 'credential', name='credential'),
    url(r'^credential/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w-.]+)/(?P<detail>\w+)[/]*$', 'credential_detail', name='credential_detail'),                       
)
