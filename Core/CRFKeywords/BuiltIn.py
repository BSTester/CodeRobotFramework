# encoding=utf8

from robot.libraries.BuiltIn import BuiltIn as RobotBuiltIn
from robot.libraries.Collections import Collections
from robot.libraries.OperatingSystem import OperatingSystem
from robot.libraries.Process import Process
from robot.libraries.Remote import Remote
from robot.libraries.Reserved import Reserved
from robot.libraries.Screenshot import Screenshot
from robot.libraries.String import String
from robot.libraries.Telnet import Telnet
from robot.libraries.XML import XML
import time


class CRFBuiltIn(
    RobotBuiltIn, 
    Collections, 
    OperatingSystem,
    Process, 
    Remote,
    Reserved,
    Screenshot,
    String,
    Telnet,
    XML):
    def __init__(self):
        Process.__init__(self)
        Remote.__init__(self)
        Screenshot.__init__(self)
        Telnet.__init__(self)
        XML.__init__(self)

    def print_log(self, message):
        message = '\n[{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), message)
        self.log('{}'.format(message), console=True)
        print('{}'.format(message))
