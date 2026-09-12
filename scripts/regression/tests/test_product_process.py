"""Product contract prototype: scope, permission, evidence and legacy boundaries."""

from copy import deepcopy
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from vulcan_core import product_process as process


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("vulcan_process_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


def ref(name, revision="snapshot:001"):
    return {"ref": name, "revision": revision}


def scope(number=1):
    return {"work": ref("issue:request-resubmit", f"snapshot:{number:03}"),
            "related_ids": ["SCN-001", "REQ-001", "SEC-001"],
            "contracts": [ref("docs/requests.md#resubmit"), ref("docs/security.md#access")],
            "tests": [ref("docs/tests.md#resubmit")], "required_checks": ["REG-001", "SEC-REG-001"]}


def basis(environment="snapshot:001"):
    return {"environment": ref("qa-environment", environment)}


def ready(session, purpose="implementation"):
    return {"scope_key": session["current_work"]["scope_key"], "ready": True,
            "purpose": purpose, "evidence": ref("review:readiness")}


def decision(session, actions=None, **extra):
    return {"scope_key": session["current_work"]["scope_key"], "actor": "project-owner",
            "authority": "user", "actions": actions or ["implement", "verify", "fix"],
            "evidence": ref("conversation:decision-001"), **extra}


def verification(session, tested=None):
    return {"scope_key": session["current_work"]["scope_key"], "basis": tested or basis(),
            "results": [{"id": name, "status": "Pass", "command": ["python", "-m", "unittest", name],
                         "evidence": ref("logs/" + name)}
                        for name in session["current_work"]["scope"]["required_checks"]]}


class ProductProcessTests(unittest.TestCase):
    def implementation(self):
        session = process.new_session(scope())
        return process.advance(session, "impl", readiness=ready(session), decision=decision(session))

    def acceptance(self):
        session = self.implementation()
        return process.advance(session, "acceptance", readiness=ready(session, "handoff"), current_basis=basis())

    def completed(self):
        session = self.acceptance()
        report = verification(session)
        key = process.verification_key(scope(), report, basis())
        return process.advance(session, "completed", verification=report, current_basis=basis(),
                               decision=decision(session, ["accept"], verification_key=key))

    def denied(self, session, target, contains, **kwargs):
        before = deepcopy(session)
        result = process.assess_transition(session, target, **kwargs)
        self.assertFalse(result["allowed"], result)
        self.assertIn(contains, result["reasons"][0])
        with self.assertRaises(process.ProcessContractError):
            process.advance(session, target, **kwargs)
        self.assertEqual(session, before)

    def test_complete_flow_is_pure_and_does_not_authorize_release(self):
        completed = self.completed()
        self.assertEqual(completed["current_gate"], "completed")
        self.assertEqual(completed["gate_status"], dict.fromkeys(process.STAGES, "done"))
        self.assertEqual(len(completed["work_history"]), 3)
        self.assertEqual(process.describe(completed)["status"], "active")
        self.assertNotIn("release", completed)
        for target in ("gate5", "release", "merge", "deploy", "push"):
            self.denied(completed, target, "invalid target")

    def test_readiness_is_not_permission(self):
        session = process.new_session(scope())
        self.denied(session, "impl", "missing scoped implement", readiness=ready(session))
        bad_ready = ready(session)
        bad_ready["ready"] = False
        self.denied(session, "impl", "not ready", readiness=bad_ready, decision=decision(session))
        bad_ready["ready"] = "true"
        self.denied(session, "impl", "not ready", readiness=bad_ready, decision=decision(session))

    def test_planning_can_be_incomplete_but_implementation_cannot(self):
        draft = scope()
        for field in ("related_ids", "contracts", "tests", "required_checks"):
            incomplete = deepcopy(draft)
            incomplete[field] = []
            session = process.new_session(incomplete)
            self.assertEqual(process.describe(session)["current_gate"], "planning")
            self.denied(session, "impl", "needs contract", readiness=ready(session), decision=decision(session))

    def test_scope_canonicalization_and_every_basis_component(self):
        original = scope()
        ordered = deepcopy(original)
        for field in ("related_ids", "contracts", "tests", "required_checks"):
            ordered[field].reverse()
        self.assertEqual(process.scope_key(original), process.scope_key(ordered))
        for field in ("work", "contracts", "tests", "related_ids", "required_checks"):
            changed = deepcopy(original)
            if field == "work":
                changed[field]["revision"] = "snapshot:002"
            elif field in {"contracts", "tests"}:
                changed[field][0]["revision"] = "snapshot:002"
            else:
                changed[field].append("NEW-002")
            session = process.new_session(changed)
            old_permission = decision(process.new_session(original))
            self.denied(session, "impl", "another scope/revision", readiness=ready(session), decision=old_permission)
        for field in ("related_ids", "contracts", "tests", "required_checks"):
            changed = deepcopy(original)
            changed[field].append(changed[field][0])
            with self.assertRaises(process.ProcessContractError):
                process.scope_key(changed)

    def test_approval_boolean_title_or_moving_branch_is_not_a_decision(self):
        session = process.new_session(scope())
        for invalid in (True, {"approved": True}, {"feature": "request-resubmit"},
                        decision(session, ["merge"]), decision(session, authority="reviewer"),
                        decision(session, authority="delegated"), decision(session, evidence=ref("chat", "HEAD"))):
            with self.subTest(invalid=invalid):
                self.assertFalse(process.assess_transition(session, "impl", readiness=ready(session), decision=invalid)["allowed"])
        delegated = decision(session, authority="delegated", authority_ref=ref("chat:owner-delegation"))
        self.assertTrue(process.assess_transition(session, "impl", readiness=ready(session), decision=delegated)["allowed"])

    def test_handoff_uses_existing_verify_authority_not_acceptance_results(self):
        session = self.implementation()
        self.denied(session, "acceptance", "wrong readiness purpose", readiness=ready(session), current_basis=basis())
        accepted_stage = self.acceptance()
        self.assertNotIn("verification", accepted_stage["current_work"])
        session["current_work"]["decisions"][0]["actions"] = ["implement"]
        self.denied(session, "acceptance", "missing scoped verify", readiness=ready(session, "handoff"), current_basis=basis())

    def test_fix_permission_reused_but_verification_only_worker_cannot_fix(self):
        session = self.acceptance()
        fixed = process.advance(session, "impl", reason=ref("finding:001"))
        self.assertEqual(fixed["current_gate"], "impl")
        self.assertEqual(fixed["gate_status"]["acceptance"], "pending")
        self.assertNotIn("verification_key", fixed["current_work"])
        session["current_work"]["decisions"][0]["actions"] = ["implement", "verify"]
        self.denied(session, "impl", "missing scoped fix", reason=ref("finding:001"))

    def test_acceptance_requires_real_results_and_scoped_acceptance_decision(self):
        session = self.acceptance()
        report = verification(session)
        self.denied(session, "completed", "missing scoped accept", verification=report, current_basis=basis())
        key = process.verification_key(scope(), report, basis())
        accept = decision(session, ["accept"], verification_key=key)
        for status in ("Fail", "Not Run", "Planned", "environment_blocked", "Pass with warnings", True):
            failed = deepcopy(report)
            failed["results"][0]["status"] = status
            self.denied(session, "completed", "not Pass", verification=failed, current_basis=basis(), decision=accept)
        for rows in ([], report["results"][:1], report["results"] * 2):
            failed = dict(report, results=rows)
            self.assertFalse(process.assess_transition(session, "completed", verification=failed,
                                                      current_basis=basis(), decision=accept)["allowed"])

    def test_changed_environment_or_test_evidence_invalidates_acceptance(self):
        session = self.acceptance()
        report = verification(session)
        accept = decision(session, ["accept"], verification_key=process.verification_key(scope(), report, basis()))
        self.denied(session, "completed", "stale verification", verification=report,
                    current_basis=basis(environment="snapshot:002"), decision=accept)
        changed_log = deepcopy(report)
        changed_log["results"][0]["evidence"]["revision"] = "snapshot:002"
        self.denied(session, "completed", "missing scoped accept", verification=changed_log, current_basis=basis(), decision=accept)

    def test_replanning_and_new_work_preserve_history_and_unresolved_obligations(self):
        session = self.acceptance()
        session["open_issues"] = ["ISSUE-001: environment blocked in another scope"]
        session["current_work"]["observations"] = [{"status": "Fail", "evidence": ref("logs/failed")}]
        changed = process.open_work(session, scope(2), reason=ref("decision:scope-change"))
        self.assertEqual(changed["current_work"]["decisions"], [])
        self.assertEqual(changed["open_issues"], session["open_issues"])
        self.assertEqual(changed["work_history"][-1]["work"]["observations"][0]["status"], "Fail")
        self.assertEqual(session["current_gate"], "acceptance")
        replanned = process.advance(session, "planning", reason=ref("question:expected-behavior"))
        self.assertEqual(replanned["current_work"]["decisions"], [])
        self.denied(replanned, "impl", "missing scoped implement", readiness=ready(replanned))
        done = self.completed()
        next_scope = scope(2)
        pending = process.new_session(next_scope)
        new_fix = process.open_work(done, next_scope, reason=ref("issue:local-fix"), target="impl",
                                    readiness=ready(pending), decision=decision(pending))
        self.assertEqual(new_fix["current_gate"], "impl")
        self.assertTrue(any(row["current_gate"] == "completed" for row in new_fix["work_history"]))
        with self.assertRaises(process.ProcessContractError):
            process.open_work(done, scope(), reason=ref("new-title-is-not-a-new-scope"))

    def test_legacy_and_unknown_models_are_never_reinterpreted(self):
        for profile in ("product", "audit", "poc"):
            legacy = {"profile": profile, "current_gate": "gate2"}
            before = deepcopy(legacy)
            self.assertEqual(process.describe(legacy), {"process_model": "legacy", "use_legacy": True})
            process.require_legacy(legacy)
            self.assertFalse(process.assess_transition(legacy, "impl")["allowed"])
            self.assertEqual(legacy, before)
        for marker in (None, "", "product-iterative-v2", 123):
            unknown = {"profile": "product", "process_model": marker}
            self.assertEqual(process.describe(unknown)["status"], "unsupported_or_invalid")
            with self.assertRaises(process.ProcessContractError):
                process.require_legacy(unknown)
        for profile in ("audit", "poc"):
            wrong = dict(process.new_session(scope()), profile=profile)
            self.assertEqual(process.describe(wrong)["status"], "unsupported_or_invalid")

    def test_invalid_state_and_forged_completion_are_diagnosed(self):
        for field, value in (("current_gate", "gate2"), ("gate_status", {}),
                             ("current_work", None), ("work_history", None)):
            session = process.new_session(scope())
            session[field] = value
            self.assertEqual(process.describe(session)["status"], "unsupported_or_invalid")
        session = process.new_session(scope())
        session.update(current_gate="completed", gate_status=dict.fromkeys(process.STAGES, "done"))
        self.assertEqual(process.describe(session)["status"], "unsupported_or_invalid")

    def test_malformed_decision_and_history_return_contract_diagnostics(self):
        for authority in ([], {}, None, 1):
            session = self.implementation()
            session["current_work"]["decisions"][0]["authority"] = authority
            self.assertEqual(process.describe(session)["status"], "unsupported_or_invalid")
            self.denied(session, "acceptance", "authority", readiness=ready(session, "handoff"), current_basis=basis())
        for history in ([{}], [None], [{"current_gate": "impl", "work": {"scope_key": []}}]):
            session = process.new_session(scope())
            session["work_history"] = history
            self.assertEqual(process.describe(session)["status"], "unsupported_or_invalid")
            with self.assertRaises(process.ProcessContractError):
                process.open_work(session, scope(2), reason=ref("scope-change"))
        with self.assertRaises(process.ProcessContractError):
            process.open_work(self.completed(), scope(2), reason=ref("new-work"), target=[])

    def test_legacy_approval_key_is_preserved_without_rechecking_source(self):
        session = self.acceptance()
        legacy_basis = dict(basis(), source={
            "fingerprint": "a" * 64, "complete": True, "errors": [],
            "sources": ["app", "requirements.txt", "tests"]})
        report = verification(session, legacy_basis)
        expected = process._digest({"scope_key": process.scope_key(scope()),
                                    "basis": legacy_basis,
                                    "results": sorted(report["results"], key=lambda row: row["id"])})
        changed = dict(basis(), source={"complete": False, "errors": ["Git unavailable"]})
        self.assertEqual(process.verification_key(scope(), report, changed), expected)
        completed = process.advance(session, "completed", verification=report, current_basis=legacy_basis,
                                    decision=decision(session, ["accept"], verification_key=expected))
        before = deepcopy(completed)
        self.assertEqual(process.describe(completed)["status"], "active")
        self.assertEqual(completed, before)
        self.assertEqual(completed["current_work"]["verification_key"], expected)

    def test_status_is_read_only_and_legacy_cli_refuses_marked_sessions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "session.json"
            path.write_text(json.dumps(process.new_session(scope())), encoding="utf-8")
            original = path.read_bytes()
            for command in (["status", "--json"], ["status", "--json", "--check"],
                            ["sync-session"], ["session", "--gate", "impl", "--status", "done"],
                            ["gate-start", "impl"], ["export"]):
                result = subprocess.run([sys.executable, str(ROOT / "vulcan.py"), *command], cwd=root,
                                        capture_output=True, text=True, encoding="utf-8", timeout=30)
                expected = 0 if command == ["status", "--json"] else 1 if "--check" in command else 2
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(sorted(p.name for p in root.iterdir()), ["session.json"])
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as error:
                vulcan.save_session({"profile": "product", "current_gate": "gate2"}, str(root))
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(path.read_bytes(), original)
            marked = json.loads(original)
            marked["process_model"] = "future-model"
            path.write_text(json.dumps(marked), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "vulcan.py"), "status", "--json"], cwd=root,
                                    capture_output=True, text=True, encoding="utf-8", timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "unsupported_or_invalid")


if __name__ == "__main__":
    unittest.main()
