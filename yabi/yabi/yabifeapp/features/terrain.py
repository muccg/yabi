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

from lettuce import *
from selenium import webdriver

import steps


@before.all
def set_browser():
    desired_capabilities = webdriver.DesiredCapabilities.CHROME

    world.browser = webdriver.Remote(
        desired_capabilities=desired_capabilities,
        command_executor="http://hub:4444/wd/hub"
    )


@before.all
def set_site_url():
    world.site_url = steps.get_site_url("yabi", default_url="http://web:8000")


@after.all
def clean_after_tests(result):
    world.browser.quit()


@before.each_scenario
def delete_cookies(scenario):
    # delete all cookies so when we browse to a url at the start we have to log in
    world.browser.delete_all_cookies()


# @after.each_scenario
def screenshot(scenario):
    world.browser.get_screenshot_as_file("/data/{0}-{1}.png".format(scenario.passed, scenario.name))


# Enable this only when you're running headless and need to debug things
# @after.each_step
def photo(step):
    name = str(step).replace("<", "").replace("<", "").replace('"', "") + ".png"
    world.browser.save_screenshot("after" + name)
