from lettuce import *
from selenium import webdriver

import steps


@before.all
def set_browser():
    desired_capabilities = webdriver.DesiredCapabilities.FIREFOX

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


@after.each_scenario
def screenshot(scenario):
    world.browser.get_screenshot_as_file("/data/{0}-{1}.png".format(scenario.passed, scenario.name))


# Enable this only when you're running headless and need to debug things
# @after.each_step
def photo(step):
    name = str(step).replace("<", "").replace("<", "").replace('"', "") + ".png"
    world.browser.save_screenshot("after" + name)
