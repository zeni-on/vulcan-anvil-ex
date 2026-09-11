"""Real Git/CLI recovery scenarios; synthetic approval, no external publishing."""

from copy import deepcopy
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from product_execution_fixture import ExecutionProject, FIXED_APP, PLAN
from vulcan_core import product_consumers
from test_product_process import vulcan


class ProductExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="product-execution-")
        self.addCleanup(self.temp.cleanup)
        self.project = ExecutionProject(self.temp.name)
        self.project.create()
        self.root = self.project.root

    def session_bytes(self):
        return (self.root / "session.json").read_bytes()

    def submit(self, request, code):
        before = self.session_bytes()
        result = self.project.cli("session", "--process-request", "-", "--json", "--apply", request=request)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        if code:
            self.assertEqual(self.session_bytes(), before)
        return json.loads(result.stdout)

    def pass_and_accept(self):
        self.project.fix()
        result = self.project.verify("passing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        verification = self.project.results("passing")
        self.project.apply(self.project.completion(verification))
        self.project.commit("fixture: scoped acceptance, not release authority")
        return verification

    def test_actual_failure_fix_retest_and_old_acceptance_key_rejected(self):
        before = self.session_bytes()
        failed = self.project.verify("failed")
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertIn("FAILED (failures=1)", failed.stderr)
        self.assertEqual(self.session_bytes(), before)
        failure_ref = self.project.ref("evidence/failed.json")
        # Even a worker's forged Pass summary cannot overrule exit_code=1.
        forged = self.project.results("failed")
        old_request = self.project.completion(forged)
        blocked = self.submit(old_request, 1)
        self.assertIn("unsuccessful", str(blocked))
        self.project.fix()
        # A rejected completion never stored these fields in the first place.
        for field in ("verification", "verification_key"):
            self.assertNotIn(field, self.project.state()["current_work"])
        stale = self.project.completion(forged)
        self.assertIn("stale", str(self.submit(stale, 1)))
        passed = self.project.verify("retest")
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        self.assertIn("Ran 3 tests", passed.stderr)
        self.assertIn("OK", passed.stderr)
        verification = self.project.results("retest")
        no_approval = self.project.request("advance", target="completed", verification=verification)
        self.assertIn("missing scoped accept", str(self.submit(no_approval, 1)))
        wrong_approval = {**no_approval, "decision": old_request["decision"]}
        self.assertIn("missing scoped accept", str(self.submit(wrong_approval, 1)))
        self.project.apply(self.project.completion(verification))
        self.assertEqual(self.project.state()["current_gate"], "completed")
        self.assertEqual(self.project.ref("evidence/failed.json"), failure_ref)
        self.assertEqual((self.root / "docs/tests.md").read_text(encoding="utf-8"), PLAN)
        self.assertFalse((self.root / "docs/runs").exists())
        self.assertFalse((self.root / ".vulcan/worktrees").exists())
        self.assertEqual(self.project.git("branch", "--show-current").stdout.strip(), "dev-test")

    def test_completed_denies_execution_then_fresh_scope_preserves_history(self):
        self.pass_and_accept()
        completed = deepcopy(self.project.state()["current_work"])
        for field in ("verification", "verification_key", "basis"):
            self.assertIn(field, completed)
        before = self.session_bytes()
        sentinel = [sys.executable, "-c", "from pathlib import Path; Path('executed').touch()"]
        result = self.project.cli("execute", "--verify", "--source", "app.py", "--evidence", "evidence/forbidden.json", "--", *sentinel)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse((self.root / "executed").exists())
        self.assertFalse((self.root / "evidence/forbidden.json").exists())
        self.assertEqual(self.session_bytes(), before)
        self.submit(self.project.request("advance", target="impl"), 2)
        scope = deepcopy(completed["scope"])
        scope["work"]["revision"] = "snapshot:2"
        self.project.apply(self.project.request("open-work", scope=scope, target="planning",
                                              reason={"ref": "fixture:expansion", "revision": "snapshot:2"}))
        self.assertEqual(self.project.state()["work_history"][-1]["work"], completed)
        self.assertEqual(self.project.state()["current_work"]["decisions"], [])
        for field in ("verification", "verification_key", "basis"):
            self.assertNotIn(field, self.project.state()["current_work"])
        self.assertEqual(self.project.cli("release-pr", "--dry-run").returncode, 1)

    def test_verify_only_actor_cannot_return_to_implementation_without_fix_permission(self):
        # Produce a valid verification-only fixture through persisted requests.
        self.project.apply(self.project.request("advance", target="planning",
                                              reason={"ref": "fixture:restrict-authority", "revision": "snapshot:2"}))
        self.project.apply(self.project.request("advance", target="impl", decision=self.project.decision(["implement", "verify"])))
        self.project.apply(self.project.request("advance", target="acceptance", basis=self.project.basis()))
        self.assertEqual(self.project.verify("verify-only-failure").returncode, 1)
        request = self.project.request("advance", target="impl", reason={"ref": "fixture:failure", "revision": "snapshot:1"})
        self.assertIn("missing scoped fix", str(self.submit(request, 2)))
        request["decision"] = self.project.decision(["fix"])
        self.project.apply(request)
        self.assertEqual(self.project.state()["current_gate"], "impl")

    def test_clean_committed_mutations_do_not_restore_release_readiness(self):
        self.pass_and_accept()
        accepted = self.session_bytes()
        mutations = {
            "app.py": FIXED_APP + "\n# A source change still requires a current observation.\n",
            "environment.json": '{"python": "different"}',
            "docs/contracts.md": "# A changed requirement\n",
            "tests/test_requests.py": "raise AssertionError('changed test definition')\n",
            "requirements.txt": "# dependency specification changed\n",
            "evidence/passing.json": "{}\n",
        }
        for path, replacement in mutations.items():
            with self.subTest(path=path):
                original = (self.root / path).read_text(encoding="utf-8")
                self.project.write(path, replacement)
                self.project.commit("fixture: mutate " + path)
                self.assertEqual(self.project.git("status", "--porcelain").stdout, "")
                preview = self.project.cli("release-pr", "--dry-run")
                self.assertEqual(preview.returncode, 1, preview.stdout + preview.stderr)
                self.assertIn("current scoped documents or execution evidence", preview.stdout)
                self.assertEqual(self.session_bytes(), accepted)
                self.project.write(path, original)
                self.project.commit("fixture: restore " + path)
                restored = self.project.cli("release-pr", "--dry-run")
                self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)

    def test_post_test_source_commit_changes_observation_but_not_test_truth(self):
        self.project.apply(self.project.request("advance", target="impl",
                                              reason={"ref": "fixture:fix", "revision": "snapshot:1"}))
        self.project.write("app.py", FIXED_APP)
        self.project.apply(self.project.request("advance", target="acceptance", basis=self.project.basis()))
        self.assertEqual(self.project.verify("uncommitted").returncode, 0)
        verification = self.project.results("uncommitted")
        report_before = (self.root / "evidence/uncommitted.json").read_bytes()
        self.project.commit("fixture: commit source after testing")
        blocked = self.submit(self.project.completion(verification), 1)
        self.assertIn("stale", str(blocked))
        self.assertEqual((self.root / "evidence/uncommitted.json").read_bytes(), report_before)
        self.assertEqual(json.loads(report_before)["command"]["exit_code"], 0)
        self.assertEqual(self.project.verify("committed").returncode, 0)
        self.project.apply(self.project.completion(self.project.results("committed")))

    def test_failed_branch_switch_preserves_dirty_content_and_session(self):
        before = self.session_bytes()
        self.project.git("branch", "occupied")
        self.project.write("app.py", FIXED_APP)
        source = (self.root / "app.py").read_bytes()
        result = self.project.git("switch", "-c", "occupied", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.session_bytes(), before)
        self.assertEqual((self.root / "app.py").read_bytes(), source)
        self.assertEqual(self.project.git("branch", "--show-current").stdout.strip(), "dev-test")
        result = self.project.cli("branch-start", "impl")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.session_bytes(), before)
        self.assertEqual((self.root / "app.py").read_bytes(), source)

    def test_missing_executable_is_environment_failure_with_preserved_state(self):
        before = self.session_bytes()
        args = self.project.verification_args("environment-blocked")
        args = args[:args.index("--") + 1] + [str(self.root / "missing-runtime")]
        result = self.project.cli(*args)
        self.assertEqual(result.returncode, 127, result.stdout + result.stderr)
        report = json.loads((self.root / "evidence/environment-blocked.json").read_bytes())
        self.assertEqual(report["command"]["launch_error"], "FileNotFoundError")
        self.assertFalse(report["source_changed"])
        self.assertEqual(self.session_bytes(), before)
        forged = self.project.results("environment-blocked")
        self.assertIn("unsuccessful", str(self.submit(self.project.completion(forged), 1)))

    def test_branch_switch_to_old_session_rejects_pending_request(self):
        request = self.project.request("advance", target="impl", reason={"ref": "fixture:fix", "revision": "snapshot:1"})
        self.project.git("switch", "main")
        self.assertEqual(self.project.state()["current_gate"], "impl")
        result = self.submit(request, 2)
        self.assertEqual(result["status"], "conflict")
        self.project.git("switch", "dev-test")
        self.assertEqual(self.project.state()["current_gate"], "acceptance")

    def test_publication_remains_disabled_even_after_candidate_with_approval(self):
        self.pass_and_accept()
        session = self.project.state()
        preview = product_consumers.release_preview(self.root, session,
            {"main_branch": "main", "integration_branch": "dev-test"}, vulcan.parse_markdown_tables)
        self.assertEqual(preview["status"], "candidate", preview)
        self.assertFalse(preview["release_authorized"])
        self.assertFalse(preview["publication_enabled"])
        before = self.session_bytes()
        with mock.patch.object(vulcan, "gh_open_release_pr") as publisher, \
                mock.patch.object(vulcan, "git_push_if_remote") as push, \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as raised:
            vulcan.cmd_release_pr(project_dir=str(self.root))
        self.assertEqual(raised.exception.code, 2)
        publisher.assert_not_called()
        push.assert_not_called()
        self.assertEqual(self.session_bytes(), before)
        self.assertFalse((self.root / ".vulcan/release").exists())

    def test_inherited_git_environment_cannot_redirect_fixture_commands(self):
        temp = tempfile.TemporaryDirectory(prefix="product-isolated-")
        self.addCleanup(temp.cleanup)
        foreign_before = {path.relative_to(self.root).as_posix(): path.read_bytes()
                          for path in self.root.rglob("*") if path.is_file()}
        isolated = ExecutionProject(temp.name)
        injected = {"GIT_DIR": str(self.root / ".git"), "GIT_WORK_TREE": str(self.root),
                    "GIT_INDEX_FILE": str(self.root / ".git/index"), "GIT_CONFIG_COUNT": "1",
                    "GIT_CONFIG_KEY_0": "user.name", "GIT_CONFIG_VALUE_0": "Unwanted override"}
        with mock.patch.dict(os.environ, injected):
            isolated.create()
            self.assertEqual(isolated.git("rev-parse", "--show-toplevel").stdout.strip().replace("\\", "/"),
                             isolated.root.as_posix())
            self.assertEqual(isolated.cli("branch-status").returncode, 0)
            self.assertEqual(isolated.verify("isolated-failure").returncode, 1)
        foreign_after = {path.relative_to(self.root).as_posix(): path.read_bytes()
                         for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(foreign_after, foreign_before)
        # A worktree pointer is not the fixture's private repository either.
        pointer = isolated.root / "pointer"
        pointer.mkdir()
        (pointer / ".git").write_text("gitdir: " + str(self.root / ".git"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "own Git directory"):
            ExecutionProject(pointer).git("add", "-A")


if __name__ == "__main__":
    unittest.main()
