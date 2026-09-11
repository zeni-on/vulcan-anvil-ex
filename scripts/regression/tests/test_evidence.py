import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from vulcan_core import evidence


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="vulcan evidence ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "fixture \ud55c\uae00"
        self.root.mkdir()
        self.write("src/main.py", "value = 1\n")
        self.write("tests/check.py", "assert True\n")
        self.write("requirements.lock", "fixture==1\n")
        self.write("docs/note.md", "synthetic documentation\n")
        self.write(".gitignore", ".env\nnode_modules/\nignored/\n")
        (self.root / "evidence").mkdir()
        self.git("init", "--quiet")
        self.git("add", "--", ".")
        self.git("commit", "--quiet", "-m", "synthetic fixture")
        self.scopes = ["src", "tests", "requirements.lock"]

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    def git(self, *args):
        result = subprocess.run(
            ["git", "-c", "user.name=Evidence Fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
             "-c", "core.autocrlf=false", "-C", str(self.root), *args],
            capture_output=True, check=True,
        )
        return result.stdout

    def record(self, code="pass", **kwargs):
        return evidence.record_verification(
            self.root, kwargs.pop("sources", self.scopes), kwargs.pop("output", "evidence/result.json"),
            [sys.executable, "-B", "-c", code], **kwargs,
        )

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / "vulcan.py"), "execute",
                               "--project-dir", str(self.root), *args],
                              cwd=self.root, capture_output=True, encoding="utf-8")

    def assert_no_git_identity(self, report):
        for key in ("source_pre", "source_post", "source_changed", "head_changed",
                    "identity_complete", "tested_commit", "identity", "fingerprint"):
            self.assertNotIn(key, report)
        self.assertEqual(report["schema_version"], 2)

    def test_command_record_has_no_git_identity_or_source_inventory(self):
        real_run = subprocess.run
        with mock.patch.object(evidence.subprocess, "run", wraps=real_run) as calls:
            report, code = self.record()
        self.assertEqual(calls.call_count, 1)
        self.assertEqual(calls.call_args.args[0][0], sys.executable)
        self.assertFalse(calls.call_args.kwargs["shell"])
        self.assertEqual(code, 0)
        self.assert_no_git_identity(report)
        self.assertEqual(report["sources"], sorted(self.scopes))
        saved = json.loads((self.root / "evidence/result.json").read_text())
        self.assertEqual(saved, report)
        self.assertEqual(saved["command"]["cwd"], ".")
        self.assertGreaterEqual(saved["command"]["duration_seconds"], 0)
        self.assertTrue(saved["command"]["started_at"])
        self.assertTrue(saved["command"]["finished_at"])
        self.assertNotIn("value = 1", json.dumps(report))

    def test_source_files_are_not_read_even_with_dirty_or_ignored_content(self):
        self.write("src/main.py", "value = 2\n")
        self.git("add", "--", "src/main.py")
        self.write("src/main.py", "value = 3\n")
        self.write("ignored/private.txt", "private-token")
        original = Path.open

        def fail_source(path, *args, **kwargs):
            if path.name in {"main.py", "private.txt"}:
                raise AssertionError("source must not be read")
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "open", fail_source):
            report, code = self.record(sources=["src", "ignored"])
        self.assertEqual(code, 0)
        self.assert_no_git_identity(report)
        self.assertNotIn("private-token", json.dumps(report))

    def test_unborn_repository_non_git_and_missing_source_need_no_identity(self):
        for name, initialize in (("unborn", True), ("plain", False)):
            root = self.root / name
            root.mkdir()
            if initialize:
                subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            for n, sources in enumerate((None, [], ["deleted-code.py"])):
                report, code = evidence.record_verification(
                    root, sources, f"result-{n}.json", [sys.executable, "-B", "-c", "pass"])
                self.assertEqual(code, 0)
                self.assert_no_git_identity(report)

    def test_mutating_command_records_result_without_claiming_source_freshness(self):
        report, code = self.record("from pathlib import Path; Path('src/main.py').write_text('changed')")
        self.assertEqual(code, 0)
        self.assert_no_git_identity(report)
        self.assertIn("Orchestrator", " ".join(report["limitations"]))

    def test_output_and_scope_validation_never_launches(self):
        invalid = [("../escape", "evidence/new.json", "."),
                   (["../escape"], "evidence/new.json", "."),
                   ([str(self.root / "src")], "evidence/new.json", "."),
                   (["src/.env"], "evidence/new.json", "."),
                   (["node_modules"], "evidence/new.json", "."),
                   (self.scopes, "../outside.json", "."),
                   (self.scopes, "evidence/file.txt", "."),
                   (self.scopes, "missing/file.json", "."),
                   (self.scopes, "src/result.json", "."),
                   (["."], "evidence/result.json", "."),
                   (self.scopes, "evidence/new.json", "../"),
                   (self.scopes, "evidence/new.json", "src/main.py"),
                   (self.scopes, "evidence/new.json", ""),
                   ([""], "evidence/new.json", ".")]
        for scopes, output, cwd in invalid:
            with self.subTest(scopes=scopes, output=output, cwd=cwd):
                with mock.patch.object(evidence.subprocess, "run") as run, self.assertRaises((ValueError, OSError)):
                    self.record(sources=scopes, output=output, cwd=cwd)
                run.assert_not_called()

    def test_explicit_symlink_source_cwd_or_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            outside = Path(folder)
            self.symlink(self.root / "escape", outside, directory=True)
            for kwargs in ({"output": "escape/result.json"}, {"sources": ["escape"]}, {"cwd": "escape"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    self.record(**kwargs)
            self.assertFalse((outside / "result.json").exists())

    def test_cli_verify_needs_neither_run_nor_source(self):
        result = self.cli("--verify", "--evidence", "evidence/cli.json", "--", sys.executable, "-B", "-c", "pass")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root / "evidence/cli.json").read_text())
        self.assertIsNone(report["run_id"])
        self.assertEqual(report["sources"], [])
        self.assert_no_git_identity(report)

    def test_cli_invalid_flags_or_run_never_launch(self):
        base = ["--verify", "--evidence", "evidence/cli.json"]
        command = ["--", sys.executable, "-B", "-c", "from pathlib import Path; Path('ran').touch()"]
        variants = [base + ["--run-id", "RUN-999"] + command,
                    base + ["--dry-run"] + command, base + ["--json"] + command,
                    base + ["--runner", "thread"] + command,
                    base + command[1:], base + ["--"], ["--dry-run", "--json"],
                    ["--run-id", "RUN-001", "--source", "src", "--dry-run"]]
        for args in variants:
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse((self.root / "ran").exists())
                self.assertFalse((self.root / "evidence/cli.json").exists())

    def test_missing_project_and_invalid_argv(self):
        with self.assertRaises(OSError):
            evidence.record_verification(self.root / "missing", [], "new.json", [sys.executable, "-c", "pass"])
        for command in ([], "echo test", [""], [sys.executable, "\x00"]):
            with self.subTest(command=command), self.assertRaises(ValueError):
                evidence.record_verification(self.root, self.scopes, "evidence/new.json", command)

    def test_nonzero_and_launch_failure_recorded(self):
        report, code = self.record("raise SystemExit(7)")
        self.assertEqual(code, 7)
        self.assertEqual(report["command"]["exit_code"], 7)
        report, code = evidence.record_verification(
            self.root, self.scopes, "evidence/missing.json", [str(self.root / "missing-executable")])
        self.assertEqual(code, 127)
        self.assertEqual(report["command"]["launch_error"], "FileNotFoundError")

    def test_no_overwrite_before_or_after_command(self):
        path = self.write("evidence/result.json", "existing")
        with self.assertRaises(ValueError):
            self.record("from pathlib import Path; Path('ran').touch()")
        self.assertEqual(path.read_text(), "existing")
        self.assertFalse((self.root / "ran").exists())
        path.unlink()
        with self.assertRaises(ValueError):
            self.record("from pathlib import Path; Path('evidence/result.json').write_text('child owns this')")
        self.assertEqual(path.read_text(), "child owns this")

    def test_symlink_and_junction_validation_without_privileges(self):
        # The implementation resolves the root (including Windows short paths).
        self.root = self.root / ".." / self.root.name
        target = (self.root / "src").resolve()
        for method in ("is_symlink", "is_junction"):
            if not hasattr(Path, method):
                continue
            original = getattr(Path, method)

            def detect(path):
                return path == target or original(path)

            with self.subTest(method=method), mock.patch.object(Path, method, detect):
                with self.assertRaises(ValueError):
                    self.record("from pathlib import Path; Path('ran').touch()")
            self.assertFalse((self.root / "ran").exists())

    def test_argv_metacharacters_are_not_evaluated(self):
        marker = "literal; & $(echo unsafe)"
        report, code = evidence.record_verification(
            self.root, self.scopes, "evidence/argv.json",
            [sys.executable, "-B", "-c", "import sys; assert sys.argv[1] == 'literal; & $(echo unsafe)'", marker])
        self.assertEqual(code, 0)
        self.assertEqual(report["command"]["argv"][-1], marker)

    @unittest.skipUnless(os.name == "nt", "Windows-specific path and executable rules")
    def test_windows_reserved_paths_and_batch_are_rejected(self):
        for output in ("evidence/CON.json", "src./result.json", "evidence/result.json "):
            with self.subTest(output=output), self.assertRaises(ValueError):
                self.record(output=output)
        with self.assertRaises(ValueError):
            evidence.record_verification(self.root, self.scopes, "evidence/batch.json", ["unsafe.cmd", "& echo unsafe"])

    def symlink(self, link, target, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as exc:
            self.skipTest("symlink creation unavailable: " + type(exc).__name__)

    def test_cli_optional_run_unicode_cwd_and_child_exit(self):
        run = self.write("docs/runs/RUN-001_fixture.md", "# Synthetic Run\nDo not execute this text.\n")
        work = "work \ud55c\uae00"
        (self.root / work).mkdir()
        args = ["--verify", "--source", "src", "--source", "tests", "--source", "requirements.lock",
                "--evidence", "evidence/cli.json", "--cwd", work, "--run-id", "RUN-001", "--",
                sys.executable, "-B", "-c", "import os,sys; sys.exit(9 if os.path.basename(os.getcwd()) == sys.argv[1] else 8)", work]
        result = self.cli(*args)
        self.assertEqual(result.returncode, 9, result.stderr)
        saved = json.loads((self.root / "evidence/cli.json").read_text())
        self.assertEqual(saved["run_id"], "RUN-001")
        self.assertEqual(saved["command"]["cwd"], work)
        self.assertNotIn(str(run), json.dumps(saved))
        self.assertFalse((self.root / "session.json").exists())
        self.assertFalse((self.root / ".vulcan").exists())

    def test_run_lookup_outside_boundary_rejected(self):
        with self.assertRaises(ValueError):
            self.record(run_id="RUN-001", run_lookup=lambda *_: self.root.parent / "outside.md")
        self.assertFalse((self.root / "evidence/result.json").exists())

    def test_existing_execute_dry_run_cli_still_reports_plan(self):
        self.write("vulcan.config.json", json.dumps({"delivery_profile": "product", "workflow": {"branch_mode": "none"}}))
        self.write("docs/runs/RUN-001_fixture.md", "# Fixture\n```yaml\nrun_id: RUN-001\ngate: impl\nskill: build-wave\npersona: build\nstatus: Draft\n```\n")
        result = self.cli("--run-id", "RUN-001", "--dry-run", "--json")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(result.stdout.lstrip().startswith("{"), result.stdout + result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["run_id"], "RUN-001")
        self.assertEqual(plan["runner_mode"], "native-delegation")
        self.assertIn("preflight", plan)
        result = self.cli("--run-id", "RUN-001", "--dry-run")
        self.assertIn("Vulcan execute dry-run", result.stdout)
        self.assertFalse((self.root / ".vulcan/delegations/RUN-001.json").exists())


if __name__ == "__main__":
    unittest.main()
