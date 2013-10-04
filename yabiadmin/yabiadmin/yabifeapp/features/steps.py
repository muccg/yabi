from lettuce import *
from selenium import webdriver
import lettuce_webdriver.webdriver


@step('I go to "(.*)"')
def our_goto(step, relative_url):
    """
    NB. This allows tests to run in different contexts ( locally, staging.)
    We delegate to the library supplied version of the step with the same pattern after fixing the path
    """
    absolute_url = world.site_url + relative_url
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

@step('I am on admin page')
def on_admin(step):
    javascript = """
    (function () {
        var titles = [];
        var links = document.getElementsByTagName('a');
        for (var i=0;i<links.length;i++) {
            var linkElement = links[i];
            titles.push(linkElement.getAttribute('title'));
        }
        return [1,2,4];
    })();
    """

    result = world.browser.execute_script(javascript)
    import pdb
    pdb.set_trace()


def get_site_url(app_name, default_url):
    """
    :return: http://example.com:8081
    """
    import os
    site_url_file = "/tmp/%s_site_url" % app_name
    if not os.path.exists(site_url_file):
        return default_url
    else:
        with open(site_url_file) as f:
            site_url = f.read()
        return site_url



