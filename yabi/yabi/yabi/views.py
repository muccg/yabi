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

import os
from django.conf import settings
from django.http import HttpResponse
from yabi.yabi.models import User

import logging
logger = logging.getLogger(__name__)


def status_page(request):
    """Availability page to be called to see if yabi is running. Should return HttpResponse with status 200"""
    logger.info('')

    # make a db connection
    User.objects.count()

    # write a file
    with open(os.path.join(settings.WRITABLE_DIRECTORY, 'status_page_testfile.txt'), 'w') as f:
        f.write("testing file write")

    # read it again
    with open(os.path.join(settings.WRITABLE_DIRECTORY, 'status_page_testfile.txt'), 'r') as f:
        contents = f.read()
        assert 'testing file write' in contents

    # delete the file
    os.unlink(os.path.join(settings.WRITABLE_DIRECTORY, 'status_page_testfile.txt'))

    return HttpResponse('Status OK')
