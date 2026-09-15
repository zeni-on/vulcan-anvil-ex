"""Synthetic legacy migration: no product workspace or operational data used."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest import mock

from vulcan_core import product_migration as migration, product_process as process, product_session as store
import test_product_process as helpers
import test_product_readiness as fixtures


class ProductMigrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ScopedReadinessTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.path = self.root / "session.json"
        self.parse = helpers.vulcan.parse_markdown_tables
        self.fixture.write("docs/work.md", "# Current planning\nShared flow, then schedule, then dashboard.\n")
        self.fixture.write("docs/migration.md", "# Decision\nMigrate this synthetic session to planning only.\n")
        self.fixture.write("docs/old-run.md", "# Past work\nNot Run: deferred inspection.\n")
        self.scope = deepcopy(self.fixture.scope)
        self.scope["work"] = self.fixture.ref("docs/work.md")
        self.legacy = {"project": "Synthetic", "profile": "product", "current_gate": "gate1",
            "gate_status": {g: "done" for g in migration.GATES},
            "completed": ["old implementation"], "pending": ["old UI verification"],
            "blocked": ["environment unavailable"], "approvals": {"gate5": {"approved": True}},
            "implementation": {"waves": [{"id": "BW-100", "status": "done"}]},
            "open_issues": ["ISSUE-OLD"], "workflow": {"integration_branch": "dev-custom"},
            "branch_state": {"branch": "dev-custom"}, "vulcan_version": "0.5.0",
            "custom_setting": {"preserve": True}}
        self.legacy["gate_status"].update(gate1="awaiting-approval", gate4="pending")
        self.original = b"\xef\xbb\xbf" + json.dumps(self.legacy, indent=3).replace("\n", "\r\n").encode()
        self.path.write_bytes(self.original)

    def request(self, **extra):
        result = {"process_model": process.MODEL, "action": "migrate", "target": "planning",
            "expected_session_revision": None, "scope": deepcopy(self.scope),
            "reason": self.fixture.ref("docs/migration.md"), "obligation_review": "pending",
            "obligations": [{"source": self.fixture.ref("docs/old-run.md"),
                "description": "Inspection UI not run; deferred, not completed", "owner": "QA owner",
                "scope": "followup", "status": "open"}]}
        result.update(extra)
        return result

    def call(self, request, apply=False):
        return store.transact(self.root, request, self.parse, apply=apply)

    def prepare(self, request=None):
        result = self.call(request or self.request())
        self.assertEqual(result["status"], "ready", result)
        return result

    def migrate(self):
        preview = self.prepare()
        result = self.call(preview["prepared_request"], True)
        self.assertEqual(result["status"], "applied", result)
        return result

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def restore_request(self, result):
        return {"process_model": process.MODEL, "action": "restore-migration",
                "expected_session_revision": None, "backup": result["backup"]}

    def test_preview_is_read_only_and_exposes_scope_and_legacy_pending(self):
        before = self.snapshot()
        directories = {p for p in self.root.rglob("*") if p.is_dir()}
        with mock.patch.object(store, "_lock", side_effect=AssertionError("preview locked")), \
                mock.patch.object(subprocess, "run", side_effect=AssertionError("hidden command")):
            result = self.prepare()
        self.assertEqual(before, self.snapshot())
        self.assertEqual(directories, {p for p in self.root.rglob("*") if p.is_dir()})
        self.assertEqual(result["current_gate"], "gate1")
        self.assertEqual(result["proposed_gate"], "planning")
        self.assertEqual(result["backup_scope"], ["session.json"])
        self.assertEqual(result["migration"]["legacy_gate_status"]["gate4"], "pending")
        self.assertEqual(result["migration"]["obligation_review"], "pending")
        self.assertEqual(result["proposed_scope"], process.normalize_scope(self.scope))
        self.assertEqual(result["prepared_request"]["expected_session_revision"], store.revision(self.original))

    def test_apply_preserves_bytes_settings_obligations_and_grants_no_approval(self):
        result = self.migrate()
        current = json.loads(self.path.read_bytes())
        self.assertEqual(current["current_work"]["decisions"], [])
        self.assertEqual(current["work_history"], [])
        self.assertEqual(current["gate_status"], {"planning": "in-progress", "impl": "pending", "acceptance": "pending"})
        for key in ("workflow", "branch_state", "open_issues", "vulcan_version", "custom_setting"):
            self.assertEqual(current[key], self.legacy[key])
        for key in ("approvals", "completed", "pending", "blocked", "implementation"):
            self.assertNotIn(key, current)
        self.assertEqual(migration._read_backup(self.root, result["backup"])[1], self.original)
        self.assertFalse(result["implementation_authorized"])
        self.assertFalse(result["release_authorized"])
        blocked = self.call({"process_model": process.MODEL, "action": "advance", "target": "impl",
                            "expected_session_revision": store.revision(self.path.read_bytes())})
        self.assertEqual(blocked["status"], "blocked", blocked)
        self.assertIn("missing scoped implement", str(blocked))
        checked = helpers.vulcan.product_readiness.collect(self.root, current, self.parse)
        self.assertEqual(checked["unresolved_obligations"], 1)
        self.assertEqual(checked["migration_handover"]["obligations"][0]["scope"], "followup")
        rendered = helpers.vulcan.product_readiness.render(checked)
        self.assertIn("not a complete/resolved inventory", rendered)
        self.assertIn("QA owner", rendered)
        self.assertIn("followup/open", rendered)

    def test_no_documents_or_dirty_untracked_cache_db_or_git_bytes_are_changed(self):
        for path in ("app/dirty.py", "new-untracked.md", ".git/index", ".git/HEAD", ".env",
                     "data/synthetic.db", "node_modules/synthetic.txt", "docs/runs/RUN-100.md"):
            self.fixture.write(path, "synthetic bytes only: " + path)
        before = self.snapshot()
        result = self.migrate()
        after = self.snapshot()
        for path, data in before.items():
            if path != "session.json":
                self.assertEqual(after[path], data, path)
        self.assertEqual(set(after) - set(before), {result["backup"]})
        backup = migration._read_backup(self.root, result["backup"])[0]
        self.assertEqual(set(backup), {"kind", "schema_version", "original_base64", "previous_revision", "migrated_revision", "preview_key"})

    def test_only_valid_unmarked_product_is_accepted(self):
        cases = [{"profile": "audit"}, {"profile": "poc"}, {"process_model": None},
                 {"process_model": "unknown"}, {"current_gate": "mystery"}, {"gate_status": {}},
                 {"gate_status": {**self.legacy["gate_status"], "gate4": "Pass"}},
                 {"current_work": {}}, {"work_history": []}, {"migration": {}}]
        for changes in cases:
            with self.subTest(changes=changes):
                self.path.write_text(json.dumps({**self.legacy, **changes}))
                before = self.path.read_bytes()
                self.assertEqual(self.call(self.request())["status"], "invalid")
                self.assertEqual(self.path.read_bytes(), before)
        self.path.unlink()
        self.assertEqual(self.call(self.request())["status"], "invalid")
        self.assertFalse((self.root / ".vulcan").exists())

    def test_invalid_request_does_not_grant_permissions_or_ignore_fields(self):
        for extra in ({"target": "impl"}, {"decision": {}}, {"approved": True},
                      {"obligation_review": "complete"}, {"preview_key": 12}, {"preview_key": "latest"},
                      {"obligations": [{}]}, {"obligations": [{**self.request()["obligations"][0], "status": "closed"}]}):
            with self.subTest(extra=extra):
                self.assertEqual(self.call(self.request(**extra))["status"], "invalid")
        self.assertEqual(self.call(self.request(), True)["status"], "invalid")
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertFalse((self.root / ".vulcan").exists())

    def test_empty_scope_and_unreviewed_obligations_do_not_invent_ids_or_success(self):
        scope = {"work": self.scope["work"], "contracts": [], "tests": [], "related_ids": [], "required_checks": []}
        result = self.prepare(self.request(scope=scope, obligations=[]))
        self.assertEqual(result["proposed_scope"]["related_ids"], [])
        self.assertEqual(result["migration"]["obligation_review"], "pending")
        self.assertEqual(result["migration"]["legacy_gate_status"]["gate4"], "pending")

    def test_changed_session_or_plan_after_preview_is_conflict(self):
        request = self.prepare()["prepared_request"]
        changed = deepcopy(request)
        changed["obligations"][0]["owner"] = "Someone else"
        self.assertEqual(self.call(changed, True)["status"], "conflict")
        self.path.write_bytes(self.original + b"\n")
        self.assertEqual(self.call(request, True)["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), self.original + b"\n")

    def test_changed_input_after_preview_and_during_save_are_conflicts(self):
        refs = [self.scope["work"], *self.scope["contracts"], *self.scope["tests"],
                self.request()["reason"], self.request()["obligations"][0]["source"]]
        for filename in {ref["ref"].split("#")[0] for ref in refs}:
            path = self.root / filename
            with self.subTest(filename=filename):
                request = self.prepare()["prepared_request"]
                original = path.read_bytes()
                path.write_bytes(original + b"changed")
                self.assertEqual(self.call(request, True)["status"], "conflict")
                path.write_bytes(original)
        request = self.prepare()["prepared_request"]
        save = store._save
        def race(*args, **kwargs):
            self.fixture.write("docs/work.md", "changed while serializing")
            return save(*args, **kwargs)
        with mock.patch.object(store, "_save", side_effect=race):
            result = self.call(request, True)
        self.assertEqual(result["status"], "conflict", result)
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_stale_preview_cannot_be_replaced_by_claiming_a_fresh_revision(self):
        request = self.prepare()["prepared_request"]
        self.path.write_bytes(self.original + b"\n")
        request["expected_session_revision"] = store.revision(self.path.read_bytes())
        self.assertEqual(self.call(request, True)["status"], "conflict")

    def test_backup_failure_and_corrupt_existing_record_never_replace_session(self):
        preview = self.prepare()
        with mock.patch.object(migration, "_preserve", side_effect=OSError("backup not writable")):
            result = self.call(preview["prepared_request"], True)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(self.path.read_bytes(), self.original)
        self.fixture.write(preview["backup"], "partial interrupted backup")
        result = self.call(preview["prepared_request"], True)
        self.assertEqual(result["status"], "conflict")
        self.assertEqual((self.root / preview["backup"]).read_text(), "partial interrupted backup")
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_save_failure_preserves_backup_and_retry_reuses_it(self):
        preview = self.prepare()
        request = preview["prepared_request"]
        with mock.patch.object(store.os, "replace", side_effect=OSError("interrupted replace")):
            failed = self.call(request, True)
        self.assertEqual(failed["status"], "invalid")
        self.assertEqual(self.path.read_bytes(), self.original)
        path = self.root / preview["backup"]
        record = path.read_bytes()
        self.assertEqual(migration._read_backup(self.root, preview["backup"])[1], self.original)
        result = self.call(request, True)
        self.assertEqual(result["status"], "applied")
        self.assertEqual(path.read_bytes(), record)
        self.assertEqual(self.call(request, True)["status"], "conflict")
        self.assertEqual(list(self.root.glob(".product-session-*.tmp")), [])

    def test_concurrent_apply_and_lock_collision_are_safe(self):
        request = self.prepare()["prepared_request"]
        self.fixture.write(".vulcan/product-process.lock", "existing writer")
        self.assertEqual(self.call(request, True)["status"], "conflict")
        (self.root / ".vulcan/product-process.lock").unlink()
        barrier = threading.Barrier(2)
        def run():
            barrier.wait(timeout=10)
            return self.call(deepcopy(request), True)["status"]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run), executor.submit(run)]
            self.assertEqual(sorted(f.result(timeout=20) for f in futures), ["applied", "conflict"])

    def test_restore_preview_and_apply_restore_exact_original_not_other_files(self):
        migrated = self.migrate()
        request = self.restore_request(migrated)
        before = self.snapshot()
        preview = self.prepare(request)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(preview["proposed_gate"], "gate1")
        self.fixture.write("new-after-migration.md", "keep this unrelated edit")
        result = self.call(preview["prepared_request"], True)
        self.assertEqual(result["status"], "applied", result)
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual((self.root / "new-after-migration.md").read_text(), "keep this unrelated edit")
        self.assertTrue((self.root / migrated["backup"]).exists())
        self.assertNotEqual(self.call(preview["prepared_request"], True)["status"], "applied")

    def test_restore_refuses_later_session_changes_even_with_fresh_expected_revision(self):
        migrated = self.migrate()
        request = self.restore_request(migrated)
        current = json.loads(self.path.read_bytes())
        current["custom_setting"] = "new setting"
        self.path.write_text(json.dumps(current))
        before = self.path.read_bytes()
        request["expected_session_revision"] = store.revision(before)
        self.assertEqual(self.call(request)["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_work_preserves_handover_but_blocks_restore(self):
        migrated = self.migrate()
        current = json.loads(self.path.read_bytes())
        scope = deepcopy(self.scope)
        scope["work"]["revision"] = "snapshot:next"
        request = {"process_model": process.MODEL, "action": "open-work", "target": "planning",
                   "scope": scope, "reason": helpers.ref("decision:next"),
                   "expected_session_revision": store.revision(self.path.read_bytes())}
        self.assertEqual(self.call(request, True)["status"], "applied")
        after = json.loads(self.path.read_bytes())
        self.assertEqual(after["migration"], current["migration"])
        self.assertEqual(after["open_issues"], self.legacy["open_issues"])
        self.assertEqual(self.call(self.restore_request(migrated))["status"], "conflict")

    def test_malformed_handover_is_diagnosed_not_rendered_as_complete(self):
        self.migrate()
        current = json.loads(self.path.read_bytes())
        for bad in ({}, {**current["migration"], "obligations": [{}]}):
            current["migration"] = bad
            self.assertEqual(process.describe(current)["status"], "unsupported_or_invalid")

    def test_session_race_at_save_and_backup_tampering_are_rejected(self):
        preview = self.prepare()
        save = store._save
        foreign = self.original + b"\n"
        def race(*args, **kwargs):
            self.path.write_bytes(foreign)
            return save(*args, **kwargs)
        with mock.patch.object(store, "_save", side_effect=race):
            self.assertEqual(self.call(preview["prepared_request"], True)["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), foreign)
        self.path.write_bytes(self.original)
        def tamper(*args, **kwargs):
            path = self.root / preview["backup"]
            path.write_bytes(path.read_bytes() + b"\n")
            return save(*args, **kwargs)
        with mock.patch.object(store, "_save", side_effect=tamper):
            self.assertEqual(self.call(preview["prepared_request"], True)["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_lock_cleanup_warning_preserves_successful_apply_result(self):
        request = self.prepare()["prepared_request"]
        unlink = Path.unlink
        def fail_lock(path, *args, **kwargs):
            if path.name == "product-process.lock":
                raise OSError("cleanup failed")
            return unlink(path, *args, **kwargs)
        with mock.patch.object(Path, "unlink", fail_lock):
            result = self.call(request, True)
        self.assertEqual(result["status"], "applied")
        self.assertTrue(result["applied"])
        self.assertIn("writer lock cleanup failed", result["warnings"][0])

    def test_restore_backup_integrity_failure_and_write_failure_are_safe(self):
        migrated = self.migrate()
        preview = self.prepare(self.restore_request(migrated))
        current = self.path.read_bytes()
        with mock.patch.object(store.os, "replace", side_effect=OSError("restore write failure")):
            self.assertEqual(self.call(preview["prepared_request"], True)["status"], "invalid")
        self.assertEqual(self.path.read_bytes(), current)
        backup = self.root / migrated["backup"]
        record = json.loads(backup.read_bytes())
        record["original_base64"] = "AAAA"
        backup.write_text(json.dumps(record))
        self.assertEqual(self.call(preview["prepared_request"], True)["status"], "invalid")
        self.assertEqual(self.path.read_bytes(), current)

    def test_invalid_or_symlink_input_paths_are_rejected_without_backup(self):
        for ref in ("../outside.md", ".env", "https://example.com/doc", "C:/private.md"):
            result = self.call(self.request(reason={"ref": ref, "revision": "sha256:" + "a" * 64}))
            self.assertEqual(result["status"], "invalid", result)
        link = self.root / "docs/link.md"
        try:
            link.symlink_to(self.root / "docs/work.md")
        except OSError:
            return
        self.assertEqual(self.call(self.request(reason={"ref": "docs/link.md", "revision": self.scope["work"]["revision"]}))["status"], "invalid")
        self.assertFalse((self.root / ".vulcan").exists())

    def test_cli_migrate_preview_apply_status_and_restore(self):
        def cli(request, apply=False):
            args = [sys.executable, str(helpers.ROOT / "vulcan.py"), "session", "--process-request", "-", "--json"]
            if apply:
                args.append("--apply")
            result = subprocess.run(args, input=json.dumps(request), cwd=self.root, capture_output=True,
                                    text=True, encoding="utf-8", timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return json.loads(result.stdout)
        preview = cli(self.request())
        self.assertEqual(self.path.read_bytes(), self.original)
        result = cli(preview["prepared_request"], True)
        status = subprocess.run([sys.executable, str(helpers.ROOT / "vulcan.py"), "status", "--json"],
                                cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertEqual(json.loads(status.stdout)["migration_handover"]["obligations"][0]["status"], "open")
        restore = cli(self.restore_request(result))
        cli(restore["prepared_request"], True)
        self.assertEqual(self.path.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
