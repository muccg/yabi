from django.conf.urls.defaults import *

# place app url patterns here

urlpatterns = patterns('yabiadmin.uploader.views',
    (r'^(?P<yabiusername>[a-zA-Z_][a-zA-Z0-9_\-\.]*)[/]*$', 'put'),
)
