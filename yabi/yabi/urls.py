# Yabi - a sophisticated online research environment for Grid, High Performance and Cloud computing.
# Copyright (C) 2015  Centre for Comparative Genomics, Murdoch University.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import *
from django.conf import settings
from django.core import urlresolvers
from django.views.generic.base import RedirectView

import admin

urlpatterns = patterns('yabi.yabifeapp.views',
                       url(r'^status_page[/]*$', 'status_page', name='status_page'),
                       (r'^preview/metadata[/]*$', 'preview_metadata'),
                       (r'^preview[/]*$', 'preview'),
                       (r'^[/]*$', 'design'),
                       (r'^account/password[/]*$', 'password'),
                       (r'^account[/]*$', 'account'),
                       (r'^design/reuse/(?P<id>.*)[/]*$', 'design'),
                       (r'^design[/]*$', 'design'),
                       (r'^jobs[/]*$', 'jobs'),
                       (r'^files[/]*$', 'files'),
                       (r'^admin[/]*$', 'admin'),
                       (r'^login[/]*$', 'login'),
                       (r'^logout[/]*$', 'logout'),
                       (r'^wslogin[/]*$', 'wslogin'),
                       (r'^wslogout[/]*$', 'wslogout'),
                       (r'^exception[/]*$', 'exception_view'))

# dispatch to either webservice, admin or general
urlpatterns += patterns('yabi.yabi.views',
                        (r'^ws/', include('yabi.yabi.wsurls')),
                        (r'^engine/', include('yabi.yabiengine.urls')),
                        url(r'^status_page[/]*$', 'status_page', name='status_page'),
                        (r'^admin-pane/', include('yabi.yabi.adminurls')),
                        (r'^admin-pane/', include(admin.site.urls)))

# redirect / to /admin
urlpatterns += patterns('',
                        ('^$', RedirectView.as_view(url=urlresolvers.reverse('admin:index'))))
# pattern for serving statically
# not needed by runserver, but it is by gunicorn
# will be overridden by apache alias under WSGI
if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': settings.STATIC_ROOT, 'show_indexes': True}))

urlpatterns += patterns('',
                        (r'^favicon\.ico', RedirectView.as_view(url='/static/images/favicon.ico')))

urlpatterns += patterns('',
                        url(r'^djamboloader/', include('djamboloader.urls')))
