# CodeRobotFramework(CRF)
不想填表格？文本模式编辑没有直接写代码的感觉？试试code版robotframework吧, 基于unittest编写测试用例, 完全支持robotframework内置关键字和扩展库关键字, 可同时生成HTML格式测试报告和JUnit XML格式报告, 可直接集成到Jenkins中执行并查看结果。 

## 需要安装的模块
```
pip install -U unittest-xml-reporting html-testRunner requests selenium \
pymysql pymongo robotframework robotframework-seleniumlibrary \
robotframework-requests robotframework-databaselibrary \
robotframework-ftplibrary robotframework-appiumlibrary \
robotframework-archivelibrary robotframework-difflibrary \
robotframework-mongodbLibrary 
```

## 可选安装的模块
```
pip install -U robotframework-selenium2library \
robotframework-extendedselenium2library robotframework-httplibrary \
robotframework-faker robotframework-ncclient robotremoteserver
```

## 目录结构说明
```
├─Core          框架核心库
│  ├─Keywords   函数库
│  └─Runner     运行库
├─Library       自定义库
├─Resource      资源
│  ├─TestData   测试数据
│  │  ├─Files   普通文件
│  │  └─SQL     SQL文件
│  └─Variables  配置/变量
├─Results       测试结果
└─TestCase      测试用例
```

## 用例注释格式说明
编写用例时增加注释可以对测试用例进行必要的描述, 同时在生成测试报告时会获取注释内容以便在测试报告中显示测试标题、操作步骤和预期结果。
```
import unittest

class TestSuite(unittest.TestCase):
    def test_case(self):
        """用例标题
        操作步骤：
        1、
        2、
        3、
        ======
        预期结果：
        1、
        2、
        """
        pass
```
>Ps: 用例标题必须写在第一行, 换行编写操作步骤和预期结果, 操作步骤与预期结果之间用======分隔开, 至少包含6个等号。
