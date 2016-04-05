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

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'yabi.yabi.adminviews',
    url(r'^user/(?P<user_id>\d+)/tools/$', 'user_tools', name='user_tools_view'),
    url(r'^user/(?P<user_id>\d+)/backends/$', 'user_backends', name='user_backends_view'),
    url(r'^tool/(?P<tool_id>\d+)/$', 'tool', name='tool_view'),
    url(r'^addtool/$', 'add_tool', name='add_tool_view'),
    url(r'^backend/(?P<backend_id>\d+)/$', 'backend', name='backend_view'),
    url(r'^backend_cred_test/(?P<backend_cred_id>\d+)/$', 'backend_cred_test', name='backend_cred_test_view'),
    url(r'^ldap_users/$', 'ldap_users', name='ldap_users_view'),
    url(r'^test_exception/$', 'test_exception', name='test_exception_view'),
    url(r'^status/$', 'status', name='status_view'),
)
