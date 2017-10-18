# coding=utf8


from DatabaseLibrary.connection_manager import ConnectionManager
from DatabaseLibrary.query import Query
from DatabaseLibrary.assertion import Assertion


class CRFDatabase(ConnectionManager, Query, Assertion):
    def __init__(self):
    	ConnectionManager.__init__(self)
