"""New init activation, real CLI first scope, and non-migrating upgrades."""

import contextlib
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from vulcan_core import product_process as process, product_session as store
from test_product_process import ROOT, decision, ref, vulcan
import test_product_readiness as fixtures


class ProductActivationTests(unittest.TestCase):
    def root(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        # Internal path helpers receive canonical roots, as public CLI paths do.
        return (Path(temp.name) / "project").resolve()

    def init(self, root, profile="product", primary="codex-cli"):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), mock.patch.object(
                vulcan.subprocess, "run", side_effect=OSError("Git disabled in fixture")):
            vulcan.init(str(root), "Request Board", "Tester", profile=profile, primary=primary)
        return output.getvalue()

    def read(self, root):
        return json.loads((root / "session.json").read_bytes())

    def cli(self, root, args, request=None):
        return subprocess.run([sys.executable, str(root / "vulcan.py"), *args], cwd=root,
            input=json.dumps(request) if request is not None else None, text=True,
            encoding="utf-8", capture_output=True, timeout=60)

    def test_new_product_all_primaries_start_unapproved_planning(self):
        for primary in ("codex-cli", "antigravity-cli", "claude-cli"):
            with self.subTest(primary=primary):
                root = self.root()
                output = self.init(root, primary=primary)
                session = self.read(root)
                work = process._validate(session)
                self.assertEqual(session["current_gate"], "planning")
                self.assertEqual(set(session["gate_status"]), set(process.STAGES))
                self.assertEqual(work["decisions"], [])
                self.assertEqual(session["work_history"], [])
                self.assertEqual(work["scope"]["work"]["ref"], "docs/product/PRODUCT_BRIEF.md")
                for field in ("related_ids", "contracts", "tests", "required_checks"):
                    self.assertEqual(work["scope"][field], [])
                config = json.loads((root / "vulcan.config.json").read_bytes())
                self.assertEqual(config["runtime"]["primary"], primary)
                self.assertNotIn("Phase 0부터 시작", output)
                self.assertIn("incomplete_scope", output)
                before = (root / "session.json").read_bytes()
                status = self.cli(root, ["status", "--check", "--json"])
                self.assertEqual(status.returncode, 1, status.stdout + status.stderr)
                self.assertIn("incomplete_scope", status.stdout)
                self.assertEqual((root / "session.json").read_bytes(), before)
                self.assertFalse(any((root / "docs/runs").glob("RUN-*.md")))

    def test_new_product_status_keeps_dashboard_comment_entrypoint(self):
        root = self.root()
        self.init(root)
        comments = root / ".vulcan/comments/comments.jsonl"
        comments.parent.mkdir(parents=True)
        comments.write_text(json.dumps({"comment_id": "C-1", "status": "open",
            "document": "docs/product/PRODUCT_BRIEF.md", "body": "Clarify actors"}) + "\n", encoding="utf-8")
        result = self.cli(root, ["status", "--json"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["dashboard_comments"]["open"], 1)

    def test_version_and_lock_contended_upgrade_are_safe_cli_paths(self):
        root = self.root()
        self.init(root)
        result = self.cli(root, ["version"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(vulcan.VULCAN_VERSION, result.stdout)
        result = self.cli(root, ["profile-status"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("process_model: product-iterative-v1", result.stdout)
        self.assertNotIn("overlay policy first", result.stdout)
        (root / "AGENTS.md").write_text("# Stale framework\n", encoding="utf-8")
        with store._lock(root):
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            result = self.cli(root, ["upgrade"])
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("upgrade conflict", result.stdout)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_audit_and_poc_init_keep_legacy_state(self):
        for profile in ("audit", "poc"):
            with self.subTest(profile=profile):
                root = self.root()
                output = self.init(root, profile=profile)
                session = self.read(root)
                self.assertNotIn("process_model", session)
                self.assertEqual(session["current_gate"], "phase0")
                self.assertEqual(len(session["gate_status"]), 7)
                self.assertIn("Phase 0부터 시작", output)

    def test_reinitialization_cannot_replace_existing_project(self):
        root = self.root()
        self.init(root)
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
        result = subprocess.run([sys.executable, str(ROOT / "vulcan.py"), "init", str(root),
            "Replacement", "--profile", "audit", "--primary", "codex-cli"],
            input="y\n", capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("upgrade", result.stdout)
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_first_agreed_scope_uses_existing_open_work_preview_and_authority(self):
        root = self.root()
        self.init(root)
        fixture = fixtures.ScopedReadinessTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for path in fixture.root.rglob("*"):
            if path.is_file():
                target = root / path.relative_to(fixture.root)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())
        path = root / "session.json"
        initial = self.read(root)

        def request(action, **extra):
            return {"process_model": process.MODEL, "action": action,
                    "expected_session_revision": store.revision(path.read_bytes()), **extra}

        def submit(value, apply=False):
            args = ["session", "--process-request", "-", "--json"]
            return self.cli(root, args + (["--apply"] if apply else []), value)

        # Even a claimed approval cannot promote init's empty scope.
        blocked = submit(request("advance", target="impl", decision=decision(initial)), True)
        self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
        self.assertIn("incomplete_scope", blocked.stdout)
        scope_request = request("open-work", target="planning", scope=fixture.scope,
                                reason=ref("discussion:first-scope"))
        before = path.read_bytes()
        preview = submit(scope_request)
        self.assertEqual(preview.returncode, 0, preview.stdout + preview.stderr)
        self.assertEqual(path.read_bytes(), before)
        applied = submit(scope_request, True)
        self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
        planning = self.read(root)
        self.assertEqual(planning["work_history"][0]["work"], initial["current_work"])
        self.assertEqual(planning["current_work"]["decisions"], [])
        no_approval = submit(request("advance", target="impl"), True)
        self.assertEqual(no_approval.returncode, 1, no_approval.stdout + no_approval.stderr)
        approved = submit(request("advance", target="impl", decision=decision(planning)), True)
        self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
        self.assertEqual(self.read(root)["current_gate"], "impl")
        legacy = self.cli(root, ["gate-start", "gate4"])
        self.assertEqual(legacy.returncode, 2)
        self.assertFalse(json.loads(approved.stdout)["release_authorized"])

    def test_upgrade_preserves_authored_docs_and_each_process(self):
        for kind in ("new_product", "legacy_product", "audit", "poc"):
            with self.subTest(kind=kind):
                root = self.root()
                self.init(root, profile="product" if "product" in kind else kind)
                path = root / "session.json"
                session = self.read(root)
                if kind == "legacy_product":
                    for key in ("process_model", "current_work", "work_history"):
                        session.pop(key)
                    session.update(current_gate="gate4", gate_status={"gate4": "in-progress"})
                session["vulcan_version"] = "old-fixture"
                path.write_text(json.dumps(session), encoding="utf-8")
                authored = root / ("docs/product/PRODUCT_BRIEF.md" if "product" in kind else "docs/user-owned.md")
                authored.write_text("# Authored scope\nDo not rewrite my requirements.\n", encoding="utf-8")
                before_doc = authored.read_bytes()
                result = self.cli(root, ["upgrade"])
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                after = self.read(root)
                self.assertEqual(after["vulcan_version"], vulcan.VULCAN_VERSION)
                for field in ("vulcan_version", "vulcan_src"):
                    after.pop(field, None)
                    session.pop(field, None)
                self.assertEqual(after, session)
                self.assertEqual(authored.read_bytes(), before_doc)

    def test_upgrade_metadata_respects_lock_and_keeps_current_work(self):
        root = self.root()
        self.init(root)
        path = root / "session.json"
        before = path.read_bytes()
        with store._lock(root):
            with self.assertRaises(store.ConflictError):
                store.refresh_framework_metadata(root, source="source", version="new")
        self.assertEqual(path.read_bytes(), before)
        original = self.read(root)
        changed = deepcopy(original)
        changed["project"] = "Concurrent owner edit"
        path.write_text(json.dumps(changed), encoding="utf-8")
        store.refresh_framework_metadata(root, source="source", version="new")
        result = self.read(root)
        self.assertEqual(result["project"], changed["project"])
        for field in ("current_gate", "gate_status", "current_work", "work_history"):
            self.assertEqual(result[field], original[field])


if __name__ == "__main__":
    unittest.main()
