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

# frontend webservices
urlpatterns = patterns(
    'yabi.yabi.ws_frontend_views',
    url(r'^tool/(?P<toolid>[^/]*)[/]*$', 'tool', name='tool'),
    url(r'^tooldesc/(?P<tooldesc_id>[^/]*)[/]*$', 'tooldesc', name='tooldesc'),
    url(r'^menu[/]*$', 'menu', name='menu'),
    url(r'^menu_saved_workflows[/]*$',
        'menu_saved_workflows', name='menu_saved_workflows'),

    url(r'^fs/ls[/]*$', 'ls', name='ls'),
    url(r'^fs/get[/]*$', 'get', name='get'),
    url(r'^fs/zget[/]*$', 'zget', name='zget'),
    url(r'^fs/put[/]*$', 'put', name='put'),
    url(r'^fs/copy[/]*$', 'copy', name='copy'),
    url(r'^fs/rcopy[/]*$', 'rcopy', name='rcopy'),
    url(r'^fs/rm[/]*$', 'rm', name='rm'),
    url(r'^fs/mkdir/?$', 'mkdir', name='mkdir'),

    url(r'^workflows/submit[/]*$', 'submit_workflow'),
    url(r'^workflows/save[/]*$', 'save_workflow'),
    url(r'^workflows/delete[/]*$', 'delete_workflow'),
    url(r'^workflows/abort[/]*$', 'abort_workflow'),
    url(r'^workflows/share[/]*$', 'share_workflow'),
    url(r'^workflows/delete_saved[/]*$', 'delete_saved_workflow'),
    url(r'^workflows/get/(?P<workflow_id>\d+)[/]*$', 'get_workflow'),
    url(r'^workflows/datesearch[/]*$', 'workflow_datesearch'),
    url(r'^workflows/(?P<id>\d+)/tags[/]*$', 'workflow_change_tags'),

    url(r'^account/credential[/]*$', 'credential', name='credential'),
    url(r'^account/credential/([0-9]+)[/]*$', 'save_credential', name='save_credential'),
    url(r'^account/passchange[/]*$', 'passchange', name="passchange"),
)

# admin support pages
urlpatterns += patterns(
    'yabi.yabi.adminviews',
    url(r'^manage_credential[/]*$', 'duplicate_credential'),
    url(r'^modify_backend/id/(?P<id>\d+)[/]*$', 'modify_backend_by_id'),
    url(r'^modify_backend/name/(?P<scheme>[a-zA-Z_]*[a-zA-Z0-9_\-\.]*)/(?P<hostname>[a-zA-Z_]*[a-zA-Z0-9_\-\.]*)[/]*$', 'modify_backend_by_name'),
)

# yabish webservices
urlpatterns += patterns(
    'yabi.yabi.ws_yabish_views',
    url(r'^yabish/submitjob/?$', 'submitjob', name='submitjob'),
    url(r'^yabish/createstageindir/?$', 'createstageindir', name='createstageindir'),
    url(r'^yabish/is_stagein_required/?$', 'is_stagein_required', name='is_stagein_required'),
    url(r'^yabish/backends/?$', 'list_backends', name='list_backends'),
)
