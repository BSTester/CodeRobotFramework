# encoding=utf8


import os
from SeleniumLibrary.base.robotlibcore import PY2
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.keywords import (AlertKeywords,
                                      BrowserManagementKeywords,
                                      CookieKeywords,
                                      ElementKeywords,
                                      FormElementKeywords,
                                      JavaScriptKeywords,
                                      RunOnFailureKeywords,
                                      ScreenshotKeywords,
                                      SelectElementKeywords,
                                      TableElementKeywords,
                                      WaitingKeywords)
from Core.CRFKeywords.BuiltIn import CRFBuiltIn
from robot.libraries.BuiltIn import RobotNotRunningError


class CRFSelenium(
    AlertKeywords,
    BrowserManagementKeywords,
    CookieKeywords,
    ElementKeywords,
    FormElementKeywords,
    JavaScriptKeywords,
    RunOnFailureKeywords,
    ScreenshotKeywords,
    SelectElementKeywords,
    TableElementKeywords,
    WaitingKeywords):
    def __init__(self):
        ctx = SeleniumLibrary(screenshot_root_directory='Results')
        AlertKeywords.__init__(self, ctx)
        BrowserManagementKeywords.__init__(self, ctx)
        ElementKeywords.__init__(self, ctx)
        FormElementKeywords.__init__(self, ctx)
        ScreenshotKeywords.__init__(self, ctx)
        SelectElementKeywords.__init__(self, ctx)
        WaitingKeywords.__init__(self, ctx)
        self.screenshot_directory = ctx.screenshot_root_directory
        self.builtIn = CRFBuiltIn()

    @property
    def log_dir(self):
        try:
            if os.path.isdir(self.screenshot_directory):
                return os.path.abspath(self.screenshot_directory)
            else:
                os.makedirs(self.screenshot_directory)
                return os.path.abspath(self.screenshot_directory)
        except RobotNotRunningError:
            return os.getcwdu() if PY2 else os.getcwd()

    def open_wdBrowser(self, url, browser='Chrome'):
        """
        通过WebDriver启动浏览器
        启动浏览器类型，可选：Firefox、Chrome、PhantomJS
        """
        self.builtIn.print_log('==============通过 WebDriver 打开 {} 浏览器=============='.format(browser))
        service_args = ['--ssl-protocol=any', '--web-security=false', '--debug=true', 
                        '--ignore-ssl-errors=true', '--webdriver-loglevel=WARN']
        if browser == 'PhantomJS':
            self.create_webdriver(browser, service_args=service_args)
        else:
            self.create_webdriver(browser)
        self.go_to(url)
        self.maximize_browser_window()

    def make_element_visible(self, xpath):
        """Make Element Visible"""
        self.builtIn.print_log('============使节点元素 {} 可见==========='.format(xpath))
        self.wait_until_page_contains_element(xpath)
        self.execute_javascript("document.evaluate('{}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.style.display = 'block';".format(xpath))
        self.wait_until_emement_is_visible(xpath)
