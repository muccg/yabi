# -*- coding: utf-8 -*-
### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.conf.urls.defaults import *
from yabife import admin
from django.utils.webhelpers import url as webhelper_url

urlpatterns = patterns('yabife.yabifeapp.views',
    (r'^status[/]*$', status_view, {'SSL': True}),
    (r'^(?P<url>engine/job/.*)$', 'adminproxy'),
    (r'^(?P<url>ws/account/credential.*)$', 'credentialproxy'),
    (r'^(?P<url>ws/fs/put)/(?P<session>[0-9a-f]{32})$', 'fileupload_session'),
    (r'^(?P<url>ws/fs/put.*)$', 'fileupload'),
    (r'^(?P<url>ws/tool.*)$', 'adminproxy_cache'),
    (r'^(?P<url>ws/.*)$', 'adminproxy'),
    (r'^(?P<url>workflows/.*)$', 'adminproxy'),                       
    (r'^preview/metadata[/]*$', 'preview_metadata'),
    (r'^preview[/]*$', 'preview'),
    (r'^[/]*$', 'design'),
    (r'^account/password[/]*$', 'password'),
    (r'^account[/]*$', 'account'),
    (r'^design/reuse/(?P<id>.*)[/]*$', 'design'),
    (r'^design[/]*$', 'design'),
    (r'^jobs[/]*$', 'jobs'),
    (r'^files[/]*$', 'files'),
    (r'^login[/]*$', 'login', {'SSL':True}),
    (r'^logout[/]*$', 'logout'),
    (r'^wslogin[/]*$', 'wslogin', {'SSL':True}),
    (r'^wslogout[/]*$', 'wslogout'),
    (r'^admin/', include(admin.site.urls), {'SSL': True}),
    (r'^registration/', include('yabife.registration.urls'), {'SSL': True}),
)

# pattern for serving statically
# will be overridden by apache alias under WSGI
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$',
                            'django.views.static.serve', 
                            {'document_root': os.path.join(os.path.dirname(__file__),"static"), 'show_indexes': True}),

    )

urlpatterns += patterns('django.views.generic.simple',
    (r'^favicon\.ico', 'redirect_to', {'url': webhelper_url('/static/images/favicon.ico')}),
)

handler404 = "yabife.yabifeapp.views.error_404"
handler500 = "yabife.yabifeapp.views.error_500"
