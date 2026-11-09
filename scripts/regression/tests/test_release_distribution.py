"""Exercise the actual release package, not a CLI importing from the source checkout."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_product_process import vulcan


ROOT = Path(__file__).resolve().parents[3]


class ReleaseDistributionTests(unittest.TestCase):
    def cli(self, script, cwd, *args):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        # Run the package standalone; no real Git commit, network or external runners.
        env["PATH"] = str(Path(sys.executable).parent)
        env["PYTHONNOUSERSITE"] = "1"
        return subprocess.run([sys.executable, "-B", str(script), *map(str, args)], cwd=cwd, env=env,
                              input="", capture_output=True, encoding="utf-8", timeout=60)

    def ok(self, script, cwd, *args):
        result = self.cli(script, cwd, *args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_real_package_initializes_both_profiles_and_keeps_private_data_out(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            base = Path(temp)
            source = base / "first-release"
            target = base / "clean-release"
            source.mkdir()
            target.mkdir()
            self.ok(ROOT / "vulcan.py", base, "release", "--target", source)
            private = [
                "session.json", "vulcan.config.json", ".codex/config.toml", ".gemini/settings.json",
                ".claude/settings.local.json", ".vulcan/comments/comments.jsonl", "docs/ref-docs/customer.md",
                "docs/reference/internal.md", "docs/artifacts/private.md", "docs/product/PRODUCT_BRIEF.md",
                "docs/templates/poc/POC_REQUIREMENTS_TEMPLATE.md", "docs/templates/customer.md",
                "templates/private-case.md", "dashboard/projects.json", "dashboard/.env",
                "dashboard/.env.production", "dashboard/.env.local", "dashboard/debug.log",
                "dashboard/test-results/results.json", "dashboard/playwright-report/index.html",
                "dashboard/node_modules/example/index.js", "dashboard/.next/cache/data.json",
                "dashboard/src/__tests__/private.ts", "dashboard/capture-011.mjs",
            ]
            for rel in private:
                self.assertFalse((source / rel).exists(), rel)
                path = source / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}" if path.suffix == ".json" else "private-synthetic", encoding="utf-8")
            self.ok(source / "vulcan.py", base, "release", "--target", target)
            for rel in private:
                self.assertFalse((target / rel).exists(), rel)
            public = [
                "AGENTS.md", "GEMINI.md", ".agents/skills/vulcan-qa/SKILL.md",
                ".codex/agents/qa-reader.toml", ".gemini/agents/qa-reader.toml",
                "docs/adapters/codex-gpt/skills/qa-execution.md", "docs/core/RUN_INPUT_CONTRACT.md",
                "docs/seed-docs/README.md", "templates/.claude/settings.json", "dashboard/package.json",
                "dashboard/src/app/page.tsx", "docs/templates/product/PRODUCT_TEST_PLAN_TEMPLATE.md",
            ]
            for rel in public:
                self.assertEqual((target / rel).read_bytes(), (ROOT / rel).read_bytes(), rel)
            template = Path("docs/templates/product/PRODUCT_BRIEF_TEMPLATE.md")
            self.assertEqual((target / template).read_bytes(), (ROOT / template).read_bytes())
            for profile in ("audit", "product"):
                with self.subTest(profile=profile):
                    project = base / profile
                    self.ok(target / "vulcan.py", base, "init", project, "Synthetic", "--profile", profile,
                            "--primary", "codex-cli")
                    session = json.loads((project / "session.json").read_bytes())
                    self.assertEqual(session["profile"], profile)
                    self.assertEqual(Path(session["vulcan_src"]).resolve(), target)
                    mappings = (vulcan.PRODUCT_ARTIFACT_TEMPLATES if profile == "product"
                                else vulcan.PROJECT_ARTIFACT_TEMPLATES)
                    for src, dst in mappings:
                        self.assertEqual((target / src).read_bytes(), (ROOT / src).read_bytes(), src)
                        self.assertTrue((project / dst).stat().st_size, dst)
                    for rel in public[:8]:
                        self.assertTrue((project / rel).is_file(), rel)
                    if profile == "product":
                        self.assertEqual({p.stem for p in (project / "docs/product").glob("*.md")}, {
                            "PRODUCT_BRIEF", "PRODUCT_ARCHITECTURE", "PRODUCT_TRACEABILITY", "PRODUCT_CONTRACTS",
                            "REGRESSION_AND_RELEASE_REPORT", "ADR_LOG"})
                        brief = project / "docs/product/PRODUCT_BRIEF.md"
                    else:
                        brief = project / "docs/artifacts/00-discovery/DOC-CORE-P0-001_Project-Brief_v0.1.md"
                        for name in ("DOC-QA-G3-001_Test-Cases_v0.1.md", "DOC-QA-G4-002_Test-Result_v0.1.md",
                                     "DOC-PM-G5-001_Release-Approval_v0.1.md"):
                            self.assertTrue(list((project / "docs/artifacts").rglob(name)), name)
                    self.assertIn("Synthetic", brief.read_text(encoding="utf-8"))
                    cli = project / "vulcan.py"
                    self.ok(cli, project, "profile-status")
                    (project / "cases.json").write_text('[{"id":"TC-001","status":"Blocked"}]')
                    self.ok(cli, project, "export", "--kind", "qa", "--input", "cases.json")
                    self.assertEqual(json.loads((project / "qa-report.json").read_bytes())["source_count"], 1)
            (target / template).unlink()
            result = self.cli(target / "vulcan.py", base, "init", base / "incomplete", "Broken", "--profile", "product")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing or linked framework template", result.stderr)
            self.assertFalse((base / "incomplete").exists())
