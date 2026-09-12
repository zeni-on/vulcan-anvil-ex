"""Pure stdlib policy tests; no Product runtime dependencies are needed."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "request_board_ci_policy", ROOT / "examples/product-request-board/ci/policy.py"
)
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


def steps(state="success"):
    result = {name: {"outcome": state, "conclusion": state}
              for name in policy.MANDATORY_STEPS}
    result["scope"] = {"outcome": "success", "conclusion": "success"}
    return result


class PathPolicyTests(unittest.TestCase):
    def test_document_only(self):
        for paths in (["README.md"], ["docs/a.md", "docs\\b.md"],
                      ["examples/product-request-board/docs/verification.md"]):
            with self.subTest(paths=paths):
                self.assertFalse(policy.requires_tests(paths))

    def test_conservative_paths(self):
        for paths in ([], [""], [None], None, "README.md", ["a.py"],
                      ["a.md", "b.json"], ["README.MD"], ["../a.md"],
                      ["/a.md"], ["C:\\a.md"], ["a//b.md"], ["./a.md"],
                      ["a\n.md"], [".github/README.md"],
                      [".github\\workflows\\notes.md"],
                      ["examples/product-request-board/docs/contracts.md"],
                      ["examples/product-request-board/docs/new-rule.md"],
                      ["examples\\product-request-board\\docs\\test-plan.md"]):
            with self.subTest(paths=paths):
                self.assertTrue(policy.requires_tests(paths))


class GatePolicyTests(unittest.TestCase):
    def test_complete(self):
        self.assertEqual(policy.assess_steps(steps(), True),
                         {"status": "success", "issues": []})
        self.assertEqual(policy.assess_steps(steps("skipped"), False),
                         {"status": "not_applicable", "issues": []})

    def test_every_mandatory_step_matrix(self):
        for required in (True, False):
            for name in policy.MANDATORY_STEPS:
                for state in (None, "skipped", "cancelled", "failure", "unknown", "success"):
                    with self.subTest(required=required, name=name, state=state):
                        data = steps("success" if required else "skipped")
                        if state is None:
                            del data[name]
                        else:
                            data[name] = {"outcome": state, "conclusion": state}
                        expected = "incomplete"
                        if state == ("success" if required else "skipped"):
                            expected = "success" if required else "not_applicable"
                        elif state == "failure":
                            expected = ("environment_blocked" if name in policy.ENVIRONMENT_STEPS
                                        else "failed")
                        result = policy.assess_steps(data, required)
                        self.assertEqual(result["status"], expected)
                        self.assertEqual(bool(result["issues"]), expected not in ("success", "not_applicable"))

    def test_continue_on_error(self):
        for name in policy.MANDATORY_STEPS:
            data = steps()
            data[name] = {"outcome": "failure", "conclusion": "success"}
            self.assertEqual(policy.assess_steps(data, True)["status"],
                             "environment_blocked" if name in policy.ENVIRONMENT_STEPS else "failed")

    def test_scope_must_succeed(self):
        for required in (True, False):
            for state in (None, "failure", "skipped", "cancelled", "unknown"):
                data = steps("success" if required else "skipped")
                data["scope"] = {"outcome": state, "conclusion": state}
                self.assertEqual(policy.assess_steps(data, required)["status"], "incomplete")
            del data["scope"]
            self.assertEqual(policy.assess_steps(data, required)["status"], "incomplete")

    def test_invalid_objects_and_mismatched_fields(self):
        for invalid in (None, [], "success", {}, {"outcome": "success"},
                        {"conclusion": "success"},
                        {"outcome": "success", "conclusion": "skipped"}):
            data = steps()
            data["api"] = invalid
            self.assertEqual(policy.assess_steps(data, True)["status"], "incomplete")
        self.assertEqual(policy.assess_steps([], True)["status"], "incomplete")
        self.assertEqual(policy.assess_steps(steps(), "false")["status"], "incomplete")

    def test_failure_precedence(self):
        data = steps()
        del data["probe"]
        data["api"] = {"outcome": "failure", "conclusion": "success"}
        self.assertEqual(policy.assess_steps(data, True)["status"], "failed")
        data["install"] = {"outcome": "failure", "conclusion": "failure"}
        self.assertEqual(policy.assess_steps(data, True)["status"], "environment_blocked")


class CliPolicyTests(unittest.TestCase):
    def invoke(self, mode, env):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, env, clear=True), redirect_stdout(stdout), redirect_stderr(stderr):
            code = policy.main([mode])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_scope_fallback_does_not_invoke_git(self):
        for event, base in (("workflow_dispatch", "a" * 40), ("push", ""),
                            ("pull_request", "--help"), ("push", "g" * 40),
                            ("push", "a" * 39), ("push", "a" * 40 + "\n")):
            with patch.object(policy.subprocess, "run") as run:
                code, out, _ = self.invoke("--scope", {"EVENT_NAME": event, "BASE_SHA": base})
                self.assertEqual(code, 0)
                self.assertTrue(json.loads(out)["required"])
                run.assert_not_called()

    def test_scope_diff_boundaries_and_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "output"
            for event in ("push", "pull_request"):
                with patch.object(policy.subprocess, "run") as run:
                    run.return_value.stdout = b"docs/space name.md\0README.md\0"
                    code, out, _ = self.invoke("--scope", {
                        "EVENT_NAME": event, "BASE_SHA": "A" * 40, "GITHUB_OUTPUT": str(output)})
                    self.assertEqual(code, 0)
                    self.assertFalse(json.loads(out)["required"])
                    run.assert_called_once_with(
                        ["git", "diff", "--no-renames", "--name-only", "-z", "A" * 40, "HEAD"],
                        cwd=ROOT, check=True, capture_output=True)
            self.assertEqual(output.read_text(), "required=false\nrequired=false\n")

    def test_scope_empty_or_bad_diff(self):
        for raw, expected in ((b"", 0), (b"README.md", 1), (b"\xff\0", 1)):
            with patch.object(policy.subprocess, "run") as run:
                run.return_value.stdout = raw
                code, out, _ = self.invoke("--scope", {"EVENT_NAME": "push", "BASE_SHA": "a" * 40})
                self.assertEqual(code, expected)
                if code == 0:
                    self.assertTrue(json.loads(out)["required"])
        with patch.object(policy.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "git")):
            self.assertEqual(self.invoke("--scope", {"EVENT_NAME": "push", "BASE_SHA": "a" * 40})[0], 1)

    def test_real_git_rename_to_markdown_cannot_hide_deleted_code_or_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
            git("init", "-q")
            git("config", "user.name", "CI fixture")
            git("config", "user.email", "ci-fixture@example.invalid")
            (root / "app.py").write_text("print('required source')\n", encoding="utf-8")
            contract = root / "examples/product-request-board/docs/contracts.md"
            contract.parent.mkdir(parents=True)
            contract.write_text("# Required contract\n", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "fixture baseline")
            base = git("rev-parse", "HEAD")
            (root / "docs").mkdir()
            (root / "app.py").rename(root / "docs/app.md")
            contract.rename(root / "docs/notes.md")
            git("add", "-A")
            git("commit", "-qm", "fixture renamed as documentation")
            # Real Git sees renames, but the policy must also inspect deleted source paths.
            self.assertTrue(all(p.endswith(".md") for p in git("diff", "--name-only", base, "HEAD").splitlines()))
            with patch.object(policy, "REPOSITORY_ROOT", root):
                code, output, error = self.invoke("--scope", {**os.environ, "EVENT_NAME": "pull_request", "BASE_SHA": base})
            self.assertEqual(code, 0, error)
            self.assertTrue(json.loads(output)["required"])

    def test_gate_cli_and_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            summary = Path(folder) / "summary"
            for required, state, expected in (("true", "success", 0), ("false", "skipped", 0),
                                              ("true", "cancelled", 1), ("true", "failure", 1)):
                code, out, _ = self.invoke("--gate", {
                    "REQUIRED": required, "STEPS_JSON": json.dumps(steps(state)),
                    "GITHUB_STEP_SUMMARY": str(summary)})
                self.assertEqual(code, expected)
                self.assertIn(json.loads(out)["status"], summary.read_text())

    def test_gate_load_failures(self):
        for env in ({}, {"REQUIRED": "True", "STEPS_JSON": "{}"},
                    {"REQUIRED": " true", "STEPS_JSON": "{}"},
                    {"REQUIRED": "1", "STEPS_JSON": "{}"},
                    {"REQUIRED": "true"}, {"REQUIRED": "true", "STEPS_JSON": "[]"},
                    {"REQUIRED": "false", "STEPS_JSON": "__import__('os')"}):
            with self.subTest(env=env):
                code, _, error = self.invoke("--gate", env)
                self.assertNotEqual(code, 0)
                self.assertIn("CI policy error", error)


if __name__ == "__main__":
    unittest.main()
