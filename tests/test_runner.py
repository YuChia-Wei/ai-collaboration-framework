"""Observable runner outcomes: failures, import errors, skips and empty selections fail."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import unittest
from unittest.mock import patch

import run


class RunnerTests(unittest.TestCase):
    def invoke(self, case):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(run, "load_suite", return_value=case), redirect_stdout(stdout), redirect_stderr(stderr):
            code = run.main(["--suite", "source"])
        return code, json.loads(stdout.getvalue())["framework_tests"], stderr.getvalue()

    def test_success_reports_executed_selection(self):
        code, report, stderr = self.invoke(unittest.TestSuite([unittest.FunctionTestCase(lambda: None)]))
        self.assertEqual(code, 0)
        self.assertEqual((report["suites"], report["tests"], report["outcome"]), (["source"], 1, "passed"))
        self.assertIn("Ran 1 test", stderr)

    def test_failures_errors_and_skips_cannot_pass(self):
        for exception, field in ((AssertionError("bad assertion"), "failures"),
                                 (ImportError("missing dependency"), "errors"),
                                 (unittest.SkipTest("unavailable"), "skipped")):
            def fail(exc=exception):
                raise exc
            with self.subTest(field=field):
                code, report, _ = self.invoke(unittest.TestSuite([unittest.FunctionTestCase(fail)]))
                self.assertEqual((code, report["outcome"], report[field]), (1, "failed", 1))

    def test_empty_suite_cannot_pass(self):
        code, report, stderr = self.invoke(unittest.TestSuite())
        self.assertEqual((code, report["tests"], report["errors"]), (1, 0, 1))
        self.assertIn("contains no tests", stderr)

    def test_unknown_selection_is_rejected(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            run.main(["--suite", "missing"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
