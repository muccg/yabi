import os
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('yabife.yabifeapp.views',
    # Example:
    # (r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),

    (r'^(?P<url>ws/.*)$', 'adminproxy'),
    (r'^(?P<url>workflows/.*)$', 'storeproxy'),                       
	(r'^[/]*$', 'design'),
	(r'^design[/]*$', 'design'),
	(r'^jobs[/]*$', 'jobs'),
    (r'^files[/]*$', 'files'),
	(r'^menu[/]*$', 'menu'),
    (r'^login[/]*$', 'login'),
    (r'^logout[/]*$', 'logout')
)


# pattern for serving statically
# will be overridden by apache alias under WSGI
urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$',
                        'django.views.static.serve', 
                        {'document_root': os.path.join(os.path.dirname(__file__),"static"), 'show_indexes': True}),

)
