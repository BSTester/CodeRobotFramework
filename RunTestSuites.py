#!/usr/bin/env python3
# coding=utf8


from unittest import TestSuite, TestLoader
from Core.Runner.TestRunner import TestRunner
from Core.Runner.xmlrunner import XMLTestRunner
from Core.Runner.HtmlTestRunner import HTMLTestRunner
# 导入测试用例
from TestCase.UserSystem.UserGUI import UserGUI


# 加载所有测试用例
def test_suites():
    test_loader = TestLoader()
    test_suite = TestSuite()
    # test_suite.addTest(UserGUI('test_U0001'))
    test_suite.addTests([
        test_loader.loadTestsFromTestCase(UserGUI),
    ])
    return test_suite

# 执行测试
def main():
    # rerun  失败重试次数
    # tb_locals  日志中是否打印变量值
    runner = TestRunner(output='Results', verbosity=2, tb_locals=True, rerun=2)
    runner.run(test_suites())

if __name__ == '__main__':
    main()
