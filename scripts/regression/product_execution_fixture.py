"""Disposable Git/CLI fixture for Product execution tests, never installed by init.

All authority below is synthetic test input, not user approval of a real product.
The prepare command creates a deliberately faulty application for native QA.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vulcan_core import product_process as process, product_readiness as readiness, product_session


BROKEN_APP = '''from copy import deepcopy


def resubmit(request, actor, content):
    if actor != request["owner"]:
        raise PermissionError("Only the owner may resubmit")
    if request["status"] != "rejected":
        raise ValueError("Only rejected requests may be resubmitted")
    result = deepcopy(request)
    result["history"].append({"content": content, "reason": request["reason"]})
    result.update(content=content, status="submitted", reason=None)
    return result
'''
FIXED_APP = BROKEN_APP.replace('{"content": content, "reason":', '{"content": request["content"], "reason":')
TESTS = '''from copy import deepcopy
import unittest
from app import resubmit


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.request = {"id": 7, "owner": "alice", "content": "original",
                        "status": "rejected", "reason": "missing detail", "history": []}

    def test_reg_001_resubmission_preserves_rejected_snapshot(self):
        before = deepcopy(self.request)
        result = resubmit(self.request, "alice", "amended")
        self.assertEqual(result["id"], 7)
        self.assertEqual(result["content"], "amended")
        self.assertEqual(result["status"], "submitted")
        self.assertEqual(result["history"], [{"content": "original", "reason": "missing detail"}])
        self.assertEqual(self.request, before)

    def test_sec_reg_001_other_user_is_denied_without_mutation(self):
        before = deepcopy(self.request)
        with self.assertRaises(PermissionError):
            resubmit(self.request, "bob", "amended")
        self.assertEqual(self.request, before)

    def test_reg_002_submitted_request_cannot_be_resubmitted(self):
        self.request["status"] = "submitted"
        with self.assertRaises(ValueError):
            resubmit(self.request, "alice", "amended")
'''
CONTRACT = '''# Request resubmission
| ID | Definition |
| --- | --- |
| SCN-001 | Owner amends and resubmits the same rejected request. |
| REQ-001 | Preserve the rejected content and rejection reason in history. |
| REQ-002 | Resubmission is allowed only from the rejected state. |

## Security
| ID | Definition |
| --- | --- |
| SEC-001 | Reject another actor without modifying the request. |
'''
PLAN = '''# Request verification
| REG ID | Method | Expected | Status |
| --- | --- | --- | --- |
| REG-001 | unittest test_reg_001 | Same ID, amended content, original snapshot and reason preserved | Planned |
| REG-002 | unittest test_reg_002 | Submitted request resubmission raises ValueError | Planned |
| SEC-REG-001 | unittest test_sec_reg_001 | Another actor raises PermissionError with no mutation | Planned |
'''


class ExecutionProject:
    sources = ["app.py", "tests", "requirements.txt", "environment.json"]
    command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]

    def __init__(self, root):
        self.root = Path(root).resolve()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def git(self, *args, check=True):
        if args[0] == "init":
            if (self.root / ".git").exists():
                raise ValueError("fixture init cannot reuse Git metadata")
        else:
            self.require_repository()
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, encoding="utf-8", check=check, timeout=30, env=self.environment())

    @staticmethod
    def environment():
        # A disposable regression must not inherit another checkout's Git
        # context, signing settings, hooks, or environment-injected config.
        env = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0")
        return env

    def require_repository(self):
        metadata = self.root / ".git"
        if not metadata.is_dir() or metadata.resolve() != self.root / ".git":
            raise ValueError("fixture requires its own Git directory")
        result = subprocess.run(["git", "rev-parse", "--show-toplevel", "--absolute-git-dir"],
                                cwd=self.root, capture_output=True, text=True, encoding="utf-8",
                                timeout=30, env=self.environment())
        paths = result.stdout.splitlines()
        if (result.returncode or len(paths) != 2 or Path(paths[0]).resolve() != self.root
                or Path(paths[1]).resolve() != metadata.resolve()):
            raise ValueError("fixture Git metadata/workspace must remain inside its own root")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "--allow-empty", "-m", message)

    def cli(self, *args, request=None):
        self.require_repository()
        return subprocess.run([sys.executable, "-B", str(ROOT / "vulcan.py"), *args], cwd=self.root,
                              input=json.dumps(request) if request is not None else None,
                              capture_output=True, text=True, encoding="utf-8", timeout=60, env=self.environment())

    def state(self):
        return json.loads((self.root / "session.json").read_bytes())

    def ref(self, name):
        return readiness.local_reference(self.root, name, markdown=name.endswith(".md"))

    def basis(self):
        return {"environment": self.ref("environment.json")}

    def request(self, action, **values):
        path = self.root / "session.json"
        return {"process_model": process.MODEL, "action": action,
                "expected_session_revision": product_session.revision(path.read_bytes()) if path.exists() else None,
                **values}

    def apply(self, request):
        result = self.cli("session", "--process-request", "-", "--json", "--apply", request=request)
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(result.stdout)

    def decision(self, actions, **values):
        return {"scope_key": self.state()["current_work"]["scope_key"], "actions": actions,
                "actor": "synthetic-test-user", "authority": "user",
                "evidence": {"ref": "fixture:permission", "revision": "snapshot:1"}, **values}

    def create(self):
        if self.root.exists() and any(self.root.iterdir()):
            raise ValueError("fixture requires a new or empty directory")
        self.root.mkdir(parents=True, exist_ok=True)
        self.write(".gitignore", "__pycache__/\n*.pyc\n")
        self.write("docs/contracts.md", CONTRACT)
        self.write("docs/tests.md", PLAN)
        self.write("app.py", BROKEN_APP)
        self.write("tests/test_requests.py", TESTS)
        self.write("requirements.txt", "# Python standard library only\n")
        self.write("evidence/.gitkeep", "")
        self.write("environment.json", json.dumps({"python": sys.version, "external_services": []}))
        self.write("vulcan.config.json", json.dumps({"workflow": {"main_branch": "main", "integration_branch": "dev-test"}}))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Synthetic Regression")
        self.git("config", "user.email", "regression@example.invalid")
        self.git("config", "core.autocrlf", "false")
        scope = {"work": {"ref": "fixture:resubmission", "revision": "snapshot:1"},
                 "related_ids": ["SCN-001", "REQ-001", "REQ-002", "SEC-001"],
                 "contracts": [self.ref("docs/contracts.md")], "tests": [self.ref("docs/tests.md")],
                 "required_checks": ["REG-001", "REG-002", "SEC-REG-001"]}
        self.apply(self.request("start", scope=scope))
        self.apply(self.request("advance", target="impl", decision=self.decision(["implement", "verify", "fix"])))
        self.commit("fixture: approved implementation basis (synthetic)")
        self.git("switch", "-c", "dev-test")
        self.apply(self.request("advance", target="acceptance", basis=self.basis()))
        self.commit("fixture: acceptance handoff (synthetic)")

    def verification_args(self, name):
        return ["execute", "--verify", "--evidence", "evidence/" + name + ".json", "--", *self.command]

    def verify(self, name):
        result = self.cli(*self.verification_args(name))
        self.write("evidence/" + name + ".log", result.stdout + result.stderr)
        return result

    def results(self, name, status="Pass"):
        report = json.loads((self.root / "evidence" / (name + ".json")).read_bytes())
        return {"scope_key": self.state()["current_work"]["scope_key"],
                "basis": self.basis(),
                "results": [{"id": identifier, "status": status, "command": report["command"]["argv"],
                             "evidence": self.ref("evidence/" + name + ".json")}
                            for identifier in self.state()["current_work"]["scope"]["required_checks"]]}

    def completion(self, verification, **values):
        key = process.verification_key(self.state()["current_work"]["scope"], verification, verification["basis"])
        return self.request("advance", target="completed", verification=verification,
                            decision=self.decision(["accept"], verification_key=key), **values)

    def fix(self):
        if (self.root / "app.py").read_text(encoding="utf-8") != BROKEN_APP:
            raise ValueError("only the known deliberate fixture defect may be fixed")
        self.apply(self.request("advance", target="impl", reason={"ref": "fixture:qa-failure", "revision": "snapshot:1"}))
        self.write("app.py", FIXED_APP)
        self.apply(self.request("advance", target="acceptance", basis=self.basis()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare"])
    parser.add_argument("directory")
    args = parser.parse_args()
    project = ExecutionProject(args.directory)
    project.create()
    print(json.dumps({"project": str(project.root), "stage": project.state()["current_gate"],
                      "command": [sys.executable, "-B", str(ROOT / "vulcan.py"), *project.verification_args("native-failure")],
                      "notice": "Deliberately broken synthetic fixture. No external services or release."}, indent=2))
