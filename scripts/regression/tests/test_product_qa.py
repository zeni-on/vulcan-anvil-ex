"""Run-free QA handoff and return use existing authority/evidence contracts."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from vulcan_core import product_qa as qa, product_process as process, product_session as store
import test_product_process as helpers
import test_product_session as sessions


class ProductQATests(unittest.TestCase):
    def setUp(self):
        self.fixture = sessions.ProductSessionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.fixture.acceptance()
        self.workflow = {"integration_branch": "dev"}

    def preview(self, **kwargs):
        return qa.handoff(self.root, self.workflow, self.fixture.parse, **kwargs)

    def files(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_preview_contains_only_current_scope_and_empty_return_not_approval(self):
        before = self.files()
        for runner in sorted(qa.NATIVE_RUNNERS):
            result = self.preview(runner=runner)
            self.assertEqual(result["status"], "candidate", result)
            self.assertEqual(result["scope"], self.fixture.read()["current_work"]["scope"])
            self.assertEqual(result["authority"], "verify_only")
            self.assertEqual(result["runner_mode"], runner)
            self.assertFalse(result["dispatched"])
            self.assertFalse(result["release_authorized"])
            self.assertEqual(result["return_request"]["verification"]["results"], [])
            self.assertNotIn("decision", result["return_request"])
            self.assertEqual(result["session_revision"], store.revision(self.fixture.path.read_bytes()))
        self.assertEqual(self.files(), before)
        self.assertFalse((self.root / "docs/runs").exists())
        self.assertFalse((self.root / ".vulcan/worktrees").exists())

    def test_cli_routes_run_free_native_preview_but_never_launches_commands(self):
        before = self.files()
        for options in (["--json"], [], ["--runner", "thread", "--json"]):
            result = self.fixture.cli(["execute", "--dry-run", *options])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("candidate", result.stdout)
        for options in ([], ["--json"], ["--dry-run", "--run-id", "RUN-001"],
                        ["--dry-run", "--runner", "codex-cli"], ["--dry-run", "--runner", "typo"],
                        ["--dry-run", "--", sys.executable, "-c", "raise RuntimeError('not executable')"]):
            result = self.fixture.cli(["execute", *options])
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.files(), before)

    def test_wrong_stage_unknown_model_or_missing_permission_never_dispatch(self):
        current = self.fixture.read()
        planning = process.new_session(current["current_work"]["scope"])
        impl = deepcopy(current)
        impl["current_gate"] = "impl"
        impl["gate_status"] = {"planning": "done", "impl": "in-progress", "acceptance": "pending"}
        missing = deepcopy(current)
        missing["current_work"]["decisions"] = []
        for state in (planning, impl, missing, {**current, "process_model": "future"}, {**current, "profile": "audit"}):
            self.fixture.path.write_text(json.dumps(state), encoding="utf-8")
            before = self.files()
            self.assertEqual(self.preview()["status"], "blocked")
            self.assertEqual(self.files(), before)

    def test_contract_plan_and_environment_changes_block_preview_and_execution(self):
        for path in ("docs/contracts.md", "docs/tests.md", "environment.json"):
            with self.subTest(path=path):
                file = self.root / path
                original = file.read_bytes()
                file.write_bytes(original + b"\nchanged\n")
                before = self.files()
                result = self.preview()
                self.assertEqual(result["status"], "blocked", result)
                (self.root / "evidence").mkdir(exist_ok=True)
                executed = self.fixture.cli(["execute", "--verify", "--evidence", "evidence/forbidden.json", "--",
                    sys.executable, "-c", "from pathlib import Path; Path('executed').touch()"])
                self.assertEqual(executed.returncode, 2, executed.stdout + executed.stderr)
                self.assertFalse((self.root / "executed").exists())
                self.assertFalse((self.root / "evidence/forbidden.json").exists())
                self.assertEqual(self.files(), before)
                file.write_bytes(original)

    def test_session_changes_during_preview_return_conflict_without_overwriting(self):
        load = store._load
        calls = []

        def changed(root):
            calls.append(root)
            if len(calls) == 2:
                self.fixture.path.write_bytes(self.fixture.path.read_bytes() + b"\n")
            return load(root)

        with mock.patch.object(store, "_load", side_effect=changed):
            self.assertEqual(self.preview()["status"], "conflict")
        self.assertTrue(self.fixture.path.read_bytes().endswith(b"\n\n"))

    def test_empty_failed_blocked_missing_and_duplicate_returns_cannot_be_accepted(self):
        request = self.preview()["return_request"]
        observed = self.fixture.observed_results()
        cases = [[]]
        for status in ("Fail", "Not Run", "environment_blocked", "Skipped"):
            rows = deepcopy(observed["results"])
            rows[0]["status"] = status
            cases.append(rows)
        cases.extend([observed["results"][:-1], observed["results"] + [observed["results"][0]]])
        before = self.files()
        for rows in cases:
            request["verification"]["results"] = rows
            result = store.transact(self.root, request, self.fixture.parse, apply=True)
            self.assertEqual(result["status"], "blocked", result)
            self.assertEqual(self.files(), before)

    def test_success_returns_verification_key_but_needs_separate_accept_decision(self):
        request = self.preview()["return_request"]
        request["verification"] = self.fixture.observed_results()
        before = self.files()
        result = store.transact(self.root, request, self.fixture.parse)
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(result["checks"]["execution"], "verified_observations")
        self.assertEqual(self.files(), before)
        request["decision"] = helpers.decision(self.fixture.read(), ["accept"],
            verification_key=result["checks"]["verification_key"])
        applied = store.transact(self.root, request, self.fixture.parse, apply=True)
        self.assertEqual(applied["status"], "applied", applied)
        self.assertFalse(applied["release_authorized"])
        self.assertEqual(self.preview()["status"], "blocked")

    def test_old_return_cannot_overwrite_new_session_revision(self):
        request = self.preview()["return_request"]
        request["verification"] = self.fixture.observed_results()
        self.fixture.path.write_bytes(self.fixture.path.read_bytes() + b"\n")
        before = self.files()
        result = store.transact(self.root, request, self.fixture.parse, apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertEqual(self.files(), before)

    def test_legacy_run_plan_dispatch_is_preserved(self):
        self.fixture.path.write_text(json.dumps({"profile": "product", "current_gate": "gate4"}), encoding="utf-8")
        with mock.patch.object(helpers.vulcan, "_execute_plan", side_effect=RuntimeError("legacy planner")) as plan:
            with self.assertRaisesRegex(RuntimeError, "legacy planner"):
                helpers.vulcan.cmd_execute("RUN-010", dry_run=True, project_dir=self.root)
            plan.assert_called_once()
        before = self.files()
        result = self.fixture.cli(["execute", "--dry-run", "--json"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("requires --run-id", result.stderr)
        self.assertEqual(self.files(), before)


class ProductQAGitTests(unittest.TestCase):
    def test_real_git_handoff_failure_retest_return_without_run_or_state_mutation_by_worker(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from product_execution_fixture import ExecutionProject
        with tempfile.TemporaryDirectory(prefix="product-qa-git-") as folder:
            project = ExecutionProject(folder)
            project.create()
            raw = (project.root / "session.json").read_bytes()
            preview = project.cli("execute", "--dry-run", "--json", "--runner", "subagent")
            self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
            plan = json.loads(preview.stdout)
            self.assertEqual(plan["workspace"]["current_branch"], "dev-test")
            self.assertEqual(project.verify("failed").returncode, 1)
            self.assertEqual((project.root / "session.json").read_bytes(), raw)
            request = plan["return_request"]
            request["verification"] = project.results("failed")  # Claimed Pass cannot mask real exit 1.
            blocked = project.cli("session", "--process-request", "-", "--json", request=request)
            self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
            self.assertIn("unsuccessful", blocked.stdout)
            project.fix()
            self.assertEqual(project.verify("retest").returncode, 0)
            stale = project.cli("session", "--process-request", "-", "--json", request=request)
            self.assertEqual(stale.returncode, 2, stale.stdout + stale.stderr)
            fresh = json.loads(project.cli("execute", "--dry-run", "--json").stdout)["return_request"]
            fresh["verification"] = project.results("retest")
            result = json.loads(project.cli("session", "--process-request", "-", "--json", request=fresh).stdout)
            self.assertEqual(result["checks"]["execution"], "verified_observations")
            fresh["decision"] = project.decision(["accept"], verification_key=result["checks"]["verification_key"])
            project.apply(fresh)
            self.assertFalse((project.root / "docs/runs").exists())
            self.assertFalse((project.root / ".vulcan/worktrees").exists())
            self.assertTrue((project.root / "evidence/failed.json").is_file())

    def test_wrong_git_workspace_blocks_handoff(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from product_execution_fixture import ExecutionProject
        with tempfile.TemporaryDirectory(prefix="product-qa-branch-") as folder:
            project = ExecutionProject(folder)
            project.create()
            project.git("switch", "-c", "worker/wrong")
            before = (project.root / "session.json").read_bytes()
            result = project.cli("execute", "--dry-run", "--json")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("agreed integration branch", result.stdout)
            self.assertEqual((project.root / "session.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
