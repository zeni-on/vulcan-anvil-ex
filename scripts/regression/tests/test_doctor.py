import contextlib
import io
import json
import os
import tempfile
import unittest

from vulcan_core.doctor import build_doctor_report, render_doctor_report, run_doctor


class DoctorReportTests(unittest.TestCase):
    def test_report_preserves_project_profile_and_json_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "session.json"), "w", encoding="utf-8") as file_obj:
                json.dump({"project": "doctor-fixture", "current_gate": "gate2"}, file_obj)
            with open(os.path.join(temp_dir, "vulcan.config.json"), "w", encoding="utf-8") as file_obj:
                json.dump({"runtime": {"primary": "codex"}}, file_obj)

            report = build_doctor_report(
                temp_dir,
                delivery_profile="product",
                runner_detector=lambda: [],
            )

            self.assertEqual(report["project_dir"], os.path.abspath(temp_dir))
            self.assertEqual(set(report["summary"]), {"pass", "warn", "fail", "info"})
            self.assertTrue(report["checks"])
            by_name = {check["name"]: check for check in report["checks"]}
            self.assertEqual(by_name["project_dir"]["status"], "pass")
            self.assertIn("project=doctor-fixture", by_name["session.json"]["detail"])
            self.assertEqual(
                by_name["vulcan.config.json"]["detail"],
                "profile=product, primary_runner=codex",
            )

            rendered = json.loads(render_doctor_report(report, emit_json=True))
            self.assertEqual(rendered, report)

    def test_run_doctor_returns_failure_for_missing_project(self):
        missing_dir = os.path.join(tempfile.gettempdir(), "vulcan-doctor-missing-project")
        if os.path.exists(missing_dir):
            self.skipTest(f"unexpected fixture path exists: {missing_dir}")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = run_doctor(
                missing_dir,
                delivery_profile="audit",
                runner_detector=lambda: [],
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("[FAIL] project.project_dir", output.getvalue())


if __name__ == "__main__":
    unittest.main()
