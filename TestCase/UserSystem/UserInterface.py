# coding=utf8


import unittest


class UserInterface(unittest.TestCase):
    """用户模块自动化用例 接口版"""
    
    def setUp(self):
        pass
        
    def test_U0001_username_register(self):
        """U0001_用户名注册
        操作步骤:
        1、进入注册页面
        2、输入6-16位账户名
        3、勾选‘我已阅读并同意《服务协议》’
        4、点击【下一步】
        5、点击【获取验证码】
        6、输入6位验证码，点击【确认】
        ======
        预期结果:
        注册成功
        """
        pass

    def tearDown(self):
        pass