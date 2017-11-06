# coding=utf8

import sys
import time
from datetime import datetime
from unittest import TextTestRunner, _TextTestResult
from .xmlrunner import XMLTestRunner
from .xmlrunner.result import _XMLTestResult
from .HtmlTestRunner.result import _HtmlTestResult


class _TestResult(_XMLTestResult, _HtmlTestResult):
    def generate_html_reports(self, testRunner):
        """ Generate report for all given runned test object. """
        all_results = self._get_info_by_testcase()
        all_tests = list()
        for testcase_class_name, all_test in all_results.items():
            all_tests += all_test
            if testRunner.outsuffix:
                testcase_class_name = "report.html"

        tests = self.report_tests(testcase_class_name, all_tests,
                                   testRunner)
        self.generate_file(testRunner.output, testcase_class_name,
                           tests)


class TestRunner(XMLTestRunner):
    """
    A test runner class that outputs the results in JUnit like XML files.
    """
    def __init__(self, output='.', outsuffix=None, stream=sys.stderr,
                 descriptions=True, verbosity=1, elapsed_times=True,
                 failfast=False, report_title=None, template=None, tb_locals=False,
                 buffer=False, encoding='UTF-8', resultclass=None, rerun=0):
        TextTestRunner.__init__(self, stream, descriptions, verbosity)
        self.rerun = rerun
        self.tb_locals = tb_locals
        self.verbosity = verbosity
        self.output = output
        self.encoding = encoding
        # None means default timestamped suffix
        # '' (empty) means no suffix
        if outsuffix is None:
            outsuffix = time.strftime("%Y%m%d%H%M%S")
        self.outsuffix = outsuffix
        self.elapsed_times = elapsed_times
        if resultclass is None:
            self.resultclass = _TestResult
        else:
            self.resultclass = resultclass

        self.report_title = report_title or "Test Report"
        self.template = template

    def run(self, test):
        """ Runs the given testcase or testsuite. """
        try:
            result = self._make_result()
            result.failfast = self.failfast
            result.tb_locals = self.tb_locals
            result.rerun = self.rerun
            if hasattr(test, 'properties'):
                # junit testsuite properties
                result.properties = test.properties

            self.stream.writeln()
            self.stream.writeln("Running tests... ")
            self.stream.writeln(result.separator2)

            self.start_time = datetime.now()
            test(result)
            stop_time = datetime.now()
            self.time_taken = stop_time - self.start_time
            
            result.printErrors()
            self.stream.writeln(result.separator2)
            run = result.testRun
            self.stream.writeln("Ran {} test{} in {}".format(run,
                                run != 1 and "s" or "", str(self.time_taken)))
            self.stream.writeln()

            expectedFails = len(result.expectedFailures)
            unexpectedSuccesses = len(result.unexpectedSuccesses)
            skipped = len(result.skipped)

            infos = []
            if not result.wasSuccessful():
                self.stream.write("FAILED")
                failed, errors = map(len, (result.failures, result.errors))
                if failed:
                    infos.append("Failures={0}".format(failed))
                if errors:
                    infos.append("Errors={0}".format(errors))
            else:
                self.stream.write("OK")

            if skipped:
                infos.append("Skipped={}".format(skipped))
            if expectedFails:
                infos.append("expected failures={}".format(expectedFails))
            if unexpectedSuccesses:
                infos.append("unexpected successes={}".format(unexpectedSuccesses))

            if infos:
                self.stream.writeln(" ({})".format(", ".join(infos)))
            else:
                self.stream.writeln("\n")

            self.stream.writeln()
            self.stream.writeln('Generating HTML reports... ')
            result.generate_html_reports(self)
            self.stream.writeln('Generating XML reports... ')
            result.generate_reports(self)
        finally:
            pass
        return result
