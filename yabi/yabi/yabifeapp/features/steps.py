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
from lettuce import step, world
import lettuce_webdriver.webdriver


@step('I go to "(.*)"')
def our_goto(step, relative_url):
    """
    NB. This allows tests to run in different contexts ( locally, staging.)
    We delegate to the library supplied version of the step with the same pattern after fixing the path
    """
    absolute_url = "%s/%s" % (world.site_url.rstrip('/'), relative_url.lstrip('/'))
    lettuce_webdriver.webdriver.goto(step, absolute_url)


@step('I should see "(.*)"')
def eventually(step, expected_string):
    number_of_seconds_to_wait = getattr(world, "wait_seconds", 10)
    lettuce_webdriver.webdriver.should_see_in_seconds(step, expected_string, number_of_seconds_to_wait)


@step('I log in as "(.*)" with "(.*)" password')
def login_as_user(step, username, password):
    username_field = world.browser.find_element_by_xpath('.//input[@name="username"]')
    username_field.send_keys(username)
    password_field = world.browser.find_element_by_xpath('.//input[@name="password"]')
    password_field.send_keys(password)
    password_field.submit()


def get_site_url(app_name, default_url):
    """
    :return: http://example.com:8081
    """
    return os.environ.get('YABIURL', default_url)
