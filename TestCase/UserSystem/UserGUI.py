# coding=utf8

import unittest
from Core.Keywords import selenium as selm
from Core.Keywords import builtIn as bln
from Core.Keywords import requests
from Library.CommonLibrary import CommonLibrary
from Resource.Variables.variables import *


class UserGUI(unittest.TestCase):
    """用户模块自动化用例 GUI版"""
    # 导入自定义库
    @classmethod
    def _include_librarys(self):
        self.comlib = CommonLibrary()

    @classmethod
    def setUpClass(self):
        self._include_librarys()
        # self.driver用于用例执行失败后自动截图, 变量为固定格式, 请勿更改, 不需要失败截图可注释
        self.driver = selm
        selm.set_selenium_speed(0.5)
    
    def setUp(self):
        pass

    def tearDown(self):
        # 启用失败自动截图功能后, 请务必注释掉这里的关闭浏览器功能, 失败截图后会自动关闭浏览器
        # selm.close_browser()
        pass

    # @unittest.skip('已取消')
    def test_U0001(self):
        """U0001_用户名注册
        操作步骤:
        1、进入注册页面
        2、输入6-16位账户名(非数字开头的英文、下划线和数字组合)、手机号(13、14、15、18、17开头)、登录密码(8-20位字符，至少含数字、大写字母、小写字母、符号中的2种)、验证码(6位)、选择推荐人，输入系统中存在的推荐人用户名或手机号
        3、勾选‘我已阅读并同意《小牛在线服务协议》’
        4、点击【下一步】
        5、点击【获取验证码】
        6、输入6位验证码，点击【确认】
        ======
        预期结果:         
        注册成功
        """
        pass

