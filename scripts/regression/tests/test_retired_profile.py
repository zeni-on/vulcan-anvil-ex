"""Exercise profile retirement at the CLI boundary, before any project write."""

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from vulcan_core.profiles import UnsupportedProfile, load_delivery_profile, normalize_delivery_profile
from vulcan_core.release import release_profile_policy


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "vulcan.py"


def snapshot(root):
    return {path.relative_to(root): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")}


class RetiredProfileTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.project = self.base / "project"
        self.project.mkdir()

    def record(self, name, value):
        (self.project / name).write_text(json.dumps(value), encoding="utf-8")

    def cli(self, *args, cwd=None, script=CLI):
        env = os.environ.copy()
        env.pop("PYTHONDONTWRITEBYTECODE", None)
        # Even a regressed command must not discover the developer's repository.
        env["GIT_CEILING_DIRECTORIES"] = os.pathsep.join((str(ROOT), str(self.base)))
        return subprocess.run([sys.executable, str(script), *map(str, args)], cwd=cwd or self.project,
                              input="", capture_output=True, encoding="utf-8", timeout=45, env=env)

    def rejected(self, *args, cwd=None):
        before = snapshot(self.base)
        result = self.cli(*args, cwd=cwd)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("retired", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(snapshot(self.base), before)

    def test_all_project_routes_reject_before_work(self):
        self.record("session.json", {"profile": "PoC", "vulcan_src": str(ROOT)})
        self.record("vulcan.config.json", {"delivery_profile": "product"})
        (self.project / "notes.md").write_bytes(b"user content\r\n")
        for args in [
            ["status", "--check", "--json"], ["profile-status"], ["doctor"], ["version"],
            ["profile-gap", "--to", "audit"], ["check-trace"], ["prepare-transition"],
            ["session", "--process-request", "missing.json", "--apply", "--json"],
            ["session", "--gate", "gate1", "--status", "done"], ["sync-session"],
            ["branch-start", "impl", "--apply"], ["release-pr", "--dry-run"],
            ["execute", "--verify", "--evidence", "unexpected.json", "--", "not-a-command"],
            ["wave-start", "BW-001"], ["run-preflight", "missing.md"],
            ["export", "--output", "unexpected.json"], ["upgrade"],
        ]:
            with self.subTest(command=args):
                self.rejected(*args)

    def test_profile_fields_in_either_file_cannot_be_shadowed(self):
        for session, config in [
            ({"delivery_profile": "PoC"}, {}),
            ({"profile": "audit", "delivery_profile": "poc"}, {}),
            ({"profile": "product", "process_model": "product-iterative-v1"}, {"delivery_profile": "poc"}),
            ({}, {"profile": "poc", "delivery_profile": "solution"}),
        ]:
            with self.subTest(session=session, config=config):
                self.record("session.json", session)
                self.record("vulcan.config.json", config)
                self.rejected("upgrade")
                self.rejected("doctor", "--project-dir", self.project, cwd=self.base)
        (self.project / "session.json").unlink()
        self.rejected("init", self.project, "existing", "--profile", "product", cwd=self.base)
        self.rejected("release", "--target", self.project, cwd=self.base)

    def test_cli_and_policy_never_alias_retired_values(self):
        for value in ("poc", " PoC ", "proof-of-concept"):
            with self.subTest(value=value):
                self.rejected("init", self.base / "never-created", "sample", "--profile", value)
                self.rejected("profile-gap", "--to", value)
                with self.assertRaises(UnsupportedProfile):
                    release_profile_policy(value)
        for value in ("", None, "AUDIT"):
            self.assertEqual(normalize_delivery_profile(value), "audit")
        self.assertEqual(normalize_delivery_profile("solution"), "product")
        with self.assertRaises(UnsupportedProfile):
            normalize_delivery_profile("unrecognized")
        self.record("session.json", {"profile": "product"})
        self.record("vulcan.config.json", {"delivery_profile": "audit"})
        self.assertEqual(load_delivery_profile(self.project), "product")

    def test_supported_upgrade_ignores_stale_source_templates_and_preserves_user_files(self):
        source = self.base / "source"
        (source / "templates").mkdir(parents=True)
        for template in ("poc/stale.md", "product/PRODUCT_BRIEF_TEMPLATE.md", "PROJECT_BRIEF_TEMPLATE.md"):
            path = source / "docs/templates" / template
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(template, encoding="utf-8")
        for profile, brief in [
            ("audit", "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md"),
            ("product", "docs/product/PRODUCT_BRIEF.md"),
        ]:
            with self.subTest(profile=profile):
                root = self.base / profile
                root.mkdir()
                (root / "session.json").write_text(json.dumps({"profile": profile, "vulcan_src": str(source)}))
                (root / ".claude").mkdir()
                (root / ".claude/CLAUDE.md").write_text("# Test Harness\n")
                notes = root / "docs/poc/authored.md"
                notes.parent.mkdir(parents=True)
                notes.write_bytes(b"keep me\r\n")
                result = self.cli("upgrade", cwd=root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads((root / "session.json").read_bytes())["profile"], profile)
                self.assertTrue((root / brief).is_file())
                self.assertFalse((root / "docs/templates/poc").exists())
                self.assertEqual(snapshot(notes.parent), {Path("authored.md"): b"keep me\r\n"})

    def stock_templates(self):
        archive = subprocess.run(["git", "archive", "--format=zip", "v0.5.0", "docs/templates/poc"],
                                 cwd=ROOT, capture_output=True)
        if archive.returncode:
            self.skipTest("historical v0.5.0 tag unavailable")
        with zipfile.ZipFile(io.BytesIO(archive.stdout)) as old:
            return {Path(name).name: old.read(name) for name in old.namelist() if name.endswith(".md")}

    def supported_upgrade_fixture(self, profile="audit"):
        source = self.base / "framework"
        (source / "templates").mkdir(parents=True, exist_ok=True)
        self.record("session.json", {"project": "Test", "profile": profile, "vulcan_src": str(source)})
        (self.project / ".claude").mkdir(exist_ok=True)
        (self.project / ".claude/CLAUDE.md").write_text("# Test Harness\n")

    def test_upgrade_removes_all_and_only_matching_historical_bytes(self):
        stock = self.stock_templates()
        self.assertEqual(len(stock), 3)
        folder = self.project / "docs/templates/poc"
        authored = self.project / "docs/poc"
        authored.mkdir(parents=True)
        for name, data in stock.items():
            (authored / name).write_bytes(data)
        old_work = snapshot(authored)
        for profile, newline in [("audit", b"\n"), ("product", b"\r\n")]:
            self.supported_upgrade_fixture(profile)
            folder.mkdir(parents=True)
            for name, data in stock.items():
                (folder / name).write_bytes(data.replace(b"\r\n", b"\n").replace(b"\n", newline))
            result = self.cli("upgrade")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(folder.exists())
            self.assertEqual(snapshot(authored), old_work)

        folder.mkdir()
        a, b, c = sorted(stock)
        modified = {a: stock[a].replace(b"{{PROJECT_NAME}}", b"Test"), b: stock[b] + b" ",
                    "authored.md": stock[c]}
        for name, data in modified.items():
            (folder / name).write_bytes(data)
        (folder / c).write_bytes(stock[c])
        result = self.cli("upgrade")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(folder), {Path(n): data for n, data in modified.items()})
        self.assertEqual(snapshot(authored), old_work)

    def test_upgrade_never_traverses_linked_retired_template_directories(self):
        self.supported_upgrade_fixture()
        external = self.base / "outside-project"
        external.mkdir()
        stock = self.stock_templates()
        for ancestor in ("docs", "docs/templates", "docs/templates/poc"):
            with self.subTest(ancestor=ancestor):
                link = self.project / ancestor
                link.parent.mkdir(parents=True, exist_ok=True)
                originals = external / Path("docs/templates/poc").relative_to(ancestor)
                originals.mkdir(parents=True, exist_ok=True)
                for name, data in stock.items():
                    (originals / name).write_bytes(data)
                before = snapshot(external)
                if os.name == "nt":
                    import _winapi
                    _winapi.CreateJunction(str(external), str(link))
                else:
                    link.symlink_to(external, target_is_directory=True)
                try:
                    result = self.cli("upgrade")
                    if ancestor.endswith("/poc"):
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("linked docs/templates", result.stderr)
                    self.assertEqual(snapshot(external), before)
                finally:
                    if os.name == "nt":
                        link.rmdir()
                    else:
                        link.unlink()

    def test_upgrade_preserves_linked_candidate_files(self):
        self.supported_upgrade_fixture()
        folder = self.project / "docs/templates/poc"
        folder.mkdir(parents=True)
        name, data = next(iter(self.stock_templates().items()))
        external = self.base / "outside.md"
        external.write_bytes(data)
        candidate = folder / name
        try:
            candidate.symlink_to(external)
        except OSError:
            # Windows without symlink privilege: a hard link must also be preserved.
            os.link(external, candidate)
        result = self.cli("upgrade")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(candidate.samefile(external))
        self.assertEqual(external.read_bytes(), data)

    def test_v050_installed_upgrader_copies_new_cli_without_delegating(self):
        # Optional historical reproduction; release archives may lack Git tags.
        archive = subprocess.run(["git", "archive", "--format=zip", "v0.5.0", "vulcan.py", "vulcan_core"],
                                 cwd=ROOT, capture_output=True)
        if archive.returncode:
            self.skipTest("historical v0.5.0 tag unavailable")
        with zipfile.ZipFile(io.BytesIO(archive.stdout)) as old:
            old.extractall(self.project)
        (self.project / ".claude").mkdir()
        (self.project / ".claude/CLAUDE.md").write_text("# Test Harness\n", encoding="utf-8")
        self.record("session.json", {"project": "fixture", "profile": "poc",
                                     "vulcan_version": "old-fixture", "vulcan_src": str(ROOT)})
        self.record("vulcan.config.json", {"delivery_profile": "poc"})
        self.rejected("upgrade")
        local = self.project / "vulcan.py"
        self.assertNotEqual(local.read_bytes(), CLI.read_bytes())
        result = self.cli("upgrade", script=local)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(local.read_bytes(), CLI.read_bytes())
        session = json.loads((self.project / "session.json").read_bytes())
        self.assertNotEqual(session["vulcan_version"], "old-fixture")
        self.assertEqual(session["profile"], "poc")
        before = snapshot(self.project)
        result = self.cli("upgrade", script=local)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("retired", result.stderr)
        self.assertEqual(snapshot(self.project), before)
