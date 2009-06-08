from django.conf.urls.defaults import *
from django.contrib import admin
from yabiadmin.yabmin import admin as yabmin

import os
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^ws/', include('yabiadmin.yabmin.wsurls')),
    (r'^admin/', include('yabiadmin.yabmin.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^static/(?P<path>.*)$',
                        'django.views.static.serve', 
                        {'document_root': os.path.join(os.path.dirname(__file__),"static"), 'show_indexes': True}),
)
