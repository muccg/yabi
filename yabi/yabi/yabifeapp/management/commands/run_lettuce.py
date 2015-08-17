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

from optparse import make_option

from lettuce import Runner

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Runs lettuce features'

    option_list = BaseCommand.option_list[1:] + (
        make_option('--app-name',
                    action='store',
                    dest='app_name',
                    default='yabi',
                    help='Application name'),

        make_option('--with-xunit',
                    action='store_true',
                    dest='enable_xunit',
                    default=False,
                    help='Output JUnit XML test results to a file'),

        make_option('--xunit-file',
                    action='store',
                    dest='xunit_file',
                    default=None,
                    help='Write JUnit XML to this file. Defaults to lettucetests.xml'),
    )

    def handle(self, *args, **options):
        app_name = options.get('app_name')
        if app_name:
            module = __import__(app_name)
            path = '%s/yabifeapp/features/' % os.path.dirname(module.__file__)
            print "Feature path = %s" % path
            runner = Runner(path, verbosity=options.get('verbosity'),
                            enable_xunit=options.get('enable_xunit'),
                            xunit_filename=options.get('xunit_file'),)

            runner.run()
        else:
            raise CommandError('Application name not provided')
