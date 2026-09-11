"""Actual scoped documents and command observations, with no project activation."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from vulcan_core import product_process as process, product_readiness as checks
from vulcan_core.evidence import capture_source_snapshot, record_verification
from test_product_process import ROOT, decision, ready, vulcan


CONTRACT = """# Request Board
## Resubmit
| ID | Definition |
| --- | --- |
| SCN-001 | Amend and resubmit the same request. |
| REQ-001 | Preserve the rejected content and rejection reason. |

## Future Feature
<!-- vulcan:state=candidate -->
| ID | Definition |
| --- | --- |
| REQ-099 | TBD |

## Security
| ID | Definition |
| --- | --- |
| SEC-001 | Only the owner can resubmit. |
"""
PLAN = """# Verification Plan
## Resubmit
| REG ID | Method | Expected | Status |
| --- | --- | --- | --- |
| REG-001 | Run request assertions | Previous reason remains | Planned |
| SEC-REG-001 | Run access assertions | Another user is denied | Planned |

## Later
<!-- vulcan:state=candidate -->
| REG ID | Method | Expected |
| --- | --- | --- |
| REG-099 | TBD | TBD |
"""


class ScopedReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("docs/contracts.md", CONTRACT)
        self.write("docs/tests.md", PLAN)
        self.write("app.py", "value = 1\n")
        self.write("tests/check.py", "from pathlib import Path\nassert 'value = 1' in Path('app.py').read_text()\n")
        self.write("requirements.txt", "# Standard library only\n")
        self.write("environment.json", json.dumps({"python": sys.version, "services": "none"}))
        self.sources = ["app.py", "tests", "requirements.txt", "environment.json"]
        self.scope = {"work": {"ref": "issue:request-resubmit", "revision": "snapshot:1"},
            "related_ids": ["SCN-001", "REQ-001", "SEC-001"],
            "contracts": [self.ref("docs/contracts.md#resubmit")],
            "tests": [self.ref("docs/tests.md#resubmit")], "required_checks": ["REG-001", "SEC-REG-001"]}

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")

    def ref(self, path):
        return checks.local_reference(self.root, path, markdown=".md" in path)

    def basis(self):
        return {"source": capture_source_snapshot(self.root, self.sources), "environment": self.ref("environment.json")}

    def session(self):
        return process.new_session(self.scope)

    def collect(self, session=None):
        return checks.collect(self.root, session or self.session(), vulcan.parse_markdown_tables)

    def assert_blocked(self, result, text):
        self.assertEqual(result["status"], "blocked", result)
        self.assertIn(text, json.dumps(result["issues"]))
        if result["transition"]:
            self.assertFalse(result["transition"]["allowed"])

    def execution_session(self):
        session = self.session()
        session = process.advance(session, "impl", readiness=ready(session), decision=decision(session))
        session = process.advance(session, "acceptance", readiness=ready(session, "handoff"), current_basis=self.basis())
        command = [sys.executable, "tests/check.py"]
        (self.root / "evidence").mkdir()
        _, code = record_verification(self.root, self.sources, "evidence/execution.json", command)
        self.assertEqual(code, 0)
        session["current_work"]["verification"] = {"scope_key": session["current_work"]["scope_key"], "basis": self.basis(),
            "results": [{"id": name, "status": "Pass", "command": command,
                         "evidence": self.ref("evidence/execution.json")} for name in self.scope["required_checks"]]}
        return session

    def test_planning_allows_planned_tests_and_unrelated_future_drafts(self):
        session = self.session()
        before = deepcopy(session)
        result = self.collect(session)
        self.assertEqual(result["status"], "ready", result)
        self.assertEqual(result["execution"], "not_required_at_this_stage")
        self.assertFalse(result["transition"]["allowed"])
        self.assertIn("missing scoped implement", str(result["transition"]))
        self.assertEqual(len(result["documents"]), 2)
        self.assertEqual(result["common_context"][0]["heading"], "Security")
        session["current_work"]["decisions"].append(decision(session))
        self.assertTrue(self.collect(session)["transition"]["allowed"])
        self.assertEqual(before["current_work"]["decisions"], [])

    def test_missing_and_mentioned_ids_do_not_become_definitions(self):
        self.write("docs/contracts.md", CONTRACT.replace("| REQ-001 | Preserve the rejected content and rejection reason. |", "Mention only REQ-001."))
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assert_blocked(self.collect(), "REQ-001 needs a primary-ID table row")

    def test_commented_definitions_and_links_are_not_current_sources(self):
        hidden = "<!--\n| ID | Definition |\n| --- | --- |\n| REQ-001 | hidden |\n[Hidden](missing.md)\n-->"
        self.write("docs/contracts.md", CONTRACT.replace("| REQ-001 | Preserve the rejected content and rejection reason. |", "") + "\n## Hidden\n" + hidden)
        self.scope["contracts"] = [self.ref("docs/contracts.md")]
        result = self.collect()
        self.assert_blocked(result, "REQ-001 needs a primary-ID table row")
        self.assertNotIn("unbound_reference", str(result["issues"]))
        self.write("docs/tests.md", "# Verification Plan\n" + "<!--\n" + PLAN + "\n-->")
        self.scope["tests"] = [self.ref("docs/tests.md")]
        self.assert_blocked(self.collect(), "REG-001 needs a primary-ID table row")

    def test_link_budget_overflow_blocks_instead_of_dropping_uninspected_sources(self):
        names = ["term-" + str(i) for i in range(checks.MAX_LINKS + 1)]
        self.write("docs/common.md", "\n".join("## " + name + "\nCurrent rule." for name in names))
        links = "\n".join("[Rule](common.md#" + name + ")" for name in names) + "\n[Uninspected](missing.md)"
        self.write("docs/contracts.md", CONTRACT.replace("## Resubmit", "## Resubmit\n" + links))
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit"), self.ref("docs/common.md")]
        self.assert_blocked(self.collect(), "link_limit")

    def test_comment_example_in_code_fence_does_not_hide_current_definitions(self):
        self.write("docs/contracts.md", "```html\n<!-- example comment opener\n```\n" + CONTRACT)
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assertEqual(self.collect()["status"], "ready")

    def test_inline_comment_example_cannot_hide_shared_security_constraints(self):
        for literal in ("`<!--`", "``a ` <!--``", "`<!--\nexample`", r"\`<!-- real comment -->"):
            content = CONTRACT.replace("## Security", "The opening token is " + literal + ".\n\n## Security")
            self.write("docs/contracts.md", content.replace("Only the owner can resubmit.", "TBD"))
            self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
            self.scope["related_ids"] = ["REQ-001", "SCN-001"]
            self.assert_blocked(self.collect(), "SEC-001 needs a substantive definition")

    def test_incomplete_plan_reports_the_actual_row_and_does_not_demand_execution(self):
        self.write("docs/tests.md", PLAN.replace("Previous reason remains", "TBD"))
        self.scope["tests"] = [self.ref("docs/tests.md#resubmit")]
        result = self.collect()
        self.assert_blocked(result, "expected outcome")
        issue = next(i for i in result["issues"] if i["code"] == "incomplete_test_plan")
        self.assertEqual((issue["path"], issue["line"]), ("docs/tests.md", 5))
        self.assertEqual(result["execution"], "not_required_at_this_stage")

    def test_shared_security_is_not_hidden_by_feature_anchor(self):
        self.scope["related_ids"].remove("SEC-001")
        self.write("docs/contracts.md", CONTRACT.replace("Only the owner can resubmit.", "TBD"))
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assert_blocked(self.collect(), "SEC-001 needs a substantive definition")

    def test_whole_file_revision_conservatively_detects_sibling_changes(self):
        self.write("docs/contracts.md", CONTRACT.replace("REQ-099", "REQ-098"))
        self.assert_blocked(self.collect(), "document revision changed")
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assertEqual(self.collect()["status"], "ready")

    def test_candidate_history_missing_anchor_and_conflicts_block(self):
        for state in ("candidate", "history"):
            self.write("docs/contracts.md", CONTRACT.replace("## Resubmit", "## Resubmit\n<!-- vulcan:state=" + state + " -->"))
            self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
            self.assert_blocked(self.collect(), "candidate/history")
        self.write("docs/contracts.md", CONTRACT)
        self.scope["contracts"] = [self.ref("docs/contracts.md#missing")]
        self.assert_blocked(self.collect(), "anchor does not exist")
        self.write("docs/contracts.md", CONTRACT.replace("## Resubmit", "## Resubmit\n<!-- vulcan:state=current -->\n<!-- vulcan:state=history -->"))
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assert_blocked(self.collect(), "conflicting_state")

    def test_bound_links_resolve_and_unbound_sources_do_not_silently_disappear(self):
        self.write("docs/common.md", "# Retention\nPreserve all rejection snapshots.\n")
        self.write("docs/contracts.md", CONTRACT.replace("## Resubmit", "## Resubmit\n[Retention](common.md#retention)\n"))
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assert_blocked(self.collect(), "unbound_reference")
        self.scope["contracts"].append(self.ref("docs/common.md#retention"))
        self.assertEqual(self.collect()["status"], "ready")
        self.write("docs/common.md", "# Retention\nNew requirement.\n")
        self.assert_blocked(self.collect(), "document revision changed")

    def test_path_traversal_remote_oversized_and_symlink_are_not_read(self):
        for path in ("../outside.md", "C:/outside.md", "https://example.test/contract.md", "docs/%2e%2e/%2e%2e/outside.md", "docs/contracts.md?query=yes"):
            self.scope["contracts"] = [{"ref": path, "revision": "sha256:" + "0" * 64}]
            self.assert_blocked(self.collect(), "invalid_reference")
        self.write("docs/large.md", "x" * (checks.MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            self.ref("docs/large.md")

    def test_symlink_reference_is_rejected(self):
        try:
            (self.root / "docs/alias.md").symlink_to(self.root / "docs/contracts.md")
        except OSError:
            self.skipTest("local symlink creation unavailable")
        with self.assertRaises(ValueError):
            self.ref("docs/alias.md")

    def test_duplicate_definitions_and_reference_budget_are_diagnosed(self):
        self.write("docs/contracts.md", CONTRACT.replace("| REQ-001 |", "| REQ-001 | Different rule |\n| REQ-001 |"))
        self.scope["contracts"] = [self.ref("docs/contracts.md#resubmit")]
        self.assert_blocked(self.collect(), "conflicting_definition")
        self.scope["contracts"] = [{"ref": "docs/x" + str(i) + ".md", "revision": "snapshot:1"} for i in range(33)]
        self.assert_blocked(self.collect(), "reference_limit")

    def test_handoff_observes_sources_but_is_not_acceptance(self):
        session = self.session()
        session = process.advance(session, "impl", readiness=ready(session), decision=decision(session))
        self.assert_blocked(self.collect(session), "verification basis")
        session["current_work"]["basis"] = self.basis()
        result = self.collect(session)
        self.assertEqual(result["status"], "ready", result)
        self.assertTrue(result["transition"]["allowed"])
        self.assertEqual(result["execution"], "not_required_at_this_stage")
        self.assertFalse(result["release_authorized"])

    def test_real_execution_reports_are_distinct_from_acceptance_permission(self):
        session = self.execution_session()
        session["open_issues"] = ["ISSUE-OTHER: not resolved by this scoped result"]
        before = deepcopy(session)
        result = self.collect(session)
        self.assertEqual(result["status"], "ready", result)
        self.assertEqual(result["execution"], "verified_observations")
        self.assertFalse(result["transition"]["allowed"])
        self.assertEqual(result["unresolved_obligations"], 1)
        self.assertEqual(session, before)
        accept = decision(session, ["accept"], verification_key=result["verification_key"])
        session["current_work"]["decisions"].append(accept)
        self.assertTrue(self.collect(session)["transition"]["allowed"])
        complete = process.advance(session, "completed", verification=session["current_work"]["verification"], current_basis=self.basis())
        checked = self.collect(complete)
        self.assertEqual(checked["status"], "ready")
        self.assertFalse(checked["release_authorized"])
        self.assertIsNone(checked["transition"])

    def test_source_test_dependency_and_environment_changes_block_old_evidence(self):
        session = self.execution_session()
        for path in ("app.py", "tests/check.py", "requirements.txt", "environment.json"):
            original = (self.root / path).read_bytes()
            self.write(path, "changed")
            self.assert_blocked(self.collect(session), "invalid_execution_basis")
            (self.root / path).write_bytes(original)
        self.write("unrelated-notes.md", "Unrelated wording correction.")
        self.assertEqual(self.collect(session)["status"], "ready")

    def test_environment_manifest_must_be_part_of_execution_observation(self):
        self.sources.remove("environment.json")
        self.assert_blocked(self.collect(self.execution_session()), "include the environment manifest")

    def test_missing_failed_and_incomplete_results_never_pass(self):
        session = self.execution_session()
        for status in ("Planned", "Not Run", "environment_blocked", "Fail"):
            altered = deepcopy(session)
            altered["current_work"]["verification"]["results"][0]["status"] = status
            self.assert_blocked(self.collect(altered), "not Pass")
        altered = deepcopy(session)
        altered["current_work"]["verification"]["results"].pop()
        self.assert_blocked(self.collect(altered), "cover each required check")
        for value in (None, [], {}, "Pass"):
            altered = deepcopy(session)
            altered["current_work"]["verification"] = value
            self.assert_blocked(self.collect(altered), "invalid_execution_basis")

    def test_fake_log_and_modified_execution_record_are_rejected_without_running_commands(self):
        session = self.execution_session()
        report_path = self.root / "evidence/execution.json"
        original = json.loads(report_path.read_text())
        self.write("evidence/execution.json", "Pass")
        self.assert_blocked(self.collect(session), "revision changed")
        for value in ("Pass", [], {}, dict(original, source_changed=True), dict(original, identity_complete=False),
                      dict(original, command=dict(original["command"], exit_code=1)),
                      dict(original, command=dict(original["command"], exit_code=False)),
                      dict(original, command=dict(original["command"], argv=["NEVER_EXECUTE_THIS"]))):
            self.write("evidence/execution.json", json.dumps(value))
            for row in session["current_work"]["verification"]["results"]:
                row["evidence"] = self.ref("evidence/execution.json")
            self.assert_blocked(self.collect(session), "invalid_execution_basis")

    def test_status_check_is_read_only_and_exit_zero_does_not_mean_approval(self):
        self.write("session.json", json.dumps(self.session()))
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        command = [sys.executable, str(ROOT / "vulcan.py"), "status", "--check", "--json"]
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        self.assertFalse(summary["runtime_enabled"])
        self.assertTrue(summary["checks_enabled"])
        self.assertFalse(summary["scoped_check"]["transition"]["allowed"])
        text = checks.render(summary["scoped_check"])
        self.assertIn("transition eligibility: False -> impl", text)
        self.assertIn("no approval", text)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)
        self.write("docs/contracts.md", "# Changed\n")
        result = subprocess.run(command, cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["scoped_check"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
