"""Pilot consumers preserve legacy behavior and never infer release authority."""

from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

from vulcan_core import product_consumers as consumers, product_process as process
import test_product_process as helpers
import test_product_session as sessions


class ProductConsumerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = sessions.ProductSessionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.workflow = {"integration_branch": "dev-happy", "main_branch": "main"}
        self.fixture.fixture.write("vulcan.config.json", json.dumps({"workflow": self.workflow}))

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.strip()

    def repository(self):
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Regression")
        self.git("config", "user.email", "regression@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.commit()

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "--allow-empty", "-m", "fixture")

    def complete(self):
        self.fixture.acceptance()
        verification = self.fixture.observed_results()
        key = process.verification_key(self.fixture.read()["current_work"]["scope"], verification,
                                       self.fixture.fixture.basis())
        self.fixture.apply(self.fixture.request("advance", target="completed", verification=verification,
            decision=helpers.decision(self.fixture.read(), ["accept"], verification_key=key)))

    def files(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(self.root).parts}

    def test_status_and_branch_consumer_show_real_state_without_writing(self):
        self.repository()
        self.fixture.implementation()
        before = self.files()
        result = self.fixture.cli(["branch-status"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("current_gate: impl", result.stdout)
        self.assertIn("branch_status: mismatch", result.stdout)
        status = self.fixture.cli(["status", "--json"])
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(json.loads(status.stdout)["branch"]["integration_branch"], "dev-happy")
        self.assertEqual(self.files(), before)
        self.assertEqual(self.git("branch", "--show-current"), "main")

    def test_acceptance_verification_rejects_wrong_branch_before_command(self):
        self.repository()
        self.fixture.acceptance()
        (self.root / "evidence").mkdir()
        args = ["execute", "--verify", "--source", "app.py", "--evidence", "evidence/no.json", "--",
                sys.executable, "-c", "from pathlib import Path; Path('executed').touch()"]
        result = self.fixture.cli(args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("agreed integration branch", result.stderr)
        self.assertFalse((self.root / "executed").exists())
        self.assertFalse((self.root / "evidence/no.json").exists())
        self.git("checkout", "-b", "dev-happy")
        result = self.fixture.cli(args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "executed").exists())
        self.assertEqual(self.fixture.read()["current_gate"], "acceptance")
        self.assertFalse((self.root / ".vulcan/worktrees").exists())

    def test_impl_self_check_on_worker_branch_and_single_workspace_are_allowed(self):
        self.repository()
        self.fixture.implementation()
        self.git("checkout", "-b", "worker/check")
        observation = self.fixture.observed_results()
        self.assertTrue(observation["results"])
        context = consumers.branch_context(self.root, self.fixture.read(), {**self.workflow, "branch_mode": "single"})
        self.assertEqual(context["branch_status"], "not_required")
        self.assertFalse(context["qa_worktree_created"])

    def test_cross_project_verification_checks_target_workflow_not_caller(self):
        self.repository()
        self.fixture.acceptance()
        (self.root / "evidence").mkdir()
        caller = self.root / "caller"
        caller.mkdir()
        (caller / "vulcan.config.json").write_text(json.dumps({"workflow": {"branch_mode": "single"}}), encoding="utf-8")
        args = [sys.executable, str(helpers.ROOT / "vulcan.py"), "execute", "--verify",
                "--project-dir", str(self.root), "--source", "app.py", "--evidence", "evidence/cross.json", "--",
                sys.executable, "-c", "from pathlib import Path; Path('executed').touch()"]
        denied = subprocess.run(args, cwd=caller, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(denied.returncode, 2, denied.stdout + denied.stderr)
        self.assertFalse((self.root / "executed").exists())
        self.git("checkout", "-b", "dev-happy")
        (caller / "vulcan.config.json").write_text(json.dumps({"workflow": {"integration_branch": "other"}}), encoding="utf-8")
        allowed = subprocess.run(args, cwd=caller, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
        self.assertTrue((self.root / "executed").exists())

    def test_non_git_pilot_can_verify_but_is_not_a_release_candidate(self):
        self.complete()
        result = consumers.release_preview(self.root, self.fixture.read(), self.workflow, self.fixture.parse)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["branch"]["repository"])
        self.assertFalse(result["release_authorized"])

    def test_detached_head_and_parent_git_repository_are_not_matched(self):
        self.repository()
        self.fixture.acceptance()
        self.git("checkout", "--detach")
        with self.assertRaisesRegex(ValueError, "agreed integration"):
            consumers.require_qa_workspace(self.root, self.fixture.read(), self.workflow)
        child = self.root / "nested"
        child.mkdir()
        context = consumers.branch_context(child, self.fixture.read(), self.workflow)
        self.assertFalse(context["repository"])
        self.assertEqual(context["branch_status"], "unavailable")
        with self.assertRaisesRegex(ValueError, "Git workspace root"):
            consumers.require_qa_workspace(child, self.fixture.read(), self.workflow)

    def test_release_preview_preserves_files_and_never_grants_publication(self):
        self.repository()
        self.git("checkout", "-b", "dev-happy")
        self.complete()
        session = self.fixture.read()
        session["open_issues"] = ["unrelated deferred obligation"]
        self.fixture.path.write_text(json.dumps(session), encoding="utf-8")
        dirty = consumers.release_preview(self.root, session, self.workflow, self.fixture.parse)
        self.assertEqual(dirty["status"], "blocked")
        self.assertTrue(any("clean" in item for item in dirty["blockers"]))
        self.commit()
        before = self.files()
        result = consumers.release_preview(self.root, session, self.workflow, self.fixture.parse)
        self.assertEqual(result["status"], "candidate", result)
        self.assertEqual(result["unresolved_obligations"], 1)
        self.assertFalse(result["publication_enabled"])
        self.assertFalse(result["release_authorized"])
        cli = self.fixture.cli(["release-pr", "--dry-run"])
        self.assertEqual(cli.returncode, 0, cli.stdout + cli.stderr)
        self.assertIn("Product release preview: candidate", cli.stdout)
        self.assertNotIn("Gate 5", cli.stdout)
        self.assertEqual(self.files(), before)
        self.assertFalse((self.root / ".vulcan/release").exists())
        publication = self.fixture.cli(["release-pr", "--no-push"])
        self.assertEqual(publication.returncode, 2)
        self.assertEqual(self.files(), before)

    def test_release_preview_rechecks_current_evidence_and_scope(self):
        self.repository()
        self.git("checkout", "-b", "dev-happy")
        self.complete()
        self.commit()
        self.fixture.fixture.write("app.py", "value = 2\n")
        result = consumers.release_preview(self.root, self.fixture.read(), self.workflow, self.fixture.parse)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["checks"]["execution"], "missing_stale_or_failed")
        self.assertFalse(result["release_authorized"])

    def test_revision_expressions_are_not_release_branches(self):
        self.repository()
        self.git("checkout", "-b", "dev-happy")
        self.complete()
        self.commit()
        for base in ("main~0", "main^{commit}", "main@{0}", "--help"):
            with self.subTest(base=base):
                result = consumers.release_preview(self.root, self.fixture.read(), self.workflow,
                                                   self.fixture.parse, base=base)
                self.assertEqual(result["status"], "blocked", result)
                self.assertIn("local branch not found: " + base, result["blockers"])

    def test_preacceptance_preview_blocked_and_legacy_writers_remain_disabled(self):
        self.fixture.start()
        before = self.files()
        preview = self.fixture.cli(["release-pr", "--dry-run"])
        self.assertEqual(preview.returncode, 1, preview.stdout + preview.stderr)
        self.assertIn("has not been accepted", preview.stdout)
        for args in (["branch-start", "impl"], ["gate-start", "gate4"], ["sync-session"]):
            with self.subTest(args=args):
                result = self.fixture.cli(args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.files(), before)

    def test_doctor_uses_environment_report_not_legacy_gate_checks(self):
        self.fixture.start()
        before = self.files()
        with mock.patch.object(helpers.vulcan, "run_doctor", return_value=0) as doctor, \
                mock.patch.object(helpers.vulcan, "load_session", side_effect=AssertionError("no legacy load")):
            helpers.vulcan.cmd_doctor(self.root, emit_json=True)
        doctor.assert_called_once_with(str(self.root), delivery_profile="product", emit_json=True)
        self.assertEqual(self.files(), before)

    def test_unknown_or_malformed_model_is_not_downgraded_by_consumers(self):
        self.fixture.start()
        original = self.fixture.read()
        for mutate in (lambda x: x.update(process_model="future"),
                       lambda x: x["gate_status"].update(gate4="done"),
                       lambda x: x.update(profile="audit")):
            session = deepcopy(original)
            mutate(session)
            self.fixture.path.write_text(json.dumps(session), encoding="utf-8")
            before = self.files()
            for args in (["branch-status"], ["doctor", "--json"], ["release-pr", "--dry-run"]):
                with self.subTest(args=args):
                    result = self.fixture.cli(args)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(self.files(), before)

    def test_absent_marker_retains_legacy_dispatch(self):
        self.fixture.path.write_text(json.dumps({"profile": "product", "current_gate": "gate2"}), encoding="utf-8")
        self.assertIsNone(consumers.load(self.root))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            helpers.vulcan.cmd_branch_status(self.root)
        self.assertIn("Vulcan workflow branch status", output.getvalue())
        self.assertIn("current_gate: gate2", output.getvalue())

    def test_legacy_consumer_does_not_apply_pilot_size_or_strict_decode(self):
        self.fixture.path.write_text(json.dumps({"profile": "product", "current_gate": "gate2",
                                                "notes": "x" * 8_000_001}), encoding="utf-8")
        self.assertIsNone(consumers.load(self.root))
        result = self.fixture.cli(["branch-status"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
