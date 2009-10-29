from django.conf.urls.defaults import *

# frontend webservices
urlpatterns = patterns('yabiadmin.yabmin.ws_frontend_views',
    url(r'^tool/(?P<toolname>[\w.-]+)[/]*$', 'tool', name='tool'),
    url(r'^menu/(?P<username>\w+)[/]*$', 'menu', name='menu'),
    url(r'^fs/ls[/]*$', 'ls', name='ls'),
    url(r'^fs/get[/]*$', 'get', name='get'),
    url(r'^fs/put[/]*$', 'put', name='put'),
    url(r'^submitworkflow[/]*$', 'submitworkflow', name='submitworkflow')
)

# backend webservices
urlpatterns += patterns('yabiadmin.yabmin.ws_backend_views',
    url(r'^credential/(?P<yabiusername>\w+)/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w\-.]+)[/]*$', 'credential', name='credential'),
    url(r'^credential/(?P<yabiusername>\w+)/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w\-.]+)/(?P<detail>\w+)[/]*$', 'credential_detail', name='credential_detail'),                       
)
