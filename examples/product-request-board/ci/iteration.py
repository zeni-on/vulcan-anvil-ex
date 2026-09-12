"""Disposable two-scope Product rehearsal, not a project migration or release tool."""

from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SAMPLE = Path(__file__).resolve().parents[1]
FRAMEWORK = SAMPLE.parents[1]
sys.path.insert(0, str(FRAMEWORK))
from vulcan_core import product_process as process, product_readiness as readiness, product_session as store

OUTPUT = SAMPLE / "ci-artifacts" / "iteration"


class IterationRehearsal(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="request-board-iteration-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.events = []
        self.addCleanup(self.export)
        for name in ("app.py", "requirements.txt"):
            shutil.copy2(SAMPLE / name, self.root / name)
        shutil.copytree(SAMPLE / "static", self.root / "static")
        (self.root / "docs").mkdir()
        for name in ("contracts.md", "test-plan.md", "status-filter.md", "status-filter-tests.md"):
            shutil.copy2(SAMPLE / "docs" / name, self.root / "docs" / name)
        (self.root / "ci").mkdir()
        shutil.copy2(SAMPLE / "ci/iteration_assertions.py", self.root / "ci/iteration_assertions.py")
        self.write("environment.json", {"python": sys.version, "database": "disposable SQLite", "interface": "FastAPI TestClient"})
        self.write("vulcan.config.json", {"workflow": {"main_branch": "main", "integration_branch": "dev"}})
        (self.root / ".gitignore").write_text("runtime/\n__pycache__/\n.vulcan/\n", encoding="utf-8")
        (self.root / "evidence").mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Iteration fixture")
        self.git("config", "user.email", "iteration@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.commit()
        self.git("switch", "-c", "dev")

    def export(self):
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "commands.json").write_text(json.dumps(self.events, indent=2, ensure_ascii=False), encoding="utf-8")
        for source, target in ((self.root / "evidence", OUTPUT / "evidence"),):
            if source.exists():
                shutil.copytree(source, target, dirs_exist_ok=True)
        if (self.root / "session.json").exists():
            shutil.copy2(self.root / "session.json", OUTPUT / "session.json")

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value, indent=2), encoding="utf-8")

    def session(self):
        return json.loads((self.root / "session.json").read_bytes())

    def ref(self, path):
        return readiness.local_reference(self.root, path, markdown=".md" in path)

    def cli(self, args, request=None, code=0, label=None):
        result = subprocess.run([sys.executable, "-B", str(FRAMEWORK / "vulcan.py"), *args], cwd=self.root,
            input=json.dumps(request) if request is not None else None, capture_output=True, text=True,
            encoding="utf-8", timeout=60, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.events.append({"label": label or " ".join(args), "argv": args, "expected_exit": code,
                            "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True,
                              encoding="utf-8", timeout=15, check=True).stdout.strip()

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "--allow-empty", "-m", "Disposable fixture checkpoint")

    def request(self, action, **values):
        path = self.root / "session.json"
        return {"process_model": process.MODEL, "action": action,
                "expected_session_revision": store.revision(path.read_bytes()) if path.exists() else None, **values}

    def send(self, request, *, apply=True, code=0, label=None):
        args = ["session", "--process-request", "-", "--json"]
        if apply:
            args.append("--apply")
        return json.loads(self.cli(args, request, code, label))

    def deny(self, request, *, apply=True, code=1, message=None, label=None):
        before = (self.root / "session.json").read_bytes()
        result = self.send(request, apply=apply, code=code, label=label)
        self.assertEqual((self.root / "session.json").read_bytes(), before)
        self.assertIn(result["status"], {"blocked", "invalid", "conflict"})
        if message:
            self.assertIn(message, json.dumps(result))
        return result

    def decision(self, actions, **values):
        # This is deliberately synthetic authority in a temporary test, not user approval.
        return {"scope_key": self.session()["current_work"]["scope_key"], "actor": "synthetic-owner",
                "authority": "user", "actions": actions,
                "evidence": {"ref": "fixture:owner-decision", "revision": "fixture:1"}, **values}

    def execution_denied(self, request, reason, label):
        result = self.deny(request, label=label)
        checked = result["checks"]
        self.assertEqual(checked["execution"], "missing_stale_or_failed")
        self.assertNotIn("verification_key", checked)
        self.assertIn(("invalid_execution_basis", reason),
                      [(issue["code"], issue["message"]) for issue in checked["issues"]])

    def scope(self, extended=False):
        return {"work": {"ref": "sample:request-board", "revision": "filter:2" if extended else "resubmit:1"},
                "related_ids": ["SCN-001", "REQ-001", "REQ-002", "SEC-001", "SEC-002"] +
                    (["SCN-002", "REQ-003", "AC-004", "AC-005", "AC-006"] if extended else []),
                "contracts": [self.ref("docs/contracts.md")] + ([self.ref("docs/status-filter.md")] if extended else []),
                "tests": [self.ref("docs/test-plan.md")] + ([self.ref("docs/status-filter-tests.md")] if extended else []),
                "required_checks": ["REG-006", "SEC-REG-006"] if extended else ["REG-001", "SEC-REG-001"]}

    def enter_acceptance(self, decision=None):
        self.send(self.request("advance", target="impl", decision=decision or self.decision(["implement", "verify", "fix"])))
        self.send(self.request("advance", target="acceptance", basis={"environment": self.ref("environment.json")}))

    def observe(self, stage):
        self.cli(["execute", "--verify", "--source", "app.py", "--source", "ci/iteration_assertions.py",
                  "--source", "requirements.txt", "--source", "environment.json",
                  "--evidence", f"evidence/{stage}.json", "--", sys.executable, "-B", "ci/iteration_assertions.py", stage])
        handoff = json.loads(self.cli(["execute", "--dry-run", "--json"]))
        request = handoff["return_request"]
        request["verification"]["results"] = [{"id": identifier, "status": "Pass", "evidence": f"evidence/{stage}.json"}
            for identifier in self.session()["current_work"]["scope"]["required_checks"]]
        preview = self.deny(request, apply=False, message="missing scoped accept decision", label=stage + ": executed is not accepted")
        self.assertEqual(preview["checks"]["execution"], "verified_observations")
        return preview

    def accept(self, preview):
        prepared = deepcopy(preview["prepared_request"])
        prepared["decision"] = self.decision(["accept"], verification_key=preview["checks"]["verification_key"])
        result = self.send(prepared)
        self.assertFalse(result["release_authorized"])
        return self.session()

    def release_preview(self, expected):
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        refs = self.git("show-ref")
        output = self.cli(["release-pr", "--dry-run"], code=0 if expected == "candidate" else 1)
        self.assertIn("Product release preview: " + expected, output)
        self.assertIn("release_authorized: False", output)
        self.assertEqual(self.git("show-ref"), refs)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_same_product_extension_retains_data_history_and_separate_release_authority(self):
        originals = {name: (self.root / "docs" / name).read_bytes() for name in ("contracts.md", "test-plan.md")}
        self.send(self.request("start", scope=self.scope()))
        self.enter_acceptance()
        first_preview = self.observe("baseline")
        accepted = self.accept(first_preview)
        first_evidence = (self.root / "evidence/baseline.json").read_bytes()
        first_data = (self.root / "runtime/baseline.json").read_bytes()
        self.commit()
        self.release_preview("candidate")

        reason = {"ref": "sample:status-filter-extension", "revision": "fixture:2"}
        self.send(self.request("open-work", target="planning", scope=self.scope(True), reason=reason))
        planning = self.session()
        self.assertEqual(planning["work_history"][-1]["work"], accepted["current_work"])
        self.assertEqual(planning["work_history"][:-1], accepted["work_history"])
        self.assertEqual(planning["current_work"]["decisions"], [])
        self.assertNotIn("verification", planning["current_work"])
        self.deny(self.request("advance", target="impl", decision=accepted["current_work"]["decisions"][0]),
                  code=2, message="scope", label="old scope cannot authorize extension")
        self.commit()
        self.release_preview("blocked")
        self.enter_acceptance()

        replay = self.request("advance", target="completed", verification=accepted["current_work"]["verification"])
        self.execution_denied(replay, "verification belongs to another scope",
                              "prior acceptance evidence cannot complete the extension")
        expanded = deepcopy(replay)
        expanded["verification"]["scope_key"] = self.session()["current_work"]["scope_key"]
        self.execution_denied(expanded, "results must cover each required check exactly once",
                              "rebinding only scope cannot replace missing extension checks")
        missing = self.request("advance", target="completed", verification={
            "scope_key": self.session()["current_work"]["scope_key"],
            "basis": {"environment": self.ref("environment.json")}, "results": []})
        self.execution_denied(missing, "verification results are missing", "new scope needs actual required observations")

        second_preview = self.observe("extension")
        prepared = deepcopy(second_preview["prepared_request"])
        prepared["decision"] = self.decision(["accept"], verification_key=first_preview["checks"]["verification_key"])
        denied = self.deny(prepared, label="old acceptance key cannot approve new observations")
        self.assertEqual(denied["checks"]["execution"], "verified_observations")
        self.assertEqual(denied["checks"]["transition"]["reasons"], ["missing scoped accept decision"])
        source = self.root / "docs/status-filter.md"
        saved = source.read_bytes()
        source.write_bytes(saved + b"\nChanged candidate condition.\n")
        prepared["decision"] = self.decision(["accept"], verification_key=second_preview["checks"]["verification_key"])
        denied = self.deny(prepared, label="changed contract after preview cannot be accepted")
        self.assertEqual(denied["checks"]["execution"], "verified_observations")
        self.assertTrue(any(issue["code"] == "invalid_reference" and issue["path"] == "docs/status-filter.md"
                            and "document revision changed" in issue["message"] for issue in denied["checks"]["issues"]))
        source.write_bytes(saved)
        final = self.accept(second_preview)
        archived = [item["work"] for item in final["work_history"] if item["current_gate"] == "completed"]
        self.assertEqual(archived, [accepted["current_work"]])
        self.assertEqual((self.root / "evidence/baseline.json").read_bytes(), first_evidence)
        self.assertEqual((self.root / "runtime/baseline.json").read_bytes(), first_data)
        for name, raw in originals.items():
            self.assertEqual((self.root / "docs" / name).read_bytes(), raw)
        self.assertTrue((self.root / "runtime/extension.json").exists())
        self.assertEqual(set(final["gate_status"]), set(process.STAGES))
        self.assertFalse((self.root / "docs/runs").exists())
        self.commit()
        self.release_preview("candidate")

        before = (self.root / "session.json").read_bytes()
        refs = self.git("show-ref")
        self.cli(["release-pr"], code=2, label="real publication not enabled by scope acceptance")
        self.assertEqual((self.root / "session.json").read_bytes(), before)
        self.assertEqual(self.git("show-ref"), refs)
        self.assertEqual(self.git("remote"), "")
        self.assertEqual(self.git("status", "--porcelain"), "")
        (self.root / "app.py").write_bytes((self.root / "app.py").read_bytes() + b"\n# pending change\n")
        self.release_preview("blocked")


if __name__ == "__main__":
    if OUTPUT.resolve() != SAMPLE.resolve() / "ci-artifacts" / "iteration":
        raise SystemExit("Refusing redirected artifact directory")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(IterationRehearsal)
    with (OUTPUT / "test.log").open("w", encoding="utf-8") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    print((OUTPUT / "test.log").read_text(encoding="utf-8"))
    summary = {"status": "passed" if result.wasSuccessful() else "failed", "tests": result.testsRun,
               "failures": len(result.failures), "errors": len(result.errors),
               "authority": "synthetic fixture only", "publication": "not performed"}
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    raise SystemExit(0 if result.wasSuccessful() else 1)
