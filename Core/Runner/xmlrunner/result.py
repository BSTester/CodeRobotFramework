
import os
import sys
import time
from datetime import datetime
import traceback
import six
import re
from os import path
from six.moves import StringIO

from .unittest import TestResult, _TextTestResult, failfast


# Matches invalid XML1.0 unicode characters, like control characters:
# http://www.w3.org/TR/2006/REC-xml-20060816/#charsets
# http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python

_illegal_unichrs = [
    (0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F), 
    (0x7F, 0x84), (0x86, 0x9F), 
    (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
] 
if sys.maxunicode >= 0x10000:  # not narrow build 
    _illegal_unichrs.extend([
        (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), 
        (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF), 
        (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF), 
        (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), 
        (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF), 
        (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF), 
        (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), 
        (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF),
    ]) 

_illegal_ranges = [
    "%s-%s" % (six.unichr(low), six.unichr(high))
    for (low, high) in _illegal_unichrs
]

INVALID_XML_1_0_UNICODE_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges)) 


STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


def xml_safe_unicode(base, encoding='utf-8'):
    """Return a unicode string containing only valid XML characters.

    encoding - if base is a byte string it is first decoded to unicode
        using this encoding.
    """
    if isinstance(base, six.binary_type):
        base = base.decode(encoding)
    return INVALID_XML_1_0_UNICODE_RE.sub('', base)


def to_unicode(data):
    """Returns unicode in Python2 and str in Python3"""
    if six.PY3:
        return six.text_type(data)
    try:
        # Try utf8
        return six.text_type(data)
    except UnicodeDecodeError:
        return repr(data).decode('utf8', 'replace')


def safe_unicode(data, encoding=None):
    return xml_safe_unicode(to_unicode(data), encoding)


def testcase_name(test_method):
    testcase = type(test_method)

    # Ignore module name if it is '__main__'
    module = testcase.__module__ + '.'
    if module == '__main__.':
        module = ''
    result = module + testcase.__name__
    return result


class _TestInfo(object):
    """
    This class keeps useful information about the execution of a
    test method.
    """

    # Possible test outcomes
    (SUCCESS, FAILURE, ERROR, SKIP) = range(4)

    def __init__(self, test_result, test_method, outcome=SUCCESS, err=None, subTest=None):
        self.test_result = test_result
        self.outcome = outcome
        self.start_time = 0
        self.stop_time = 0
        self.elapsed_time = 0
        self.err = err
        self.stdout = test_result._stdout_data
        self.stderr = test_result._stderr_data
        self.screenshot = ''
        self.rerun = 0
        test_description = self.test_result.getDescription(test_method)
        self.test_description = test_description.split()[0] if len(test_description.split())<3 else test_description.split()[-1]

        self.test_exception_info = (
            '' if outcome in (self.SUCCESS, self.SKIP)
            else self.test_result._exc_info_to_string(
                self.err, test_method)
        )
        
        self.suite_doc = test_method.__doc__
        self.test_doc = test_method._testMethodDoc
        self.test_name = testcase_name(test_method)
        self.test_id = test_method.id()
        if subTest:
            self.test_id = subTest.id()

    def id(self):
        return self.test_id

    def test_finished(self):
        """Save info that can only be calculated once a test has run.
        """
        self.elapsed_time = \
            self.test_result.stop_time - self.test_result.start_time
        self.start_time = self.test_result.start_time
        self.stop_time = self.test_result.stop_time

    def get_description(self):
        """
        Return a text representation of the test method.
        """
        return self.test_description

    def get_error_info(self):
        """
        Return a text representation of an exception thrown by a test
        method.
        """
        return self.test_exception_info


