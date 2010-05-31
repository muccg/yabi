# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# frontend webservices
urlpatterns = patterns('yabiadmin.yabi.ws_frontend_views',
    url(r'^tool/(?P<toolname>[\w.-]+)[/]*$', 'tool', name='tool'),
    url(r'^menu/(?P<username>\w+)[/]*$', 'menu', name='menu'),
    url(r'^fs/ls[/]*$', 'ls', name='ls'),
    url(r'^fs/get[/]*$', 'get', name='get'),
    url(r'^fs/put[/]*$', 'put', name='put'),
    url(r'^fs/copy[/]*$', 'copy', name='copy'),
    url(r'^fs/rm[/]*$', 'rm', name='rm'),
    url(r'^submitworkflow[/]*$', 'submitworkflow', name='submitworkflow'),
    url(r'^fs/getuploadurl/*$', 'getuploadurl', name='getuploadurl' ),
)

# backend webservices
urlpatterns += patterns('yabiadmin.yabi.ws_backend_views',
    url(r'^credential/(?P<yabiusername>\w+)[/]*$', 'credential_uri', name='credential_uri'),
    #url(r'^credential_deprecated/(?P<yabiusername>\w+)/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w\-.]+)/(?P<detail>\w+)[/]*$', 'credential_detail', name='credential_detail'),                       
    #url(r'^credential/(?P<yabiusername>\w+)/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w\-.]+)[/]*$', 'credential', name='credential'),
)

