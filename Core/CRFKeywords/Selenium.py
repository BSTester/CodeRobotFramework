# encoding=utf8


import os
from SeleniumLibrary.base.robotlibcore import PY2
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.keywords.alert import AlertKeywords
from SeleniumLibrary.keywords.browsermanagement import BrowserManagementKeywords
from SeleniumLibrary.keywords.cookie import CookieKeywords
from SeleniumLibrary.keywords.element import ElementKeywords
from SeleniumLibrary.keywords.formelement import FormElementKeywords
from SeleniumLibrary.keywords.javascript import JavaScriptKeywords
from SeleniumLibrary.keywords.runonfailure import RunOnFailureKeywords
from SeleniumLibrary.keywords.screenshot import ScreenshotKeywords
from SeleniumLibrary.keywords.selectelement import SelectElementKeywords
from SeleniumLibrary.keywords.tableelement import TableElementKeywords
from SeleniumLibrary.keywords.waiting import WaitingKeywords


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
    def __init__(self, timeout=60, implicit_wait=0.0,
                 run_on_failure='Capture Page Screenshot',
                 screenshot_root_directory='Results'):
        ctx = SeleniumLibrary(timeout=timeout, implicit_wait=implicit_wait, 
            run_on_failure=run_on_failure, screenshot_root_directory=screenshot_root_directory)
        self.screenshot_directory = screenshot_root_directory
        AlertKeywords.__init__(self, ctx),
        BrowserManagementKeywords.__init__(self, ctx),
        CookieKeywords.__init__(self, ctx),
        ElementKeywords.__init__(self, ctx),
        FormElementKeywords.__init__(self, ctx),
        JavaScriptKeywords.__init__(self, ctx),
        RunOnFailureKeywords.__init__(self, ctx),
        ScreenshotKeywords.__init__(self, ctx),
        SelectElementKeywords.__init__(self, ctx),
        TableElementKeywords.__init__(self, ctx),
        WaitingKeywords.__init__(self, ctx)

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
