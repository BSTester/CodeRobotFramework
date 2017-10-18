# encoding=utf8


from QTLibrary.keywords._element import _ElementKeywords
from QTLibrary.keywords._logging import _LoggingKeywords
from QTLibrary.keywords._runonfailure import _RunOnFailureKeywords


class CRFQT(
    _ElementKeywords,
    _LoggingKeywords,
    _RunOnFailureKeywords):
	def __init__(self):
		_ElementKeywords.__init__(self)
		_RunOnFailureKeywords.__init__(self)
		