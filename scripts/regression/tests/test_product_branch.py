"""Real Git branch preparation without implicit state writes or publication."""

from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest import mock

from vulcan_core import product_branch as branch, product_process as process
import test_product_process as helpers
import test_product_session as sessions


class ProductBranchTests(unittest.TestCase):
    def setUp(self):
        self.fixture = sessions.ProductSessionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.workflow = {"integration_branch": "dev-happy", "main_branch": "main"}
        self.fixture.fixture.write("vulcan.config.json", json.dumps({"workflow": self.workflow}))
        self.fixture.fixture.write(".gitignore", "node_modules/\n")
        self.fixture.start()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Regression")
        self.git("config", "user.email", "regression@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("add", "-A")
        self.git("commit", "-m", "fixture planning")
        self.fixture.apply(self.fixture.request("advance", target="impl", decision=helpers.decision(self.fixture.read())))

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, encoding="utf-8", check=True).stdout.strip()

    def files(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*")
                if p.is_file() and ".git" not in p.relative_to(self.root).parts}

    def start(self, *, apply=False, workflow=None):
        resolver = (lambda _: workflow) if workflow is not None else helpers.vulcan.workflow_policy
        return branch.start(self.root, resolver, self.fixture.parse, apply=apply)

    def test_default_cli_preview_preserves_git_files_and_session(self):
        before = self.files()
        refs = self.git("show-ref")
        result = self.fixture.cli(["branch-start", "impl", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        preview = json.loads(result.stdout)
        self.assertEqual(preview["status"], "ready")
        self.assertEqual(preview["operation"], "create")
        self.assertFalse(preview["applied"])
        self.assertEqual(preview["current_branch"], "main")
        self.assertEqual(self.git("show-ref"), refs)
        self.assertEqual(self.files(), before)
        self.assertFalse((self.root / ".vulcan/product-process.lock").exists())

    def test_apply_keeps_pending_session_cache_index_and_commit_history(self):
        self.fixture.fixture.write("node_modules/local-cache", "installed")
        before = self.files()
        head = self.git("rev-parse", "HEAD")
        index = self.git("ls-files", "--stage")
        result = self.fixture.cli(["branch-start", "impl", "--apply", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        applied = json.loads(result.stdout)
        self.assertEqual(applied["status"], "applied")
        self.assertTrue(applied["applied"])
        self.assertFalse(applied["session_changed"])
        self.assertFalse(applied["release_authorized"])
        self.assertEqual(self.git("branch", "--show-current"), "dev-happy")
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("ls-files", "--stage"), index)
        self.assertEqual(self.files(), before)
        self.assertNotIn("branch_state", self.fixture.read())

    def test_staged_and_untracked_session_are_preserved(self):
        for mode in ("staged", "untracked"):
            with self.subTest(mode=mode):
                if mode == "staged":
                    self.git("add", "session.json")
                else:
                    self.git("switch", "main")
                    self.git("rm", "--cached", "session.json")
                    self.git("commit", "-m", "fixture untracked session")
                before = self.files()
                result = self.start(apply=True, workflow={**self.workflow, "integration_branch": "dev-" + mode})
                self.assertEqual(result["status"], "applied", result)
                self.assertEqual(self.files(), before)

    def test_same_tree_existing_branch_switch_preserves_current_session(self):
        self.git("branch", "dev-happy")
        before = self.files()
        preview = self.start()
        self.assertEqual(preview["operation"], "switch")
        result = self.start(apply=True)
        self.assertEqual(result["status"], "applied", result)
        self.assertEqual(self.files(), before)

    def test_different_existing_tree_is_not_checked_out_or_rewritten(self):
        # A target from another iteration must not replace current contracts/state.
        self.git("add", "session.json")
        self.git("commit", "-m", "fixture impl")
        self.git("switch", "-c", "dev-happy")
        self.fixture.fixture.write("app.py", "value = 2\n")
        self.git("add", "app.py")
        self.git("commit", "-m", "fixture different implementation")
        self.git("switch", "main")
        before = self.files()
        refs = self.git("show-ref")
        result = self.start(apply=True)
        self.assertEqual(result["status"], "blocked", result)
        self.assertIn("different content", result["message"])
        self.assertEqual(self.git("branch", "--show-current"), "main")
        self.assertEqual(self.git("show-ref"), refs)
        self.assertEqual(self.files(), before)

    def test_already_integration_is_noop_even_with_unfinished_code(self):
        self.git("switch", "-c", "dev-happy")
        self.fixture.fixture.write("app.py", "value = 2\n")
        before = self.files()
        result = self.start(apply=True)
        self.assertEqual(result["status"], "unchanged", result)
        self.assertFalse(result["applied"])
        self.assertEqual(self.files(), before)

    def test_code_or_untracked_changes_block_without_stashing(self):
        for path in ("app.py", "docs/한글 기록.md"):
            with self.subTest(path=path):
                self.fixture.fixture.write(path, "pending work\n")
                before = self.files()
                result = self.start(apply=True)
                self.assertEqual(result["status"], "blocked", result)
                self.assertIn("pending changes", result["message"])
                self.assertEqual(self.files(), before)
                self.assertEqual(self.git("branch", "--show-current"), "main")
                self.assertEqual(self.git("stash", "list"), "")

    def test_planning_acceptance_and_completed_do_not_start_branches(self):
        impl = self.fixture.read()
        acceptance = process.advance(impl, "acceptance", readiness=helpers.ready(impl, "handoff"),
                                     current_basis=self.fixture.fixture.basis())
        verification = helpers.verification(acceptance, self.fixture.fixture.basis())
        key = process.verification_key(acceptance["current_work"]["scope"], verification, self.fixture.fixture.basis())
        completed = process.advance(acceptance, "completed", verification=verification,
                                    current_basis=self.fixture.fixture.basis(),
                                    decision=helpers.decision(acceptance, ["accept"], verification_key=key))
        for session in (process.new_session(impl["current_work"]["scope"]), acceptance, completed):
            with self.subTest(stage=session["current_gate"]):
                self.fixture.path.write_text(json.dumps(session), encoding="utf-8")
                before = self.files()
                result = self.start()
                self.assertEqual(result["status"], "blocked", result)
                self.assertEqual(self.files(), before)

    def test_missing_authority_and_changed_contract_do_not_mutate(self):
        original = self.fixture.read()
        session = deepcopy(original)
        session["current_work"]["decisions"] = []
        self.fixture.path.write_text(json.dumps(session), encoding="utf-8")
        before = self.files()
        self.assertEqual(self.start(apply=True)["status"], "invalid")
        self.assertEqual(self.files(), before)
        self.fixture.path.write_text(json.dumps(original), encoding="utf-8")
        self.fixture.fixture.write("docs/contracts.md", "# Changed contract\n")
        result = self.start()
        self.assertEqual(result["status"], "blocked", result)
        self.assertIn("revision changed", str(result["checks"]))

    def test_single_policy_invalid_names_and_worker_branch_reject(self):
        for policy in ({"branch_mode": "single"}, {"impl_uses_integration_branch": False},
                       {"integration_branch": "main"}, {"integration_branch": "main~0"},
                       {"integration_branch": "--help"}):
            with self.subTest(policy=policy):
                self.assertIn(self.start(workflow={**self.workflow, **policy})["status"], {"blocked", "invalid"})
        self.git("switch", "-c", "worker/in-progress")
        result = self.start(apply=True)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("worker branch", result["message"])
        self.assertEqual(self.git("branch", "--show-current"), "worker/in-progress")

    def test_detached_head_and_nested_project_do_not_change_parent_repository(self):
        self.git("switch", "--detach")
        self.assertEqual(self.start()["status"], "blocked")
        self.git("switch", "main")
        child = self.root / "nested"
        child.mkdir()
        (child / "session.json").write_bytes(self.fixture.path.read_bytes())
        result = branch.start(child, helpers.vulcan.workflow_policy, self.fixture.parse)
        self.assertEqual(result["status"], "blocked", result)
        self.assertIn("rooted at the project", result["message"])
        self.assertEqual(self.git("branch", "--show-current"), "main")

    def test_existing_writer_lock_is_not_removed(self):
        lock = self.root / ".vulcan/product-process.lock"
        lock.write_text("another writer", encoding="ascii")
        result = self.start(apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertEqual(lock.read_text(), "another writer")
        self.assertEqual(self.git("branch", "--show-current"), "main")

    def test_concurrent_session_change_prevents_checkout_without_reverting_editor(self):
        inspect = branch._inspect
        calls = 0

        def changed(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                session = self.fixture.read()
                session["editor_note"] = "concurrent change"
                self.fixture.path.write_text(json.dumps(session), encoding="utf-8")
            return inspect(*args, **kwargs)

        with mock.patch.object(branch, "_inspect", side_effect=changed):
            result = self.start(apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertEqual(self.fixture.read()["editor_note"], "concurrent change")
        self.assertEqual(self.git("branch", "--show-current"), "main")

    def test_git_failure_does_not_reset_or_claim_unchanged_state(self):
        git = branch._git

        def fail(root, *args, **kwargs):
            if "switch" in args:
                raise subprocess.TimeoutExpired("git switch", 30)
            return git(root, *args, **kwargs)

        before = self.files()
        with mock.patch.object(branch, "_git", side_effect=fail):
            result = self.start(apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertIsNone(result["applied"])
        self.assertIn("no automatic rollback", result["message"])
        self.assertEqual(self.files(), before)

    def different_commit(self):
        self.git("branch", "dev-happy")
        self.git("switch", "-c", "other-content")
        self.fixture.fixture.write("app.py", "value = 2\n")
        self.git("add", "app.py")
        self.git("commit", "-m", "fixture other content")
        commit = self.git("rev-parse", "HEAD")
        self.git("switch", "main")
        return commit

    def test_target_moved_before_ref_lock_cannot_checkout_different_content(self):
        other = self.different_commit()
        hold = branch._hold_target

        @contextlib.contextmanager
        def moved(*args):
            self.git("update-ref", "refs/heads/dev-happy", other)
            with hold(*args):
                yield

        before = self.files()
        with mock.patch.object(branch, "_hold_target", side_effect=moved):
            result = self.start(apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertEqual(self.git("branch", "--show-current"), "main")
        self.assertEqual(self.files(), before)

    def test_target_ref_cannot_move_during_checkout(self):
        other = self.different_commit()
        git = branch._git
        attempted = []

        def move(root, *args, **kwargs):
            if "switch" in args:
                attempted.append(subprocess.run(["git", "update-ref", "refs/heads/dev-happy", other],
                                 cwd=root, capture_output=True, timeout=10).returncode)
            return git(root, *args, **kwargs)

        before = self.files()
        with mock.patch.object(branch, "_git", side_effect=move):
            result = self.start(apply=True)
        self.assertEqual(result["status"], "applied", result)
        self.assertEqual(len(attempted), 1)
        self.assertNotEqual(attempted[0], 0)
        self.assertEqual(self.files(), before)
        self.assertNotEqual(self.git("rev-parse", "HEAD"), other)

    def test_post_switch_ref_change_is_reported_without_rollback(self):
        other = self.different_commit()
        hold = branch._hold_target

        @contextlib.contextmanager
        def moved(*args):
            with hold(*args):
                yield
            self.git("update-ref", "refs/heads/dev-happy", other)

        before = self.files()
        with mock.patch.object(branch, "_hold_target", side_effect=moved):
            result = self.start(apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertIsNone(result["applied"])
        self.assertEqual(self.git("branch", "--show-current"), "dev-happy")
        self.assertEqual(self.files(), before)

    def test_new_branch_is_pinned_to_inspected_commit(self):
        other = self.different_commit()
        expected = self.git("rev-parse", "HEAD")
        git = branch._git

        def moved(root, *args, **kwargs):
            if "switch" in args:
                self.git("update-ref", "refs/heads/main", other)
            return git(root, *args, **kwargs)

        with mock.patch.object(branch, "_git", side_effect=moved):
            result = self.start(apply=True, workflow={**self.workflow, "integration_branch": "new-dev"})
        self.assertEqual(result["status"], "applied", result)
        self.assertEqual(self.git("rev-parse", "HEAD"), expected)
        self.assertEqual(self.git("rev-parse", "main"), other)

    def test_cli_resolves_policy_under_lock_not_before_it(self):
        lock = branch.store._lock

        @contextlib.contextmanager
        def changed(root):
            self.fixture.fixture.write("vulcan.config.json", json.dumps({"workflow": {"branch_mode": "single"}}))
            self.git("add", "vulcan.config.json")
            self.git("commit", "-m", "fixture changed policy")
            with lock(root) as warnings:
                yield warnings

        output = io.StringIO()
        with mock.patch.object(branch.store, "_lock", side_effect=changed), contextlib.redirect_stdout(output):
            code = helpers.vulcan.cmd_branch_start(project_dir=self.root, apply=True, emit_json=True)
        self.assertEqual(code, 1, output.getvalue())
        self.assertIn("no integration branch", json.loads(output.getvalue())["message"])
        self.assertEqual(self.git("branch", "--show-current"), "main")

    def test_malformed_policy_does_not_fall_back_to_default_branch_creation(self):
        for text in ('{', '{"workflow": null}', '{"workflow":{"impl_uses_integration_branch":"false"}}'):
            with self.subTest(config=text):
                self.fixture.fixture.write("vulcan.config.json", text)
                before = self.files()
                result = self.start(apply=True)
                self.assertEqual(result["status"], "invalid", result)
                self.assertEqual(self.files(), before)
                self.assertEqual(self.git("branch", "--show-current"), "main")

    def final_inspection_change(self, change):
        inspect = branch._inspect
        calls = 0

        def changed(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                change()
            return inspect(*args, **kwargs)

        with mock.patch.object(branch, "_inspect", side_effect=changed):
            result = self.start(apply=True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertIsNone(result["applied"])

    def test_final_inspection_session_change_is_not_reported_as_success(self):
        def change():
            session = self.fixture.read()
            session["editor_note"] = "late change"
            self.fixture.path.write_text(json.dumps(session), encoding="utf-8")

        self.final_inspection_change(change)
        self.assertEqual(self.fixture.read()["editor_note"], "late change")
        self.assertEqual(self.git("branch", "--show-current"), "dev-happy")

    def test_final_inspection_ref_change_is_not_reported_as_success(self):
        other = self.different_commit()
        before = self.files()
        self.final_inspection_change(lambda: self.git("update-ref", "refs/heads/dev-happy", other))
        self.assertEqual(self.git("rev-parse", "HEAD"), other)
        self.assertEqual(self.files(), before)

    def test_final_inspection_checkout_is_not_reported_as_success(self):
        before = self.files()
        self.final_inspection_change(lambda: self.git("switch", "main"))
        self.assertEqual(self.git("branch", "--show-current"), "main")
        self.assertEqual(self.files(), before)

    def test_checkout_hooks_are_not_executed_or_reconfigured(self):
        hook = self.root / ".git/hooks/post-checkout"
        hook.write_text("#!/bin/sh\nprintf unsafe > hook-ran\n", encoding="ascii")
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", str(hook.parent))
        result = self.start(apply=True)
        self.assertEqual(result["status"], "applied", result)
        self.assertFalse((self.root / "hook-ran").exists())
        self.assertEqual(self.git("config", "core.hooksPath"), str(hook.parent))

    def test_legacy_dispatch_remains_explicit_and_pilot_flags_cannot_write(self):
        self.fixture.path.write_text(json.dumps({"profile": "product", "current_gate": "impl"}), encoding="utf-8")
        before = self.files()
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(helpers.vulcan, "has_blocking_dirty_status", return_value=False), \
                mock.patch.object(helpers.vulcan, "git_current_branch", return_value="dev-happy"), \
                mock.patch.object(helpers.vulcan, "refresh_session_stats") as refresh, \
                mock.patch.object(helpers.vulcan, "save_session") as save, \
                mock.patch.object(helpers.vulcan, "git_commit", return_value=False) as commit, \
                mock.patch.object(helpers.vulcan, "git_push_if_remote") as push:
            helpers.vulcan.cmd_branch_start(project_dir=self.root)
            save.assert_called_once()
            refresh.assert_called_once()
            commit.assert_called_once()
            push.assert_not_called()
            self.assertEqual(helpers.vulcan.cmd_branch_start(project_dir=self.root, dry_run=True), 2)
            self.assertEqual(save.call_count, 1)
        self.assertEqual(self.files(), before)


if __name__ == "__main__":
    unittest.main()
