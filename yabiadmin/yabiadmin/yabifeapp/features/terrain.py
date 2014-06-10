import os
from lettuce import *
from selenium import webdriver
import lettuce_webdriver.webdriver

import steps

if "DISPLAY" not in os.environ:
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(800, 600))
else:
    display = None

@before.all
def set_browser():
    if display: display.start()
    world.browser = webdriver.Firefox()

@before.all
def set_wait_seconds():
    world.wait_seconds = 15


@before.all
def set_site_url():
    world.site_url = steps.get_site_url("yabifeapp", default_url="http://localhost:8000")


@after.all
def clean_after_tests(result):
    world.browser.quit()
    if display: display.stop()

@before.each_scenario
def delete_cookies(scenario):
    # delete all cookies so when we browse to a url at the start we have to log in
    world.browser.delete_all_cookies()

@after.each_step
def photo(step):
    name = str(step).replace("<","").replace("<","").replace('"',"") + ".png"
    world.browser.save_screenshot("after" + name)


