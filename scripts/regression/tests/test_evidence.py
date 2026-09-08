import hashlib
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

    def snapshot(self, sources=None):
        return evidence.capture_source_snapshot(self.root, sources or self.scopes)

    def files(self, snapshot):
        return {item["path"]: item for item in snapshot["files"]}

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / "vulcan.py"), "execute",
                               "--project-dir", str(self.root), *args],
                              cwd=self.root, capture_output=True, encoding="utf-8")

    def test_clean_commit_and_scoped_hashes(self):
        report, code = self.record()
        self.assertEqual(code, 0)
        head = self.git("rev-parse", "HEAD").decode().strip()
        self.assertEqual(report["tested_commit"], head)
        self.assertTrue(report["identity_complete"])
        self.assertFalse(report["source_changed"])
        files = self.files(report["source_pre"])
        self.assertEqual(set(files), {"src/main.py", "tests/check.py", "requirements.lock"})
        self.assertEqual(files["src/main.py"]["sha256"], hashlib.sha256(b"value = 1\n").hexdigest())
        self.assertEqual(files["src/main.py"]["status"], "  ")
        saved = json.loads((self.root / "evidence/result.json").read_text())
        self.assertEqual(saved, report)
        self.assertEqual(saved["command"]["cwd"], ".")
        self.assertGreaterEqual(saved["command"]["duration_seconds"], 0)
        self.assertNotIn("value = 1", json.dumps(report))
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_staged_and_unstaged_are_distinct(self):
        self.write("src/main.py", "value = 2\n")
        self.git("add", "--", "src/main.py")
        self.write("src/main.py", "value = 3\n")
        report, code = self.record()
        entry = self.files(report["source_pre"])["src/main.py"]
        self.assertEqual(code, 0)
        self.assertEqual(entry["status"], "MM")
        self.assertTrue(entry["staged"])
        self.assertTrue(entry["unstaged"])
        self.assertIsNone(report["tested_commit"])
        self.assertTrue(report["identity_complete"])

    def test_replaced_commit_cannot_claim_original_source_identity(self):
        original = self.git("rev-parse", "HEAD").decode().strip()
        self.write("src/main.py", "value = 2\n")
        self.git("add", "--", "src/main.py")
        self.git("commit", "--quiet", "-m", "replacement fixture")
        replacement = self.git("rev-parse", "HEAD").decode().strip()
        with mock.patch.dict(os.environ):
            os.environ.pop("GIT_NO_REPLACE_OBJECTS", None)
            self.git("replace", original, replacement)
            self.git("checkout", "--quiet", "--detach", original)
            self.assertEqual(self.git("show", "HEAD:src/main.py"), b"value = 2\n")
            self.assertEqual(self.git("status", "--porcelain", "--", "src/main.py"), b"")
            report, code = self.record("import runpy; assert runpy.run_path('src/main.py')['value'] == 2")
        self.assertEqual(code, 0)
        self.assertIsNone(report["tested_commit"])
        self.assertNotEqual(report["identity"], "scoped_clean_commit")
        self.assertTrue(report["identity_complete"])
        for snapshot in (report["source_pre"], report["source_post"]):
            self.assertEqual(snapshot["head"], original)
            self.assertTrue(snapshot["scoped_dirty"])
            entry = self.files(snapshot)["src/main.py"]
            self.assertEqual(entry["status"], "M ")
            self.assertEqual(entry["sha256"], hashlib.sha256(b"value = 2\n").hexdigest())

    def test_staged_only_and_untracked_new(self):
        self.write("src/main.py", "value = 2\n")
        self.git("add", "--", "src/main.py")
        self.write("src/new file.py", "new = True\n")
        report, _ = self.record()
        entries = self.files(report["source_pre"])
        self.assertEqual(entries["src/main.py"]["status"], "M ")
        self.assertEqual(entries["src/new file.py"]["status"], "??")
        self.assertTrue(entries["src/new file.py"]["new"])
        self.assertIsNotNone(entries["src/new file.py"]["sha256"])
        self.assertIsNone(report["tested_commit"])

    def test_unstaged_and_staged_deleted_exact_source(self):
        (self.root / "src/main.py").unlink()
        for staged in (False, True):
            with self.subTest(staged=staged):
                if staged:
                    self.git("add", "-u", "--", "src/main.py")
                report, _ = self.record(sources=["src/main.py"], output=f"evidence/delete-{staged}.json")
                entry = report["source_pre"]["files"][0]
                self.assertTrue(entry["deleted"])
                self.assertIsNone(entry["sha256"])
                self.assertFalse(entry["exists"])
                self.assertEqual(entry["status"], "D " if staged else " D")
                self.assertIsNone(report["tested_commit"])

    def test_doc_only_changes_outside_scope_do_not_invalidate_identity(self):
        self.write("docs/note.md", "changed before command\n")
        report, _ = self.record("from pathlib import Path; Path('docs/note.md').write_text('changed again')")
        self.assertIsNotNone(report["tested_commit"])
        self.assertFalse(report["source_changed"])

    def test_mutation_during_command_is_observed(self):
        report, code = self.record("from pathlib import Path; Path('src/main.py').write_text('changed')")
        self.assertEqual(code, 0)
        self.assertTrue(report["source_changed"])
        self.assertIsNone(report["tested_commit"])
        self.assertEqual(report["identity"], "changed")

    def test_new_and_deleted_files_during_command(self):
        report, _ = self.record("from pathlib import Path; Path('src/main.py').unlink(); Path('src/new.py').write_text('new')")
        entries = self.files(report["source_post"])
        self.assertTrue(entries["src/main.py"]["deleted"])
        self.assertTrue(entries["src/new.py"]["new"])
        self.assertTrue(report["source_changed"])

    def test_nonzero_and_launch_failure_recorded(self):
        report, code = self.record("raise SystemExit(7)")
        self.assertEqual(code, 7)
        self.assertEqual(report["command"]["exit_code"], 7)
        self.assertIsNotNone(report["tested_commit"])
        report, code = evidence.record_verification(
            self.root, self.scopes, "evidence/missing.json", [str(self.root / "missing-executable")])
        self.assertEqual(code, 127)
        self.assertEqual(report["command"]["launch_error"], "FileNotFoundError")

    def test_output_and_scope_validation_never_runs_or_writes(self):
        invalid = [([], "evidence/new.json", "."), (["missing"], "evidence/new.json", "."),
                   (["../escape"], "evidence/new.json", "."),
                   ([str(self.root / "src")], "evidence/new.json", "."),
                   (self.scopes, "../outside.json", "."), (self.scopes, "evidence/file.txt", "."),
                   (self.scopes, "missing/file.json", "."), (self.scopes, "src/result.json", "."),
                   (["."], "evidence/result.json", "."), (self.scopes, "evidence/new.json", "../"),
                   (self.scopes, "evidence/new.json", "src/main.py"),
                   (self.scopes, "evidence/new.json", ""), ([""], "evidence/new.json", ".")]
        for scopes, output, cwd in invalid:
            with self.subTest(scopes=scopes, output=output, cwd=cwd):
                with self.assertRaises((ValueError, OSError)):
                    self.record("from pathlib import Path; Path('ran').touch()", sources=scopes, output=output, cwd=cwd)
                self.assertFalse((self.root / "ran").exists())
                self.assertEqual(list((self.root / "evidence").iterdir()), [])

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

    def test_ignored_and_sensitive_content_not_hashed(self):
        self.write("src/node_modules/huge.js", "must not read")
        self.write("src/.env", "secret-token")
        self.write("src/ignored/private.txt", "private-token")
        snapshot = self.snapshot()
        self.assertEqual(len(snapshot["files"]), 3)
        for source in ("src/node_modules", "src/.env", "src/ignored"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.record(sources=[source])
        self.assertIn("Git-ignored", " ".join(snapshot["coverage"]))

    def test_unborn_repo_has_no_commit_identity(self):
        root = self.root / "unborn"
        root.mkdir()
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        (root / "code.py").write_text("pass")
        report, code = evidence.record_verification(root, ["code.py"], "result.json", [sys.executable, "-B", "-c", "pass"])
        self.assertEqual(code, 0)
        self.assertIsNone(report["tested_commit"])
        self.assertIsNone(report["source_pre"]["head"])
        self.assertTrue(report["source_pre"]["files"][0]["new"])
        self.assertFalse(report["identity_complete"])

    def test_non_git_hashes_and_exclusion_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "src").mkdir()
            (root / "src/main.py").write_text("pass")
            (root / "src/.env").write_text("not recorded")
            report, code = evidence.record_verification(root, ["src"], "result.json", [sys.executable, "-B", "-c", "pass"])
            self.assertEqual(code, 0)
            self.assertEqual(report["source_pre"]["git"], "non_git")
            self.assertIsNone(report["tested_commit"])
            self.assertIsNotNone(report["source_pre"]["files"][0]["sha256"])
            self.assertEqual(len(report["source_pre"]["excluded"]), 1)
            self.assertTrue(report["identity_complete"])
            self.assertIn("ignore rules are unavailable", " ".join(report["limitations"]))

    def test_unicode_spaces_and_literal_pathspec(self):
        name = "src/\ud55c\uae00 [one] file.py"
        self.write(name, "unicode fixture\n")
        self.write("src/\ud55c\uae00 o file.py", "do not match wildcard\n")
        self.git("add", "--", name)
        report, _ = self.record(sources=[name])
        self.assertEqual([item["path"] for item in report["source_pre"]["files"]], [name])
        self.assertEqual(report["source_pre"]["files"][0]["status"], "A ")

    def test_git_collection_failure_is_not_clean_identity(self):
        with mock.patch.object(evidence, "_inventory", side_effect=OSError("private diagnostic")):
            report, code = self.record()
        self.assertEqual(code, 0)
        self.assertFalse(report["identity_complete"])
        self.assertIsNone(report["tested_commit"])
        self.assertNotIn("private diagnostic", json.dumps(report))

    def test_file_read_failure_is_incomplete(self):
        original = Path.open

        def fail(path, *args, **kwargs):
            if path.name == "main.py":
                raise PermissionError("private path")
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "open", fail):
            report, _ = self.record()
        self.assertFalse(report["identity_complete"])
        self.assertIsNone(report["tested_commit"])
        self.assertNotIn("private path", json.dumps(report))

    def test_assume_unchanged_does_not_claim_clean_commit(self):
        self.git("update-index", "--assume-unchanged", "--", "src/main.py")
        self.write("src/main.py", "hidden change\n")
        report, _ = self.record()
        self.assertIsNone(report["tested_commit"])
        self.assertFalse(report["identity_complete"])

    def test_clean_git_status_cannot_override_raw_content_mismatch(self):
        original = evidence._inventory(self.root, self.scopes)
        self.write("src/main.py", "value = 2\n")
        with mock.patch.object(evidence, "_inventory", return_value=original):
            report, _ = self.record()
        self.assertTrue(report["identity_complete"])
        self.assertFalse(report["source_pre"]["scoped_dirty"])
        self.assertFalse(self.files(report["source_pre"])["src/main.py"]["raw_matches_index"])
        self.assertIsNone(report["tested_commit"])

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

    def test_symlink_source_and_output_escape_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            outside = Path(folder)
            (outside / "secret.py").write_text("not read")
            self.symlink(self.root / "src/link.py", outside / "secret.py")
            with self.assertRaises(ValueError):
                self.record()
            (self.root / "src/link.py").unlink()
            self.symlink(self.root / "escape", outside, directory=True)
            for kwargs in ({"output": "escape/result.json"}, {"sources": ["escape"]}, {"cwd": "escape"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    self.record(**kwargs)
            self.assertFalse((outside / "result.json").exists())

    def test_internal_symlink_conservatively_rejected(self):
        self.symlink(self.root / "src/link.py", self.root / "src/main.py")
        with self.assertRaises(ValueError):
            self.record()

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

    def test_cli_verify_without_run(self):
        result = self.cli("--verify", "--source", "src", "--evidence", "evidence/cli.json", "--", sys.executable, "-B", "-c", "pass")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(json.loads((self.root / "evidence/cli.json").read_text())["run_id"])

    def test_cli_invalid_flags_or_run_never_launch(self):
        base = ["--verify", "--source", "src", "--evidence", "evidence/cli.json"]
        command = ["--", sys.executable, "-B", "-c", "from pathlib import Path; Path('ran').touch()"]
        variants = [base + ["--run-id", "RUN-999"] + command,
                    base + ["--dry-run"] + command, base + ["--json"] + command,
                    base + ["--runner", "thread"] + command,
                    base + command[1:], base + ["--"], ["--dry-run", "--json"],
                    ["--verify", "--evidence", "evidence/cli.json"] + command,
                    ["--run-id", "RUN-001", "--source", "src", "--dry-run"]]
        for args in variants:
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse((self.root / "ran").exists())
                self.assertFalse((self.root / "evidence/cli.json").exists())

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

    def test_missing_project_and_invalid_argv(self):
        with self.assertRaises(OSError):
            evidence.capture_source_snapshot(self.root / "missing", ["src"])
        for command in ([], "echo test", [""], [sys.executable, "\x00"]):
            with self.subTest(command=command), self.assertRaises(ValueError):
                evidence.record_verification(self.root, self.scopes, "evidence/new.json", command)
        self.assertFalse((self.root / "evidence/new.json").exists())


if __name__ == "__main__":
    unittest.main()
