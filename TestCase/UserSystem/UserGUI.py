# coding=utf8


import unittest
from Core.Keywords.Selenium import Selenium
from Core.Keywords.BuiltIn import BuiltIn


class UserGUI(unittest.TestCase):
    """用户模块自动化用例 GUI版"""
    # 导入所需要的库
    def _include_librarys(self):
        self.selenium = Selenium()
        self.builtIn = BuiltIn()
    
    def setUp(self):
        self._include_librarys()
    
    def test_login(self):
        """登录
        操作步骤：
        预期结果：
        """
        pass

    def tearDown(self):
        pass
