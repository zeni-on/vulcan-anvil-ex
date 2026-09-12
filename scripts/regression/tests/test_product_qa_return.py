"""Path-only QA results reuse command records without granting acceptance."""

from copy import deepcopy
import json
import unittest
from unittest import mock

from vulcan_core import product_qa as qa, product_session as store
import test_product_process as helpers
import test_product_session as sessions


class ProductQAReturnTests(unittest.TestCase):
    def setUp(self):
        self.fixture = sessions.ProductSessionTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.acceptance()
        self.root = self.fixture.root
        self.observed = self.fixture.observed_results()
        self.request = qa.handoff(self.root, {"integration_branch": "dev"}, self.fixture.parse)["return_request"]
        self.request["verification"]["results"] = [
            {"id": row["id"], "status": row["status"], "evidence": row["evidence"]["ref"]}
            for row in self.observed["results"]]
        self.report = self.root / "evidence/results.json"

    def preview(self, request=None):
        return store.transact(self.root, self.request if request is None else request, self.fixture.parse)

    def files(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_preview_expands_exact_record_preserves_input_and_requires_accept(self):
        original = deepcopy(self.request)
        before = self.files()
        result = self.preview()
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(result["checks"]["execution"], "verified_observations")
        self.assertIn("missing scoped accept decision", result["checks"]["transition"]["reasons"])
        prepared = result["prepared_request"]
        self.assertEqual(prepared["verification"], self.observed)
        self.assertEqual(prepared["expected_session_revision"], self.request["expected_session_revision"])
        self.assertNotIn("decision", prepared)
        self.assertEqual(self.request, original)
        self.assertEqual(self.files(), before)
        prepared["decision"] = helpers.decision(self.fixture.read(), ["accept"],
            verification_key=result["checks"]["verification_key"])
        accepted = store.transact(self.root, prepared, self.fixture.parse, apply=True)
        self.assertEqual(accepted["status"], "applied", accepted)
        self.assertFalse(accepted["release_authorized"])
        self.assertEqual(self.fixture.read()["current_work"]["verification"], self.observed)

    def test_cli_stdin_and_file_preview_need_no_new_cli_or_helper(self):
        self.fixture.fixture.write("return.json", json.dumps(self.request))
        before = self.files()
        for source in ("-", "return.json"):
            command = self.fixture.cli(["session", "--process-request", source, "--json"],
                                       request=self.request if source == "-" else None)
            self.assertEqual(command.returncode, 1, command.stdout + command.stderr)
            result = json.loads(command.stdout)
            self.assertEqual(result["prepared_request"]["verification"], self.observed)
            self.assertIn("verification_key", result["checks"])
        self.assertEqual(self.files(), before)

    def test_text_preview_summarizes_prepared_request_instead_of_dumping_it(self):
        command = self.fixture.cli(["session", "--process-request", "-"], request=self.request)
        self.assertEqual(command.returncode, 1, command.stdout + command.stderr)
        self.assertIn("prepared_request: available with --json", command.stdout)
        self.assertNotIn("'results':", command.stdout)

    def test_compact_apply_and_decision_injection_are_rejected(self):
        before = self.files()
        applied = store.transact(self.root, self.request, self.fixture.parse, apply=True)
        self.assertEqual(applied["status"], "invalid", applied)
        request = deepcopy(self.request)
        request["decision"] = helpers.decision(self.fixture.read(), ["accept"], verification_key="not-approved")
        result = self.preview(request)
        self.assertEqual(result["status"], "invalid", result)
        self.assertNotIn("prepared_request", result)
        self.assertEqual(self.files(), before)

    def test_stale_session_is_not_rebound_and_report_is_not_read(self):
        self.fixture.path.write_bytes(self.fixture.path.read_bytes() + b"\n")
        with mock.patch.object(store.readiness, "_content", side_effect=AssertionError("must not read evidence")):
            result = self.preview()
        self.assertEqual(result["status"], "conflict", result)
        self.assertNotIn("prepared_request", result)

    def test_session_change_during_preparation_returns_conflict(self):
        load = store._load
        calls = []

        def changed(root):
            calls.append(root)
            if len(calls) == 2:
                self.fixture.path.write_bytes(self.fixture.path.read_bytes() + b"\n")
            return load(root)

        with mock.patch.object(store, "_load", side_effect=changed):
            result = self.preview()
        self.assertEqual(result["status"], "conflict", result)
        self.assertNotIn("prepared_request", result)

    def test_changed_report_after_preview_invalidates_prepared_acceptance(self):
        result = self.preview()
        prepared = result["prepared_request"]
        prepared["decision"] = helpers.decision(self.fixture.read(), ["accept"],
            verification_key=result["checks"]["verification_key"])
        self.report.write_bytes(self.report.read_bytes() + b"\n")
        before = self.files()
        result = store.transact(self.root, prepared, self.fixture.parse, apply=True)
        self.assertEqual(result["status"], "blocked", result)
        self.assertIn("artifact revision changed", str(result))
        self.assertEqual(self.files(), before)

    def test_nonpass_status_is_preserved_and_never_has_acceptance_key(self):
        before = self.files()
        for status in ("Fail", "Not Run", "environment_blocked", "Skipped"):
            with self.subTest(status=status):
                request = deepcopy(self.request)
                request["verification"]["results"][0]["status"] = status
                result = self.preview(request)
                self.assertEqual(result["status"], "blocked", result)
                self.assertEqual(result["prepared_request"]["verification"]["results"][0]["status"], status)
                self.assertNotIn("verification_key", result["checks"])
        self.assertEqual(self.files(), before)

    def test_failed_or_launch_blocked_record_is_not_promoted_by_claimed_pass(self):
        original = json.loads(self.report.read_bytes())
        for exit_code, launch_error in ((1, None), (127, "FileNotFoundError")):
            report = deepcopy(original)
            report["command"].update(exit_code=exit_code, launch_error=launch_error)
            self.report.write_text(json.dumps(report), encoding="utf-8")
            before = self.files()
            result = self.preview()
            self.assertEqual(result["status"], "blocked", result)
            self.assertIn("unsuccessful", str(result))
            self.assertNotIn("verification_key", result["checks"])
            self.assertEqual(self.files(), before)

    def test_missing_duplicate_or_out_of_scope_ids_are_not_silently_filled(self):
        rows = self.request["verification"]["results"]
        for changed in (rows[:-1], rows + [rows[0]], [{**rows[0], "id": "FOREIGN-001"}, *rows[1:]]):
            request = deepcopy(self.request)
            request["verification"]["results"] = changed
            result = self.preview(request)
            self.assertEqual(result["status"], "invalid", result)
            self.assertIn("exactly once", result["message"])
            self.assertNotIn("prepared_request", result)

    def test_path_boundaries_missing_and_invalid_artifacts_are_rejected(self):
        self.fixture.fixture.write("evidence/bad.json", '{"schema_version":2,"schema_version":2}')
        self.fixture.fixture.write(".env", "SECRET=private")
        for reference in ("../escape.json", "C:/outside.json", "https://example.invalid/result.json",
                          "evidence/results.json#fragment", ".env", "evidence/missing.json",
                          "evidence", "docs/contracts.md", "evidence/bad.json", "evidence/results.json?x=1"):
            with self.subTest(reference=reference):
                request = deepcopy(self.request)
                request["verification"]["results"][0]["evidence"] = reference
                result = self.preview(request)
                self.assertEqual(result["status"], "invalid", result)
                self.assertNotIn("prepared_request", result)

    def test_compact_rows_reject_overrides_and_unknown_or_unhashable_status(self):
        for extra in ({"command": ["do-not-execute"]}, {"approved": True}, {"status": "Success"}, {"status": []}):
            request = deepcopy(self.request)
            request["verification"]["results"][0].update(extra)
            result = self.preview(request)
            self.assertEqual(result["status"], "invalid", result)
            self.assertNotIn("prepared_request", result)

    def test_full_and_mixed_rows_keep_existing_explicit_contract(self):
        request = deepcopy(self.request)
        request["verification"]["results"][0] = deepcopy(self.observed["results"][0])
        result = self.preview(request)
        self.assertEqual(result["prepared_request"]["verification"], self.observed)
        full = deepcopy(self.request)
        full["verification"] = self.observed
        self.assertNotIn("prepared_request", self.preview(full))

    def test_malformed_report_cannot_supply_command_fields(self):
        original = json.loads(self.report.read_bytes())
        malformed = [{**original, "schema_version": True}, {**original, "kind": "other"}]
        for values in ({"argv": []}, {"argv": ["x", None]}, {"exit_code": True},
                       {"started_at": None}, {"finished_at": ""}, {"launch_error": []}):
            malformed.append({**original, "command": {**original["command"], **values}})
        for report in malformed:
            self.report.write_text(json.dumps(report), encoding="utf-8")
            result = self.preview()
            self.assertEqual(result["status"], "invalid", result)
            self.assertNotIn("prepared_request", result)

    def test_expanded_commands_cannot_exceed_existing_request_budget(self):
        report = json.loads(self.report.read_bytes())
        report["command"]["argv"] = ["not-executed", "x" * 1000]
        self.report.write_text(json.dumps(report), encoding="utf-8")
        before = self.files()
        with mock.patch.object(store, "MAX_REQUEST_BYTES", len(json.dumps(self.request)) + 500):
            result = self.preview()
        self.assertEqual(result["status"], "invalid", result)
        self.assertIn("size limit", result["message"])
        self.assertNotIn("prepared_request", result)
        self.assertEqual(self.files(), before)

    def test_wrong_scope_environment_contract_and_stage_do_not_get_approved(self):
        request = deepcopy(self.request)
        request["verification"]["scope_key"] = "foreign"
        self.assertEqual(self.preview(request)["status"], "invalid")
        for name in ("environment.json", "docs/contracts.md", "docs/tests.md"):
            path = self.root / name
            original = path.read_bytes()
            path.write_bytes(original + b"\n")
            result = self.preview()
            self.assertEqual(result["status"], "blocked", result)
            path.write_bytes(original)
        state = self.fixture.read()
        state["current_gate"] = "impl"
        self.fixture.path.write_text(json.dumps(state), encoding="utf-8")
        request = deepcopy(self.request)
        request["expected_session_revision"] = store.revision(self.fixture.path.read_bytes())
        self.assertEqual(self.preview(request)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
