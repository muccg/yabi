# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# frontend webservices
urlpatterns = patterns('yabiadmin.yabi.ws_frontend_views',
    url(r'^tool/(?P<toolname>[^/]+)[/]*$', 'tool', name='tool'),
    url(r'^login[/]*$', 'login'),
    url(r'^logout[/]*$', 'logout'),
    url(r'^menu[/]*$', 'menu', name='menu'),
    url(r'^fs/ls[/]*$', 'ls', name='ls'),
    url(r'^fs/get[/]*$', 'get', name='get'),
    url(r'^fs/put[/]*$', 'put', {'SSL':False}, name='put'),
    url(r'^fs/copy[/]*$', 'copy', name='copy'),
    url(r'^fs/rm[/]*$', 'rm', name='rm'),
    url(r'^submitworkflow[/]*$', 'submitworkflow', name='submitworkflow'),
    url(r'^fs/getuploadurl/*$', 'getuploadurl', name='getuploadurl'),
    url(r'^account/credential[/]*$', 'credential', name='credential'),
    url(r'^account/credential/([0-9]+)[/]*$', 'save_credential', name='save_credential'),
)

# admin support pages
urlpatterns += patterns('yabiadmin.yabi.adminviews',
    url(r'^password_collection[/]*$', 'password_collection')
)

# backend webservices
# TODO this is the only backend webservice and now needs to be non-SSL where
# all the frontend ws urls are SSL. We should move this.
urlpatterns += patterns('yabiadmin.yabi.ws_backend_views',
    url(r'^credential/(?P<yabiusername>\w+)[/]*$', 'credential_uri', {'SSL':False}, name='credential_uri'),
    #url(r'^credential_deprecated/(?P<yabiusername>\w+)/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w\-.]+)/(?P<detail>\w+)[/]*$', 'credential_detail', name='credential_detail'),                       
    #url(r'^credential/(?P<yabiusername>\w+)/(?P<scheme>\w+)/(?P<username>\w+)/(?P<hostname>[\w\-.]+)[/]*$', 'credential', name='credential'),
)

# yabish webservices
urlpatterns += patterns('yabiadmin.yabi.ws_yabish_views',
    url(r'^yabish/submitjob/?$', 'submitjob', name='submitjob'),  
    url(r'^yabish/createstageindir/?$', 'createstageindir', name='createstageindir'),  
)
