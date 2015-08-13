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

from django.utils.encoding import smart_str
from django.http import JsonResponse


def cache_keyname(key):
    """return a safe cache key"""
    # smart_str takes care of non-ascii characters (memcache doesn't support Unicode in keys)
    # memcache also doesn't like spaces
    return smart_str(key).replace(' ', '_').encode('string_escape')


def json_response(data):
    return JsonResponse({
        'status': 'success',
        'data': data})


def json_error_response(message, **response_kwargs):
    return JsonResponse({
        'status': 'error',
        'message': message}, **response_kwargs)
