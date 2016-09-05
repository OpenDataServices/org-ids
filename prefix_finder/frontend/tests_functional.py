import os
import time
import pytest
from selenium import webdriver

BROWSER = os.environ.get('BROWSER', 'Firefox')


@pytest.fixture(scope="module")
def browser(request):
    if BROWSER == "Firefox":
        # Make downloads work
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", os.getcwd())
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/json")
        browser = getattr(webdriver, BROWSER)(firefox_profile=profile)
        browser.implicitly_wait(3)
        request.addfinalizer(lambda: browser.quit())
        return browser
    else:
        browser = getattr(webdriver, BROWSER)()
        browser.implicitly_wait(3)
        request.addfinalizer(lambda: browser.quit())
        return browser


@pytest.fixture(scope="module")
def server_url(request, live_server):
    if 'CUSTOM_SERVER_URL' in os.environ:
        return os.environ['CUSTOM_SERVER_URL']
    else:
        return live_server.url
    time.sleep(2)


def test_home(server_url, browser):
    browser.get(server_url)
    assert False
