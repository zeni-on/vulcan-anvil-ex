import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("vulcan_product_workflow_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class ProductWorkflowTests(unittest.TestCase):
    def test_result_and_status_columns_do_not_conceal_failures(self):
        for status, result, blocked in (("Fail", "Pass", True), ("Pass", "Fail", True),
                                        ("Pass", "Narrative smoke observations", False)):
            with self.subTest(status=status, result=result):
                report = self.report(execution=False) + (
                    "## Current Execution Result\n\n"
                    "| REG ID | Status | Result |\n| --- | --- | --- |\n"
                    f"| REG-001 | {status} | {result} |\n\n"
                    "| SEC-REG ID | Status | Result |\n| --- | --- | --- |\n"
                    "| SEC-REG-001 | Pass | Security smoke observations |\n"
                )
                issues = vulcan.product_verification_result_findings(report, "gate4", warnings=[])
                self.assertEqual(bool(issues), blocked, issues)
                if blocked:
                    self.assertTrue(any("conflicting Result/Status" in issue for issue in issues))
        root = self.project()
        path = self.run_file(root, body=(
            "\n## Current Verification\n\n"
            "| Command | Status | Result |\n| --- | --- | --- |\n"
            "| test | Fail | Pass |\n"
        ))
        self.assertTrue(vulcan.product_run_completion_findings(str(path))[0])

    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def project(self, profile="product", gate="impl"):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.write(root / "session.json", json.dumps({
            "profile": profile, "current_gate": gate, "project": "workflow-fixture",
            "implementation": {"waves": {"current": "", "items": []}},
        }))
        self.write(root / "vulcan.config.json", json.dumps({
            "delivery_profile": profile, "workflow": {"enabled": False},
        }))
        for path in vulcan.product_required_artifacts_for_gate(gate):
            self.write(root / path, "# Fixture\nSCN-001 REQ-001 SEC-001\n")
        self.write(root / "docs/product/REGRESSION_AND_RELEASE_REPORT.md", self.report())
        return root

    @staticmethod
    def report(result="Pass", security="Pass", execution=True):
        text = (
            "# Current Regression Report\n\n"
            "| REG ID | Target | Method |\n| --- | --- | --- |\n"
            "| REG-001 | SCN-001 | python -m unittest |\n\n"
            "| SEC-REG ID | Target | Method |\n| --- | --- | --- |\n"
            "| SEC-REG-001 | SEC-001 | python -m unittest |\n\n"
        )
        if execution:
            text += (
                "| REG ID | Result | Evidence |\n| --- | --- | --- |\n"
                f"| REG-001 | {result} | test.log |\n\n"
                "| SEC-REG ID | Result | Evidence |\n| --- | --- | --- |\n"
                f"| SEC-REG-001 | {security} | security.log |\n"
            )
        return text

    def run_file(self, root, name="RUN-001.md", gate="impl", skill="build-wave", status="Completed", bw="BW-001", body=""):
        path = root / "docs/runs" / name
        self.write(path, (
            "# Execution\n\n```yaml\nrun_id: RUN-001\nadapter: codex-gpt\n"
            f"profile: {vulcan.load_delivery_profile(str(root))}\ngate: {gate}\nskill: {skill}\n"
            f"persona: build\nrun_type: Implementation\nstatus: {status}\n"
            + (f"bw_id: {bw}\n" if bw else "")
            + "related_ids: [REQ-001]\nevidence: []\ntraceability_updates: []\nopen_issues: []\n"
            "verification_results:\n  - command: python -m unittest\n    result: passed\n    exit_code: 0\n"
            "```\n" + body
        ))
        return path

    def transition(self, root):
        output = io.StringIO()
        code = 0
        # Only fixture state is involved; suppress the unrelated stats rewrite.
        with contextlib.redirect_stdout(output), mock.patch.object(vulcan, "save_session"):
            try:
                vulcan.cmd_prepare_transition(str(root))
            except SystemExit as error:
                code = error.code
        return code, output.getvalue()

    def test_product_prose_and_deferred_plan_tables_do_not_create_waves(self):
        root = self.project()
        self.run_file(root, skill="implementation-plan", bw="", body=(
            "Deferred/excluded: BW-051 and BW-052.\n"
            "| Wave | Status |\n| --- | --- |\n| BW-051 | Planned |\n| BW-052 | Planned |\n"
        ))
        self.assertEqual(vulcan.collect_build_wave_records(str(root)), [])
        self.assertEqual(self.transition(root)[0], 0)

    def test_product_explicit_identity_ignores_other_ids_and_tables(self):
        root = self.project()
        self.run_file(root, name="RUN-001-BW-099.md", status="Failed", body=(
            "Do not execute BW-052.\n| Wave | Status |\n| --- | --- |\n| BW-001 | Completed |\n"
        ))
        records = vulcan.collect_build_wave_records(str(root))
        self.assertEqual([(r["id"], r["status"]) for r in records], [("BW-001", "Failed")])
        self.assertEqual(self.transition(root)[0], 1)

    def test_legacy_filename_requires_build_metadata(self):
        root = self.project()
        self.run_file(root, name="RUN-001_build-wave-BW-000_scaffold.md", skill="implementation-scaffold", bw="")
        self.run_file(root, name="RUN-002-BW-052.md", skill="implementation-plan", bw="")
        self.assertEqual([r["id"] for r in vulcan.collect_build_wave_records(str(root))], ["BW-000"])

    def test_duplicate_completed_run_cannot_hide_unfinished_wave(self):
        for status in ("Blocked", "Failed", "InProgress", "CompletedWithIssues", "Review Requested"):
            with self.subTest(status=status):
                root = self.project()
                self.run_file(root, status=status)
                self.run_file(root, name="RUN-002.md")
                records = vulcan.collect_build_wave_records(str(root))
                self.assertEqual(records[0]["status"], status)
                self.assertEqual(self.transition(root)[0], 1)

    def test_session_orphans_are_filtered_but_registered_unresolved_work_survives(self):
        root = self.project()
        session = vulcan.load_session(str(root))
        session["implementation"]["waves"]["items"] = [
            {"id": "BW-051", "status": "Planned", "run": ""},
            {"id": "BW-052", "status": "Planned", "run": ""},
        ]
        self.assertEqual(vulcan.compute_implementation_progress(str(root), session)["waves"]["total"], 0)
        self.assertEqual(vulcan.merge_session_wave_records(session, []), [])
        for status in ("InProgress", "Blocked", "Failed", "CompletedWithIssues", "Implemented", "Unknown"):
            with self.subTest(status=status):
                session["implementation"]["waves"]["items"][-1]["status"] = status
                progress = vulcan.compute_implementation_progress(str(root), session)["waves"]
                self.assertEqual(progress["total"], 1)
                self.assertEqual(progress["completed"], 0)
                self.assertEqual(progress["current"], "BW-052")
                self.write(root / "session.json", json.dumps(session))
                self.assertEqual(self.transition(root)[0], 1)
        session["implementation"]["waves"] = {"items": [], "current": "BW-053"}
        self.assertEqual(vulcan.compute_implementation_progress(str(root), session)["waves"]["total"], 1)

    def test_session_done_does_not_override_failed_run_and_registration_is_preserved(self):
        session = {"implementation": {"waves": {"items": [
            {"id": "BW-001", "status": "Completed"},
            {"id": "BW-002", "status": "Planned", "run": "docs/runs/missing.md"},
        ]}}}
        discovered = [{"id": "BW-001", "status": "Failed", "run": "actual.md", "related_ids": []}]
        merged = vulcan.merge_session_wave_records(session, discovered, profile="product")
        self.assertEqual([r["status"] for r in merged], ["Failed", "Planned"])
        session["implementation"]["waves"]["items"][0]["status"] = "Planned"
        self.assertEqual(vulcan.merge_session_wave_records(session, discovered, profile="product")[0]["status"], "Failed")

    def test_run_free_product_allows_outcomes_but_actual_failures_block(self):
        for gate in ("impl", "gate4", "gate5"):
            for result in ("Pass", "Fail", "Not Run", "environment_blocked", "Skipped"):
                with self.subTest(gate=gate, result=result):
                    root = self.project(gate=gate)
                    self.write(root / "docs/product/REGRESSION_AND_RELEASE_REPORT.md", self.report(result=result))
                    with mock.patch.object(vulcan, "run_preflight_file", side_effect=AssertionError("no preflight")):
                        code, output = self.transition(root)
                    self.assertEqual(code, 0 if result == "Pass" or (result == "Skipped" and gate == "impl") else 1, output)

    def test_required_docs_security_and_missing_execution_still_block(self):
        for change in ("doc", "security", "security-fail", "missing-results"):
            with self.subTest(change=change):
                root = self.project(gate="gate4")
                if change == "doc":
                    (root / "docs/product/PRODUCT_BRIEF.md").unlink()
                elif change == "security":
                    self.write(root / "docs/product/PRODUCT_CONTRACTS.md", "# No security contract\n")
                else:
                    self.write(root / "docs/product/REGRESSION_AND_RELEASE_REPORT.md", self.report(
                        security="Fail" if change == "security-fail" else "Pass", execution=change != "missing-results",
                    ))
                self.assertEqual(self.transition(root)[0], 1)
        self.assertEqual(vulcan.product_verification_result_findings(self.report(execution=False), "impl"), [])
        self.assertTrue(vulcan.product_verification_result_findings("REG-001 SEC-REG-001", "gate4"))

    def test_gate3_precreated_not_run_results_are_pending_not_failures(self):
        for value in ("Not Run", "not_run", "not-run", "not_executed", "미실행"):
            with self.subTest(value=value):
                warnings = []
                report = self.report(result=value, security=value)
                self.assertEqual(vulcan.product_verification_result_findings(report, "gate3", warnings), [])
                self.assertEqual(len(warnings), 1, warnings)
                self.assertIn("REG-001, SEC-REG-001", warnings[0])
                self.assertIn("Gate 4", warnings[0])
                for gate in ("impl", "gate4", "gate5", "completed"):
                    self.assertTrue(vulcan.product_verification_result_findings(report, gate, []), gate)

    def test_gate3_real_failures_and_conflicting_results_remain_blocking(self):
        for value in ("Fail", "Blocked", "environment_blocked", "environment-blocked"):
            with self.subTest(value=value):
                issues = vulcan.product_verification_result_findings(
                    self.report(result=value, security="Not Run"), "gate3", [],
                )
                self.assertTrue(any("REG-001:" in i and "blocks completion" in i for i in issues), issues)
        conflicting = self.report(result="Not Run") + self.result_table("Pass")
        self.assertTrue(any("contradictory" in i for i in
                            vulcan.product_verification_result_findings(conflicting, "gate3", [])))
        columns = "# Current Results\n| REG ID | Result | Status |\n| --- | --- | --- |\n| REG-001 | Not Run | Fail |\n"
        self.assertTrue(any("conflicting Result/Status" in i for i in
                            vulcan.product_verification_result_findings(columns, "gate3", [])))

    def test_gate3_inline_and_linked_not_run_results_reach_transition_without_rewriting(self):
        for split in (False, True):
            with self.subTest(split=split):
                root = self.project(gate="gate3")
                report = self.report(result="Not Run", security="Not Run")
                relative = "docs/artifacts/04-review/not-run/results.md" if split else "docs/product/REGRESSION_AND_RELEASE_REPORT.md"
                self.write(root / relative, report)
                if split:
                    self.write(root / "docs/product/REGRESSION_AND_RELEASE_REPORT.md",
                               "# Report\n[results](../artifacts/04-review/not-run/results.md)\n")
                before = {p: p.read_bytes() for p in root.rglob("*.md")}
                session = (root / "session.json").read_bytes()
                code, output = self.transition(root)
                self.assertEqual(code, 0, output)
                self.assertEqual(before, {p: p.read_bytes() for p in before})
                self.assertEqual(session, (root / "session.json").read_bytes())
                counts = vulcan._product_test_status_counts(str(root))
                self.assertEqual((counts["passed"], counts["pending"], counts["security"]["pending"]), (0, 1, 1))
                self.assertTrue(vulcan.collect_product_profile_findings(str(root), "gate4")[0])

    def test_completed_product_uses_output_checks_not_historical_readiness(self):
        root = self.project()
        path = self.run_file(root, body="\n```yaml\nverification:\n  cwd: removed-worktree\n  commands:\n    - TBD\n```\n")
        with mock.patch.object(vulcan, "run_preflight_file", side_effect=AssertionError("no preflight")), \
                mock.patch.object(vulcan, "check_run_file", wraps=vulcan.check_run_file) as check:
            code, output = self.transition(root)
        self.assertEqual(code, 0, output)
        check.assert_not_called()
        for replacement in ("result: failed", "result: not_run", "result: environment_blocked", "exit_code: 7"):
            self.run_file(root)
            content = path.read_text(encoding="utf-8")
            self.write(path, content.replace("exit_code: 0" if replacement.startswith("exit_code") else "result: passed", replacement))
            self.assertEqual(self.transition(root)[0], 1)
        self.run_file(root)
        self.write(path, path.read_text(encoding="utf-8").replace(
            "verification_results:\n  - command: python -m unittest\n    result: passed\n    exit_code: 0", "verification_results: []",
        ))
        self.assertEqual(self.transition(root)[0], 0)
        self.assertTrue(vulcan.product_run_completion_findings(str(path))[1])
        self.run_file(root)
        self.write(path, path.read_text(encoding="utf-8").replace(
            "    exit_code: 0", "    exit_code: 0\n  - command: required-security-check",
        ))
        self.assertEqual(self.transition(root)[0], 0)

    def test_recorded_approved_current_run_does_not_repeat_output_validation(self):
        root = self.project()
        self.run_file(root)
        with mock.patch.object(vulcan, "product_run_is_approved_history", return_value=True), \
                mock.patch.object(vulcan, "product_run_completion_findings", side_effect=AssertionError("historical revalidation")) as output_check:
            code, output = self.transition(root)
        self.assertEqual(code, 0, output)
        output_check.assert_not_called()

    def test_earlier_unfinished_run_still_blocks(self):
        root = self.project()
        self.run_file(root, gate="gate2", skill="orchestrator-plan", bw="", status="Blocked")
        self.assertEqual(self.transition(root)[0], 1)

    @staticmethod
    def result_table(status="Fail", result_id="REG-001", required="yes"):
        return (
            "\n| REG ID | Result | Required | Evidence |\n| --- | --- | --- | --- |\n"
            f"| {result_id} | {status} | {required} | test.log |\n"
        )

    def test_report_pass_explanation_does_not_become_substring_failure(self):
        for value in (
            "Pass; empty state verified, not run list appears empty",
            "Pass; 미실행 목록이 비어 있음",
            "Pass (failed-login rejection verified)",
        ):
            with self.subTest(value=value):
                warnings = []
                issues = vulcan.product_verification_result_findings(self.report(result=value, security=value), "gate4", warnings)
                self.assertEqual(issues, [])
                self.assertEqual(warnings, [])

    def test_report_history_cannot_veto_or_supply_current_results(self):
        for marker in ("## History\n### Execution Results\n", "## Old snapshot\n<!-- vulcan:state=history -->\n### Results\n"):
            with self.subTest(marker=marker):
                historical_failures = marker + self.result_table("Fail") + "\n" + self.result_table("environment_blocked", "SEC-REG-001")
                self.assertEqual(vulcan.product_verification_result_findings(self.report() + historical_failures, "gate4"), [])
                historical_passes = historical_failures.replace("Fail", "Pass").replace("environment_blocked", "Pass")
                issues = vulcan.product_verification_result_findings(self.report(execution=False) + historical_passes, "gate4")
                self.assertTrue(any("current execution results are missing" in issue for issue in issues))
        historic_plan = "\n## History\n### Regression Plan\n| REG ID | Method |\n| --- | --- |\n| REG-999 | old test |\n"
        self.assertEqual(vulcan.product_verification_result_findings(self.report() + historic_plan, "gate5"), [])
        nested = "\n## History\n### Execution Result\n" + self.result_table("Fail")
        self.assertEqual(vulcan.product_verification_result_findings(self.report() + nested, "gate4"), [])
        promoted = nested.replace("### Execution Result", "### Execution Result\n<!-- vulcan:state=current -->")
        self.assertTrue(vulcan.product_verification_result_findings(self.report() + promoted, "gate4"))

    def test_report_plan_candidate_and_unrelated_tables_are_not_executions(self):
        plan = "\n## Gate 3 Regression Plan\n" + self.result_table("Fail")
        candidate = "\n## Proposed results\n<!-- vulcan:state=candidate -->\n" + self.result_table("Fail")
        unrelated = "\n## Issues\n| Issue | Linked REG | Result |\n| --- | --- | --- |\n| ISSUE-001 | REG-001 | Fail |\n"
        self.assertEqual(vulcan.product_verification_result_findings(self.report() + plan + candidate + unrelated, "gate4"), [])
        missing = vulcan.product_verification_result_findings(self.report(execution=False) + plan + candidate, "gate4")
        self.assertTrue(missing)
        self.assertFalse(any("blocks completion" in issue for issue in missing))

    def test_report_unclassified_contradictions_require_classification(self):
        content = self.report() + "\n# Legacy Results\n" + self.result_table("Fail")
        issues = vulcan.product_verification_result_findings(content, "gate4")
        self.assertTrue(any("contradictory current/unclassified" in issue for issue in issues))
        # Neither physical ordering nor a later Pass resolves an unclassified conflict.
        reversed_content = "# Legacy Results\n" + self.result_table("Fail") + "\n" + self.report()
        self.assertTrue(any("contradictory" in issue for issue in vulcan.product_verification_result_findings(reversed_content, "gate4")))

    def test_report_ambiguous_optional_legacy_rows_warn_without_inventing_failure(self):
        warnings = []
        content = self.report() + self.result_table("Optional smoke was not run; manual signoff recorded", "REG-002", "no")
        self.assertEqual(vulcan.product_verification_result_findings(content, "gate4", warnings), [])
        self.assertTrue(any("manual review" in warning for warning in warnings))
        required = vulcan.product_verification_result_findings(self.report(result="Pass / Fail / Not Run"), "gate4", [])
        self.assertTrue(any("missing successful current" in issue for issue in required))

    def test_run_legacy_done_absent_results_and_metadata_only_warn(self):
        root = self.project()
        path = root / "docs/runs/legacy.md"
        for content in (
            "# Legacy summary\n```yaml\nstatus: Done\n```\nScoped changes verified; no structured output was used.\n",
            "# Legacy summary\nOptional smoke mixed Pass/Fail notes; manual decision retained.\n",
            "# Result\n```yaml\nstatus: Done\nverification_results: []\n```\n",
        ):
            with self.subTest(content=content):
                self.write(path, content)
                with mock.patch.object(vulcan, "check_run_file", side_effect=AssertionError("no retroactive run-check")):
                    issues, warnings = vulcan.product_run_completion_findings(str(path))
                self.assertEqual(issues, [])
                self.assertTrue(warnings)

    def test_run_explicit_failure_and_blocker_survive_without_new_metadata(self):
        root = self.project()
        path = root / "docs/runs/legacy.md"
        for output in (
            "status: Blocked", "status: Failed",
            "verification_results:\n  - result: Fail", "verification_results:\n  - status: environment_blocked",
            "verification_results:\n  - command: smoke\n    exit_code: 1",
            "open_issues:\n  - id: ISSUE-001\n    status: open\n    blocking: true",
        ):
            with self.subTest(output=output):
                self.write(path, "# Current Result\n```yaml\n" + output + "\n```\n")
                self.assertTrue(vulcan.product_run_completion_findings(str(path))[0])

    def test_run_waived_nonblocking_open_issues_are_not_automatic_blockers(self):
        root = self.project()
        for fields in ("status: waived", "blocking: false\n    status: blocked", "blocking: true\n    waived: true", "status: nonblocking"):
            path = self.run_file(root)
            content = path.read_text(encoding="utf-8").replace("open_issues: []", "open_issues:\n  - id: ISSUE-001\n    " + fields)
            self.write(path, content)
            issues, warnings = vulcan.product_run_completion_findings(str(path))
            self.assertEqual(issues, [], fields)
            self.assertTrue(any("manual triage" in warning for warning in warnings))

    def test_run_history_is_not_current_failure_and_pass_explanations_are_safe(self):
        root = self.project()
        path = self.run_file(root)
        original = path.read_text(encoding="utf-8").replace("result: passed", "result: 'Pass; empty state verified, not run list appears empty; 미실행 없음'")
        history = (
            "\n## History\n### Verification Results\n```yaml\nverification_results:\n"
            "  - result: failed\n    exit_code: 3\n```\n"
            "\n| Command | Result |\n| --- | --- |\n| old smoke | Fail |\n"
        )
        for heading in ("## History", "## Earlier snapshot\n<!-- vulcan:state=history -->"):
            self.write(path, original + history.replace("## History", heading))
            self.assertEqual(vulcan.product_run_completion_findings(str(path))[0], [])
        self.write(path, original + history.replace("## History", "## Unclassified results"))
        self.assertTrue(vulcan.product_run_completion_findings(str(path))[0])
        self.write(path, original + history.replace("### Verification Results", "### Verification Results\n<!-- vulcan:state=current -->"))
        self.assertTrue(vulcan.product_run_completion_findings(str(path))[0])

    def history(self, root, gate="gate4"):
        session = vulcan.load_session(str(root))
        session["gate_status"] = {gate: "done"}
        session["approvals"] = {gate: {"approved_at": "2026-08-01T10:00:00",
                                     "approval_evidence": "Explicit user approval"}}
        self.write(root / "session.json", json.dumps(session))
        return self.run_file(root, gate=gate, skill="qa-execution" if gate == "gate4" else "release-approval", bw="")

    def test_recorded_approved_future_runs_are_history_without_git(self):
        for current in ("impl", "gate2", "gate3"):
            for gate in ("gate4", "gate5"):
                with self.subTest(current=current, gate=gate):
                    root = self.project(gate=current)
                    self.history(root, gate)
                    with mock.patch.object(vulcan, "git_text", side_effect=AssertionError("no history lookup")):
                        self.assertEqual(vulcan.validate_gate_progression(str(root), current), [])

    def test_active_or_unapproved_future_runs_are_not_approved(self):
        for variant in ("inprogress", "no-approval", "no-evidence", "bad-timestamp", "not-done"):
            with self.subTest(variant=variant):
                root = self.project()
                path = self.history(root)
                if variant == "inprogress":
                    content = path.read_text(encoding="utf-8")
                    self.write(path, content.replace("status: Completed", "status: InProgress"))
                else:
                    session = vulcan.load_session(str(root))
                    if variant == "no-approval":
                        session["approvals"] = {}
                    elif variant == "not-done":
                        session["gate_status"]["gate4"] = "in-progress"
                    else:
                        field = "approval_evidence" if variant == "no-evidence" else "approved_at"
                        session["approvals"]["gate4"][field] = ""
                    self.write(root / "session.json", json.dumps(session))
                issues = vulcan.validate_gate_progression(str(root), "impl")
                self.assertTrue(issues)
                self.assertTrue(any("recorded Gate completion and approval" in issue for issue in issues))

    def test_audit_poc_discovery_merge_and_future_gate_rules_are_unchanged(self):
        for profile in ("audit", "poc"):
            with self.subTest(profile=profile):
                root = self.project(profile=profile)
                self.run_file(root, skill="implementation-plan", bw="", body="Deferred BW-051\n| Wave | Status |\n| --- | --- |\n| BW-052 | Planned |\n")
                self.assertEqual([r["id"] for r in vulcan.collect_build_wave_records(str(root))], ["BW-051", "BW-052"])
                session = {"implementation": {"waves": {"items": [{"id": "BW-053", "status": "Planned"}]}}}
                self.assertEqual(len(vulcan.merge_session_wave_records(session, [], profile=profile)), 1)
                self.run_file(root, name="RUN-002.md", gate="gate4", bw="")
                self.assertTrue(vulcan.validate_gate_progression(str(root), "impl"))

    def test_audit_poc_transition_preflight_is_preserved(self):
        for profile in ("audit", "poc"):
            root = self.project(profile=profile)
            path = self.run_file(root)
            with mock.patch.object(vulcan, "run_preflight_file", return_value=(["sentinel preflight blocker"], [])) as preflight:
                code, output = self.transition(root)
            preflight.assert_called_once_with(str(path))
            self.assertEqual(code, 1)
            self.assertIn("sentinel preflight blocker", output)

    def test_external_execution_and_explicit_preflight_still_block_before_launch(self):
        root = self.project()
        path = self.run_file(root, status="InProgress")
        for entry in ("run-exec", "agent-run", "run-preflight"):
            with self.subTest(entry=entry), contextlib.redirect_stdout(io.StringIO()), \
                    mock.patch.object(vulcan, "workflow_branch_guard"), \
                    mock.patch.object(vulcan, "run_preflight_file", return_value=(["scope blocker"], [])) as preflight, \
                    mock.patch.object(vulcan.subprocess, "Popen", side_effect=AssertionError("must not launch")):
                with self.assertRaises(SystemExit) as raised:
                    if entry == "run-exec":
                        vulcan.cmd_run_exec("RUN-001", project_dir=str(root))
                    elif entry == "agent-run":
                        vulcan.cmd_agent_run("work", run_id="RUN-001", project_dir=str(root))
                    else:
                        vulcan.cmd_run_preflight(str(path))
                self.assertEqual(raised.exception.code, 1)
                preflight.assert_called_once_with(str(path))

    def test_product_direct_edit_is_not_limited_by_actor_size_bookkeeping(self):
        body = (
            "\nimplementation-complete\n\n```yaml\n"
            "orchestrator_direct_edit_reason: Authorized bounded work\n"
            "direct_edit_scope:\n  files:\n    - a.py\n    - b.py\n    - c.py\n"
            "  estimated_loc: 500\n  contract_changed: true\n```\n"
        )
        for profile in ("product", "audit", "poc"):
            root = self.project(profile=profile)
            path = self.run_file(root, body=body)
            for checker in (vulcan.check_run_file, vulcan.run_preflight_file):
                issues, warnings = checker(str(path))
                limits = [item for item in issues + warnings if "Orchestrator 직접 구현 예외" in item]
                self.assertEqual(bool(limits), profile != "product", limits)
            if profile == "product":
                blockers, _ = vulcan.run_preflight_file(str(path))
                self.assertTrue(any("target_contracts" in item for item in blockers))
                self.write(path, path.read_text(encoding="utf-8") + "\n```yaml\nscope:\n  writable:\n    - session.json\n```\n")
                self.assertTrue(any("session.json" in item for item in vulcan.run_preflight_file(str(path))[0]))


if __name__ == "__main__":
    unittest.main()
