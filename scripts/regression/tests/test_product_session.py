"""Persisted Product pilot: previews, authority, evidence, iteration and CAS."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest import mock

from vulcan_core import product_process as process, product_session as store
import test_product_process as helpers
import test_product_readiness as fixtures


class ProductSessionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ScopedReadinessTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.path = self.root / "session.json"
        self.parse = helpers.vulcan.parse_markdown_tables

    def read(self):
        return json.loads(self.path.read_bytes())

    def request(self, action, **extra):
        return {"process_model": process.MODEL, "action": action,
                "expected_session_revision": store.revision(self.path.read_bytes()) if self.path.exists() else None, **extra}

    def apply(self, request):
        result = store.transact(self.root, request, self.parse, apply=True)
        self.assertEqual(result["status"], "applied", result)
        return result

    def start(self):
        return self.apply(self.request("start", scope=self.fixture.scope))

    def implementation(self):
        self.start()
        return self.apply(self.request("advance", target="impl", decision=helpers.decision(self.read())))

    def acceptance(self):
        self.implementation()
        return self.apply(self.request("advance", target="acceptance", basis=self.fixture.basis()))

    def cli(self, args, request=None):
        return subprocess.run([sys.executable, str(helpers.ROOT / "vulcan.py"), *args], cwd=self.root,
            input=json.dumps(request) if request is not None else None, capture_output=True,
            text=True, encoding="utf-8", timeout=30)

    def cli_request(self, request, apply=True):
        args = ["session", "--process-request", "-", "--json"]
        if apply:
            args.append("--apply")
        return self.cli(args, request)

    def observed_results(self):
        (self.root / "evidence").mkdir()
        args = ["execute", "--verify"]
        for source in self.fixture.sources:
            args.extend(["--source", source])
        command = [sys.executable, "tests/check.py"]
        result = self.cli([*args, "--evidence", "evidence/results.json", "--", *command])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return {"scope_key": self.read()["current_work"]["scope_key"], "basis": self.fixture.basis(),
                "results": [{"id": name, "status": "Pass", "command": command,
                             "evidence": self.fixture.ref("evidence/results.json")}
                            for name in self.fixture.scope["required_checks"]]}

    def test_cli_lifecycle_and_new_work_preserve_history_without_hidden_gates(self):
        start = self.cli_request(self.request("start", scope=self.fixture.scope))
        self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
        planning = self.read()
        impl = self.cli_request(self.request("advance", target="impl", decision=helpers.decision(planning)))
        self.assertEqual(impl.returncode, 0, impl.stdout + impl.stderr)
        qa = self.cli_request(self.request("advance", target="acceptance", basis=self.fixture.basis()))
        self.assertEqual(qa.returncode, 0, qa.stdout + qa.stderr)
        verification = self.observed_results()
        request = self.request("advance", target="completed", verification=verification)
        before = self.path.read_bytes()
        preview = self.cli_request(request, apply=False)
        self.assertEqual(preview.returncode, 1, preview.stdout + preview.stderr)
        result = json.loads(preview.stdout)
        self.assertEqual(result["checks"]["execution"], "verified_observations")
        self.assertEqual(self.path.read_bytes(), before)
        request["decision"] = helpers.decision(self.read(), ["accept"], verification_key=result["checks"]["verification_key"])
        done = self.cli_request(request)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertFalse(json.loads(done.stdout)["release_authorized"])
        completed = self.read()
        self.assertEqual(completed["current_gate"], "completed")
        self.assertEqual(set(completed["gate_status"]), set(process.STAGES))
        self.assertEqual(len(completed["work_history"]), 3)
        new_scope = deepcopy(self.fixture.scope)
        new_scope["work"]["revision"] = "snapshot:2"
        next_work = self.cli_request(self.request("open-work", scope=new_scope, target="planning", reason=helpers.ref("issue:next")))
        self.assertEqual(next_work.returncode, 0, next_work.stdout + next_work.stderr)
        self.assertEqual(self.read()["current_gate"], "planning")
        self.assertEqual(self.read()["work_history"][-1]["work"], completed["current_work"])
        self.assertEqual(self.read()["current_work"]["decisions"], [])
        self.assertFalse((self.root / "docs/runs").exists())
        self.assertFalse((self.root / ".git").exists())

    def test_default_cli_preview_does_not_create_state_or_lock(self):
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.cli_request(self.request("start", scope=self.fixture.scope), apply=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "ready")
        self.assertFalse(json.loads(result.stdout)["applied"])
        self.assertIsNone(json.loads(result.stdout)["current_gate"])
        self.assertEqual(json.loads(result.stdout)["proposed_gate"], "planning")
        self.assertFalse(self.path.exists())
        self.assertFalse((self.root / ".vulcan").exists())
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_status_reports_observed_session_revision(self):
        self.start()
        result = self.cli(["status", "--json"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["session_revision"], store.revision(self.path.read_bytes()))

    def test_ready_preview_does_not_bypass_later_contract_changes_or_authority(self):
        self.start()
        request = self.request("advance", target="impl", decision=helpers.decision(self.read()))
        preview = store.transact(self.root, request, self.parse)
        self.assertEqual(preview["status"], "ready")
        self.assertEqual(preview["current_gate"], "planning")
        self.assertEqual(preview["proposed_gate"], "impl")
        self.fixture.write("docs/contracts.md", "# Changed\n")
        before = self.path.read_bytes()
        result = store.transact(self.root, request, self.parse, apply=True)
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(self.path.read_bytes(), before)
        self.fixture.write("docs/contracts.md", fixtures.CONTRACT)
        request.pop("decision")
        result = store.transact(self.root, request, self.parse, apply=True)
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(self.path.read_bytes(), before)

    def test_reused_request_and_foreign_revision_cannot_overwrite_new_state(self):
        self.start()
        request = self.request("advance", target="impl", decision=helpers.decision(self.read()))
        self.apply(request)
        before = self.path.read_bytes()
        self.assertEqual(store.transact(self.root, request, self.parse, apply=True)["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), before)

    def test_atomic_write_failure_retains_session_and_removes_temporary_file(self):
        self.start()
        before = self.path.read_bytes()
        request = self.request("advance", target="impl", decision=helpers.decision(self.read()))
        with mock.patch.object(store.os, "replace", side_effect=OSError("simulated save failure")):
            result = store.transact(self.root, request, self.parse, apply=True)
        self.assertEqual(result["status"], "invalid")
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.root.glob(".product-session-*.tmp")), [])
        self.assertFalse((self.root / ".vulcan/product-process.lock").exists())

    def test_lock_collision_and_parallel_apply_allow_only_one_writer(self):
        self.start()
        request = self.request("advance", target="impl", decision=helpers.decision(self.read()))
        self.fixture.write(".vulcan/product-process.lock", "another writer")
        before = self.path.read_bytes()
        self.assertEqual(store.transact(self.root, request, self.parse, apply=True)["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), before)
        (self.root / ".vulcan/product-process.lock").unlink()
        barrier = threading.Barrier(2)
        def run():
            barrier.wait(timeout=10)
            return store.transact(self.root, deepcopy(request), self.parse, apply=True)["status"]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run), executor.submit(run)]
            statuses = sorted(f.result(timeout=30) for f in futures)
        self.assertEqual(statuses, ["applied", "conflict"])
        self.assertEqual(len(self.read()["work_history"]), 1)

    def test_session_change_during_checks_is_not_overwritten(self):
        self.start()
        request = self.request("advance", target="impl", decision=helpers.decision(self.read()))
        collect = store.readiness.collect
        foreign = self.read()
        foreign["open_issues"] = ["ISSUE-001"]
        foreign_bytes = json.dumps(foreign).encode()
        def changed(*args):
            result = collect(*args)
            self.path.write_bytes(foreign_bytes)
            return result
        with mock.patch.object(store.readiness, "collect", side_effect=changed):
            result = store.transact(self.root, request, self.parse, apply=True)
        self.assertEqual(result["status"], "conflict")
        self.assertEqual(self.path.read_bytes(), foreign_bytes)

    def test_lock_cleanup_failure_does_not_report_applied_state_as_unwritten(self):
        with mock.patch.object(Path, "unlink", side_effect=OSError("cleanup blocked")):
            result = self.start()
        self.assertTrue(result["applied"])
        self.assertIn("cleanup failed", result["warnings"][0])
        self.assertEqual(self.read()["current_gate"], "planning")

    def test_fix_and_replanning_preserve_obligations_without_new_gates(self):
        self.acceptance()
        current = self.read()
        current["open_issues"] = ["ISSUE-OTHER"]
        current["current_work"]["observations"] = [{"status": "Fail", "evidence": helpers.ref("logs/prior-fail")}]
        self.path.write_text(json.dumps(current))
        self.apply(self.request("advance", target="impl", reason=helpers.ref("finding:1")))
        self.assertEqual(self.read()["open_issues"], ["ISSUE-OTHER"])
        self.assertEqual(self.read()["work_history"][-1]["work"]["observations"][0]["status"], "Fail")
        self.apply(self.request("advance", target="planning", reason=helpers.ref("decision:scope-change")))
        self.assertEqual(self.read()["current_work"]["decisions"], [])

    def test_verification_only_authority_cannot_authorize_fix(self):
        self.start()
        permit = helpers.decision(self.read(), ["implement", "verify"])
        self.apply(self.request("advance", target="impl", decision=permit))
        self.apply(self.request("advance", target="acceptance", basis=self.fixture.basis()))
        before = self.path.read_bytes()
        result = store.transact(self.root, self.request("advance", target="impl", reason=helpers.ref("finding:1")), self.parse, apply=True)
        self.assertNotEqual(result["status"], "applied")
        self.assertEqual(self.path.read_bytes(), before)

    def test_changed_source_or_environment_blocks_acceptance_write(self):
        self.acceptance()
        verification = self.observed_results()
        key = process.verification_key(self.fixture.scope, verification, self.fixture.basis())
        request = self.request("advance", target="completed", verification=verification,
                               decision=helpers.decision(self.read(), ["accept"], verification_key=key))
        before = self.path.read_bytes()
        self.fixture.write("app.py", "value = 2\n")
        result = store.transact(self.root, request, self.parse, apply=True)
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(self.path.read_bytes(), before)

    def test_legacy_sessions_and_mixed_flags_cannot_enter_the_pilot(self):
        for profile in ("product", "audit", "poc"):
            original = json.dumps({"profile": profile, "current_gate": "gate2"}).encode()
            self.path.write_bytes(original)
            request = self.request("open-work", scope=self.fixture.scope, target="planning", reason=helpers.ref("not-migration"))
            result = self.cli_request(request)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(self.path.read_bytes(), original)
        result = self.cli(["session", "--process-request", "-", "--approved"], request)
        self.assertEqual(result.returncode, 2)
        result = self.cli(["session"])
        self.assertEqual(result.returncode, 2)

    def test_verification_command_cannot_run_during_planning(self):
        self.start()
        result = self.cli(["execute", "--verify", "--source", "app.py", "--evidence", "NO.json", "--",
                           sys.executable, "-c", "open('SHOULD_NOT_EXIST', 'w').close()"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse((self.root / "SHOULD_NOT_EXIST").exists())

    def test_implementation_self_check_is_not_acceptance_authority(self):
        self.start()
        self.apply(self.request("advance", target="impl", decision=helpers.decision(self.read(), ["implement"])))
        before = self.path.read_bytes()
        verification = self.observed_results()
        self.assertEqual(self.path.read_bytes(), before)
        handoff = store.transact(self.root, self.request("advance", target="acceptance", basis=self.fixture.basis()), self.parse, apply=True)
        self.assertEqual(handoff["status"], "blocked", handoff)
        self.assertIn("missing scoped verify", str(handoff["checks"]["transition"]))
        finish = store.transact(self.root, self.request("advance", target="completed", verification=verification), self.parse, apply=True)
        self.assertFalse(finish["applied"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_deep_json_returns_structured_invalid_instead_of_traceback(self):
        raw = '{"x":' + '[' * 20_000 + '0' + ']' * 20_000 + '}'
        result = subprocess.run([sys.executable, str(helpers.ROOT / "vulcan.py"), "session", "--process-request", "-", "--json"],
                                cwd=self.root, input=raw, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.path.exists())

    def test_invalid_and_ignored_payload_fields_fail_closed(self):
        for raw in (b'{"action":"start", "action":"advance"}', b'{"x":NaN}', b'[]', b'null'):
            with self.assertRaises(ValueError):
                store.decode(raw)
        for extra in ({"process_model": "other"}, {"approved": True}, {"readiness": {"ready": True}},
                      {"action": []}, {"expected_session_revision": "HEAD"}):
            request = self.request("start", scope=self.fixture.scope)
            request.update(extra)
            self.assertEqual(store.transact(self.root, request, self.parse)["status"], "invalid")
        self.assertFalse(self.path.exists())


if __name__ == "__main__":
    unittest.main()