class _XMLTestResult(_TextTestResult):
    """
    A test result class that can express test results in a XML report.

    Used by XMLTestRunner.
    """
    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1,
                 elapsed_times=True, properties=None, infoclass=None):
        _TextTestResult.__init__(self, stream, descriptions, verbosity)
        self.rerun = 0
        self.retry = 0
        self.tb_locals = False
        self.buffer = True  # we are capturing test output
        self._stdout_data = None
        self._stderr_data = None
        self.successes = []
        self.tested_fail_error = []
        self.callback = None
        self.elapsed_times = elapsed_times
        self.properties = properties  # junit testsuite properties
        if infoclass is None:
            self.infoclass = _TestInfo
        else:
            self.infoclass = infoclass
        self.testRun = 0

    def _prepare_callback(self, test_info, target_list, verbose_str,
                          short_str):
        """
        Appends a `infoclass` to the given target list and sets a callback
        method to be called by stopTest method.
        """
        target_list.append(test_info)

        def callback():
            """Prints the test method outcome to the stream, as well as
            the elapsed time.
            """
            test_info.test_finished()

            # Ignore the elapsed times for a more reliable unit testing
            if not self.elapsed_times:
                self.start_time = self.stop_time = 0

            if self.showAll:
                self.stream.writeln(
                    '%s (%.6fs)' % (verbose_str, test_info.elapsed_time)
                )
            elif self.dots:
                self.stream.write(short_str)

        self.callback = callback

    def startTest(self, test):
        """
        Called before execute each test method.
        """
        if self.retry == 0:
            self.testRun += 1
        self.start_time = time.time()
        TestResult.startTest(self, test)

        if self.showAll:
            self.stream.write('  ' + self.getDescription(test))
            self.stream.write(" ... ")

    def _save_output_data(self):
        # Only try to get sys.stdout and sys.sterr as they not be
        # StringIO yet, e.g. when test fails during __call__
        try:
            self._stdout_data = sys.stdout.getvalue()
            self._stderr_data = sys.stderr.getvalue()
        except AttributeError:
            pass

    def stopTest(self, test):
        """
        Called after execute each test method.
        """
        self._save_output_data()
        # self._stdout_data = sys.stdout.getvalue()
        # self._stderr_data = sys.stderr.getvalue()

        _TextTestResult.stopTest(self, test)
        self.stop_time = time.time()

        if self.callback and callable(self.callback):
            self.callback()
            self.callback = None

        if self.rerun > self.retry:
            self.retry += 1
            self.stream.write('Rerun {} time...'.format(self.retry))
            test(self)
        else:
            self.retry = 0

    def addSuccess(self, test):
        """
        Called when a test executes successfully.
        """
        self._save_output_data()
        testinfo = self.infoclass(self, test)
        testinfo.rerun = self.retry
        self._prepare_callback(
            testinfo, self.successes, 'OK', '.'
        )
        self.retry = self.rerun
        if testinfo.test_id in self.tested_fail_error:
            self._remove_test(testinfo.test_id)

    @failfast
    def addFailure(self, test, err):
        """
        Called when a test method fails.
        """
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.FAILURE, err)
        if testinfo.test_id in self.tested_fail_error:
            self._remove_test(testinfo.test_id)
        try:
            testinfo.screenshot = test.driver.capture_page_screenshot()
            test.driver.close_browser()
        except Exception as e:
            pass
        testinfo.rerun = self.retry
        self.failures.append((testinfo,
            self._exc_info_to_string(err, test)))
        self.tested_fail_error.append(testinfo.test_id)
        self._prepare_callback(testinfo, [], 'FAIL', 'F')

    @failfast
    def addError(self, test, err):
        """
        Called when a test method raises an error.
        """
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.ERROR, err)
        if testinfo.test_id in self.tested_fail_error:
            self._remove_test(testinfo.test_id)
        try:
            testinfo.screenshot = test.driver.capture_page_screenshot()
            test.driver.close_browser()
        except Exception as e:
            pass
        testinfo.rerun = self.retry
        self.errors.append((testinfo,
            self._exc_info_to_string(err, test)))
        self.tested_fail_error.append(testinfo.test_id)
        self._prepare_callback(testinfo, [], 'ERROR', 'E')

    def addSubTest(self, testcase, test, err):
        """
        Called when a subTest method raises an error.
        """
        if err is not None:
            self._save_output_data()
            testinfo = self.infoclass(
                self, testcase, self.infoclass.ERROR, err, subTest=test)
            if testinfo.test_id in self.tested_fail_error:
                self._remove_test(testinfo.test_id)
            try:
                testinfo.screenshot = test.driver.capture_page_screenshot()
                test.driver.close_browser()
            except Exception as e:
                pass
            testinfo.rerun = self.retry
            self.errors.append((
                testinfo,
                self._exc_info_to_string(err, testcase)
            ))
            self.tested_fail_error.append(testinfo.test_id)
            self._prepare_callback(testinfo, [], 'ERROR', 'E')

    def addSkip(self, test, reason):
        """
        Called when a test method was skipped.
        """
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.SKIP, reason)
        self.skipped.append((testinfo, reason))
        self._prepare_callback(testinfo, [], 'SKIP', 'S')
        self.retry = self.rerun

    def _remove_test(self, test_id):
        for test in self.failures:
            if test[0].test_id == test_id:
                self.failures.remove(test)
        for test in self.errors:
            if test[0].test_id == test_id:
                self.errors.remove(test)

    def printErrorList(self, flavour, errors):
        """
        Writes information about the FAIL or ERROR to the stream.
        """
        for test_info, dummy in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(
                '%s [%.6fs]: %s' % (flavour, test_info.elapsed_time,
                                    test_info.get_description())
            )
            self.stream.writeln(self.separator2)
            self.stream.writeln('%s' % test_info.get_error_info())

    def _get_info_by_testcase(self):
        """
        Organizes test results by TestCase module. This information is
        used during the report generation, where a XML report will be created
        for each TestCase.
        """
        tests_by_testcase = {}
        for tests in (self.successes, self.failures, self.errors,
                      self.skipped):
            for test_info in tests:
                if isinstance(test_info, tuple):
                    # This is a skipped, error or a failure test case
                    test_info = test_info[0]
                testcase_name = test_info.suite_doc if test_info.suite_doc else test_info.test_name
                if testcase_name not in tests_by_testcase:
                    tests_by_testcase[testcase_name] = []
                tests_by_testcase[testcase_name].append(test_info)

        return tests_by_testcase

    def _report_testsuite_properties(xml_testsuite, xml_document, properties):
        if properties:
            xml_properties = xml_document.createElement('properties')
            xml_testsuite.appendChild(xml_properties)
            for key, value in properties.items():
                prop = xml_document.createElement('property')
                prop.setAttribute('name', str(key))
                prop.setAttribute('value', str(value))
                xml_properties.appendChild(prop)

    _report_testsuite_properties = staticmethod(_report_testsuite_properties)

    def _report_testsuite(suite_name, tests, xml_document, parentElement,
                          properties):
        """
        Appends the testsuite section to the XML document.
        """
        testsuite = xml_document.createElement('testsuite')
        parentElement.appendChild(testsuite)

        testsuite.setAttribute('name', suite_name)
        testsuite.setAttribute('tests', str(len(tests)))

        testsuite.setAttribute(
            'time', '%.6f' % sum(map(lambda e: e.elapsed_time, tests))
        )
        failures = filter(lambda e: e.outcome == e.FAILURE, tests)
        failures = len(list(failures))
        testsuite.setAttribute('failures', str(failures))

        errors = filter(lambda e: e.outcome == e.ERROR, tests)
        errors = len(list(errors))
        testsuite.setAttribute('errors', str(errors))

        skips = filter(lambda e: e.outcome == _TestInfo.SKIP, tests)
        skips = len(list(skips))
        testsuite.setAttribute('skipped', str(skips))
 
        parentElement.setAttribute('tests', str(int(parentElement.getAttribute('tests'))+len(tests)))
        parentElement.setAttribute('failures', str(int(parentElement.getAttribute('failures'))+failures))
        parentElement.setAttribute('errors', str(int(parentElement.getAttribute('errors'))+errors))
        parentElement.setAttribute('skipped', str(int(parentElement.getAttribute('skipped'))+skips))
        parentElement.setAttribute('time', '%.6f' % (sum(map(lambda e: e.elapsed_time, tests))+float(parentElement.getAttribute('time'))))

        _XMLTestResult._report_testsuite_properties(
            testsuite, xml_document, properties)

        for test in tests:
            _XMLTestResult._report_testcase(test, testsuite, xml_document)

        systemout = xml_document.createElement('system-out')
        testsuite.appendChild(systemout)

        stdout = StringIO()
        for test in tests:
            # Merge the stdout from the tests in a class
            if test.stdout is not None:
                stdout.write(test.stdout)
        _XMLTestResult._createCDATAsections(
            xml_document, systemout, stdout.getvalue())

        systemerr = xml_document.createElement('system-err')
        testsuite.appendChild(systemerr)

        stderr = StringIO()
        for test in tests:
            # Merge the stderr from the tests in a class
            if test.stderr is not None:
                stderr.write(test.stderr)
        _XMLTestResult._createCDATAsections(
            xml_document, systemerr, stderr.getvalue())

        return testsuite

    _report_testsuite = staticmethod(_report_testsuite)

    def _test_method_name(test_id):
        """
        Returns the test method name.
        """
        return test_id.split('.')[-1]

    _test_method_name = staticmethod(_test_method_name)

    def _createCDATAsections(xmldoc, node, text):
        text = safe_unicode(text)
        pos = text.find(']]>')
        while pos >= 0:
            tmp = text[0:pos+2]
            cdata = xmldoc.createCDATASection(tmp)
            node.appendChild(cdata)
            text = text[pos+2:]
            pos = text.find(']]>')
        cdata = xmldoc.createCDATASection(text)
        node.appendChild(cdata)

    _createCDATAsections = staticmethod(_createCDATAsections)

    def _report_testcase(test_result, xml_testsuite, xml_document):
        """
        Appends a testcase section to the XML document.
        """
        testcase = xml_document.createElement('testcase')
        xml_testsuite.appendChild(testcase)

        class_name = re.sub(r'^__main__.', '', test_result.id())
        class_name = class_name.rpartition('.')[0]
        testcase.setAttribute('classname', class_name)
        testcase.setAttribute(
            'name', '{} ({})'.format(_XMLTestResult._test_method_name(test_result.test_description), test_result.test_id.split('.')[-1])
        )

        testcase.setAttribute('starttime', datetime.fromtimestamp(test_result.start_time).strftime('%Y-%m-%d %H:%M:%S.%f'))
        testcase.setAttribute('stoptime', datetime.fromtimestamp(test_result.stop_time).strftime('%Y-%m-%d %H:%M:%S.%f'))
        testcase.setAttribute('time', '%.6f' % test_result.elapsed_time)
        testcase.setAttribute('status', "PASS")
        testcase.setAttribute('rerun', str(test_result.rerun))
        testcase.setAttribute('screenshot', test_result.screenshot)
        property_step = xml_document.createElement('step')
        property_expected = xml_document.createElement('expected')
        testcase.appendChild(property_step)
        testcase.appendChild(property_expected)
        test_doc = test_result.test_doc        
        test_doc = test_doc if test_doc else '======'
        test_doc = test_doc.split('\n', 1)[-1]
        sep = re.findall(r'(======+)', test_doc)[0] if len(re.findall(r'(======+)', test_doc)) != 0 else '======'
        test_doc = test_doc.split(sep, 1)
        detail_step = test_doc[0]
        expected = test_doc[1] if len(test_doc) > 1 else ''
        property_step.setAttribute('message', detail_step)
        property_expected.setAttribute('message', expected.strip())

        if (test_result.outcome != test_result.SUCCESS):
            elem_name = ('failure', 'error', 'skipped')[test_result.outcome-1]
            failure = xml_document.createElement(elem_name)
            testcase.appendChild(failure)
            if test_result.outcome != test_result.SKIP:
                testcase.setAttribute('status', "FAIL")
                failure.setAttribute(
                    'type',
                    safe_unicode(test_result.err[0].__name__)
                )
                failure.setAttribute(
                    'message',
                    safe_unicode(test_result.err[1])
                )
                error_info = safe_unicode(test_result.get_error_info())
                _XMLTestResult._createCDATAsections(
                    xml_document, failure, error_info)
            else:
                testcase.setAttribute('status', "SKIP")
                failure.setAttribute('type', 'skip')
                failure.setAttribute('message', safe_unicode(test_result.err))

    _report_testcase = staticmethod(_report_testcase)

    def generate_reports(self, test_runner):
        """
        Generates the XML reports to a given XMLTestRunner object.
        """
        from xml.dom.minidom import Document
        all_results = self._get_info_by_testcase()

        outputHandledAsString = \
            isinstance(test_runner.output, six.string_types)

        if (outputHandledAsString and not os.path.exists(test_runner.output)):
            os.makedirs(test_runner.output)

        doc = Document()
        testsuite = doc.createElement('testsuites')
        doc.appendChild(testsuite)
        parentElement = testsuite
            
        parentElement.setAttribute('name', test_runner.report_title)
        parentElement.setAttribute('tests', '0')
        parentElement.setAttribute('time', '0.000')
        parentElement.setAttribute('failures', '0')
        parentElement.setAttribute('errors', '0')
        parentElement.setAttribute('skipped', '0')
 
        for suite, tests in all_results.items():
            suite_name = suite
            if test_runner.outsuffix:
                # not checking with 'is not None', empty means no suffix.
                suite_name = '%s-%s' % (suite, test_runner.outsuffix)

            # Build the XML file
            testsuite = _XMLTestResult._report_testsuite(
                suite_name, tests, doc, parentElement, self.properties
            )
        xml_content = doc.toprettyxml(
            indent='\t',
            encoding=test_runner.encoding
        )

        if outputHandledAsString:
            filename = path.join(
                test_runner.output,
                'output.xml')
            with open(filename, 'wb') as report_file:
                report_file.write(xml_content)

        if not outputHandledAsString:
            # Assume that test_runner.output is a stream
            test_runner.output.write(xml_content)

    def _exc_info_to_string(self, err, test):
        """Converts a sys.exc_info()-style tuple of values into a string."""
        if six.PY3:
            # It works fine in python 3
            try:
                return super(_XMLTestResult, self)._exc_info_to_string(
                    err, test)
            except AttributeError:
                # We keep going using the legacy python <= 2 way
                pass

        # This comes directly from python2 unittest
        exctype, value, tb = err
        # Skip test runner traceback levels
        while tb and self._is_relevant_tb_level(tb):
            tb = tb.tb_next

        if exctype is test.failureException:
            # Skip assert*() traceback levels
            length = self._count_relevant_tb_levels(tb)
            msgLines = traceback.format_exception(exctype, value, tb, length)
        else:
            msgLines = traceback.format_exception(exctype, value, tb)

        if self.buffer:
            # Only try to get sys.stdout and sys.sterr as they not be
            # StringIO yet, e.g. when test fails during __call__
            try:
                output = sys.stdout.getvalue()
            except AttributeError:
                output = None
            try:
                error = sys.stderr.getvalue()
            except AttributeError:
                error = None
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        # This is the extra magic to make sure all lines are str
        encoding = getattr(sys.stdout, 'encoding', 'utf-8')
        lines = []
        for line in msgLines:
            if not isinstance(line, str):
                # utf8 shouldnt be hard-coded, but not sure f
                line = line.encode(encoding)
            lines.append(line)

        return ''.join(lines)
