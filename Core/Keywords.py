# encoding=utf8


from Core.CRFKeywords.Appium import CRFAppium
from Core.CRFKeywords.Archive import CRFArchive
from Core.CRFKeywords.BuiltIn import CRFBuiltIn
from Core.CRFKeywords.Database import CRFDatabase
from Core.CRFKeywords.Diff import CRFDiff
# from Core.CRFKeywords.Ftp import CRFFtp
# from Core.CRFKeywords.Mongo import CRFMongo
from Core.CRFKeywords.QT import CRFQT
from Core.CRFKeywords.Requests import CRFRequests
from Core.CRFKeywords.Selenium import CRFSelenium


# 初始化关键字
selenium = CRFSelenium()
requests = CRFRequests()
qt = CRFQT()
# mongo = CRFMongo()
# ftp = CRFFtp()
diff = CRFDiff()
database = CRFDatabase()
archive = CRFArchive()
appium = CRFAppium()
builtIn = CRFBuiltIn()
