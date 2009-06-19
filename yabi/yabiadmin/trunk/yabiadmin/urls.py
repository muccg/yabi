from django.conf.urls.defaults import *
from django.contrib import admin
from yabiadmin.yabmin import admin as yabmin

import os
admin.autodiscover()

# dispatch to either webservice, admin or general
urlpatterns = patterns('yabiadmin.yabmin.views',
    (r'^ws/', include('yabiadmin.yabmin.wsurls')),
    (r'^engine/', include('yabiadmin.yabiengine.urls')),
    (r'^admin/', include('yabiadmin.yabmin.adminurls')),
    (r'^admin/(.*)', admin.site.root)
)

# pattern for serving statically
# will be overridden by apache alias under WSGI
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$',
                        'django.views.static.serve', 
                        {'document_root': os.path.join(os.path.dirname(__file__),"static"), 'show_indexes': True}),

)
