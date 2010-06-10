from django.conf.urls.defaults import *
from django.contrib import admin

import os
admin.autodiscover()

# dispatch to either webservice, admin or general
urlpatterns = patterns('yabiadmin.yabi.views',
    (r'^(?P<url>workflows/.*)$', 'storeproxy'),
    (r'^ws/', include('yabiadmin.yabi.wsurls')),
    (r'^engine/', include('yabiadmin.yabiengine.urls')),
    (r'^admin/', include('yabiadmin.yabi.adminurls')),
    (r'^admin/', include(admin.site.urls))
)

# pattern for serving statically
# will be overridden by apache alias under WSGI
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$',
                        'django.views.static.serve', 
                        {'document_root': os.path.join(os.path.dirname(__file__),"static"), 'show_indexes': True}),
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^favicon\.ico', 'redirect_to', {'url': '/static/images/favicon.ico'}),
    )
