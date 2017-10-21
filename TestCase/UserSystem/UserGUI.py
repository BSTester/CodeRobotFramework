# coding=utf8

import unittest
from Core.Keywords import selenium as selm
from Core.Keywords import builtIn as bln
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

    def setUp(self):
        pass
        
    def test_U0018(self):
        """U0018_会员等级
        操作步骤:
        操作步骤:
        1、点击【会员等级】链接
        
        ======
        预期结果:
        
        预期结果:
        1、显示当前用户的成长值
        2、显示【去赚取成长值】按钮，点击跳转成长任务界面
        3、显示各项成长任务对应成长值
        4、显示成长值的计算方式
        5、显示会员升级与保级说明
        """
        pass

    def tearDown(self):
        pass
