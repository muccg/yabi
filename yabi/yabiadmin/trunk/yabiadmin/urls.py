from django.conf.urls.defaults import *
from django.contrib import admin
from yabiadmin.yabmin import admin as yabmin

#admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include('yabiadmin.yabmin.urls')),
    (r'^admin/(.*)', admin.site.root),
)
