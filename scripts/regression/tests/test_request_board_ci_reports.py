"""Fail-closed report adapters for this sample, not a universal CI parser."""

from copy import deepcopy
import importlib.util
import io
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("request_board_checks", ROOT / "examples/product-request-board/ci/checks.py")
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


class RequestBoardReportTests(unittest.TestCase):
    def setUp(self):
        self.inventory = checks.required()
        self.api = {"executed": len(self.inventory["api"]), "cases": [
            {"id": name, "status": "passed"} for name in self.inventory["api"]]}
        self.browser = {"errors": [], "suites": [{"specs": [
            {"title": tag, "tags": [tag.removeprefix("@")], "tests": [
                {"projectName": project, "expectedStatus": "passed", "status": "expected",
                 "results": [{"status": "passed", "retry": 0, "errors": []}]}
                for project in self.inventory["projects"]]}
            for tag in self.inventory["browser"]]}]}

    def test_complete_reports(self):
        self.assertEqual(checks.api_issues(self.api, self.inventory), [])
        self.assertEqual(checks.browser_issues(self.browser, self.inventory), [])

    def test_api_missing_duplicate_and_nonpassing_are_not_success(self):
        for state in ("skipped", "failed", "error", "expected_failure", "unexpected_success", "unknown"):
            report = deepcopy(self.api)
            report["cases"][0]["status"] = state
            self.assertTrue(checks.api_issues(report, self.inventory), state)
        for cases in ([], self.api["cases"][1:], self.api["cases"] * 2):
            self.assertTrue(checks.api_issues({"cases": cases, "executed": len(cases)}, self.inventory))

    def test_browser_missing_project_flow_and_duplicate_cannot_hide_in_green_report(self):
        report = deepcopy(self.browser)
        report["suites"][0]["specs"].pop(0)
        self.assertTrue(checks.browser_issues(report, self.inventory))
        report = deepcopy(self.browser)
        report["suites"][0]["specs"][0]["tests"].pop()
        self.assertTrue(checks.browser_issues(report, self.inventory))
        report = deepcopy(self.browser)
        report["suites"] *= 2
        self.assertTrue(checks.browser_issues(report, self.inventory))
        self.assertTrue(checks.browser_issues({"suites": []}, self.inventory))

    def test_browser_skip_expected_failure_retry_and_runner_error_are_rejected(self):
        variants = [{"results": []}, {"expectedStatus": "failed"}, {"status": "skipped"},
                    {"results": [{"status": "skipped"}]}, {"results": [{"status": "failed"}]},
                    {"results": [{"status": "passed", "retry": 1}]},
                    {"results": [{"status": "passed", "errors": ["hidden error"]}]},
                    {"results": [{"status": "failed"}, {"status": "passed"}]}]
        for variant in variants:
            report = deepcopy(self.browser)
            report["suites"][0]["specs"][0]["tests"][0].update(variant)
            self.assertTrue(checks.browser_issues(report, self.inventory), variant)
        self.browser["errors"] = ["global setup failed"]
        self.assertTrue(checks.browser_issues(self.browser, self.inventory))

    def test_recorded_unittest_subtest_failure_cannot_be_counted_as_pass(self):
        class Sample(unittest.TestCase):
            def test_bad(self):
                with self.subTest("failure"):
                    self.fail("known failure")
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=checks.RecordedResult).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Sample))
        self.assertEqual(result.cases[0]["status"], "failed")
        self.assertEqual(result.testsRun, 1)

    def test_workflow_preserves_always_run_final_gate_and_unprivileged_execution(self):
        text = (ROOT / ".github/workflows/product-request-board.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("if: always()\n        env:\n          REQUIRED:", text)
        self.assertIn("STEPS_JSON: ${{ toJSON(steps) }}", text)
        self.assertNotIn("continue-on-error", text)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("paths-ignore:", text)
        self.assertNotIn("secrets.", text)
        self.assertNotIn("if: ", text.split("steps:", 1)[0])
        for name in ("static", "api", "browser", "reports", "probe"):
            self.assertIn("id: " + name, text)


if __name__ == "__main__":
    unittest.main()
