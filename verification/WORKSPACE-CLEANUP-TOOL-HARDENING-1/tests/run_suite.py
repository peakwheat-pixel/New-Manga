# -*- coding: utf-8 -*-
"""Run the hardening test suite and emit machine-readable per-test outcomes.

``unittest -v`` prints a test's docstring instead of its dotted id when a
docstring exists, which makes log parsing ambiguous.  This tiny runner uses the
same verbose text output for humans and appends one ``JSON_RESULTS:`` line with
``{test_id: outcome}`` for the evidence generator (AC7 coverage matrix).
"""
import json
import os
import sys
import unittest


class Collector(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[test.id()] = "ok"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test.id()] = "FAIL"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test.id()] = "ERROR"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test.id()] = "skipped: %s" % reason


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    loader = unittest.TestLoader()
    suite = loader.discover(here, pattern="test_*.py", top_level_dir=here)
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2,
                                     resultclass=Collector)
    result = runner.run(suite)
    sys.stdout.write("JSON_RESULTS:%s\n"
                     % json.dumps(result.outcomes, sort_keys=True))
    sys.stdout.flush()
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
