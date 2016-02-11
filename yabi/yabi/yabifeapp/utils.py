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

import hashlib
from django.conf import settings


def preview_key(uri):
    # The naive approach here is to use the file name encoded in such a way
    # that memcache accepts it as a key, but that turns out to be problematic,
    # as it's not uncommon for file names within YABI to be greater than the
    # 250 character limit memcache imposes on key names. As a result, we'll
    # hash the file name and accept the (extremely slight) risk of collisions.
    uri = uri.encode("utf-8")
    file_hash = hashlib.sha512(uri).hexdigest()
    return str("-preview-%s" % file_hash)


def using_dev_settings():

    using_dev_settings = False

    # these should be true in production
    for s in ['SESSION_COOKIE_SECURE', 'SESSION_COOKIE_HTTPONLY', ]:
        if getattr(settings, s) is False:
            using_dev_settings = True
            break

    # these should be false in production
    for s in ['DEBUG']:
        if getattr(settings, s) is True:
            using_dev_settings = True
            break

    # SECRET_KEY
    if settings.SECRET_KEY == 'set_this':
        using_dev_settings = True

    return using_dev_settings
