"""Installed authoring routes and optional templates, not live product QA."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from vulcan_core.product_documents import ProductDocuments
from vulcan_core.document_context import _sections, _reference_definitions, _links

spec = importlib.util.spec_from_file_location("vulcan_product_writing_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)

GUIDE = "docs/core/PRODUCT_DOCUMENT_WRITING.md"
ROUTES = (
    "AGENTS.md", "GEMINI.md", "docs/core/PRODUCT_PROFILE_BASELINE.md",
    "docs/core/PRODUCT_WORKER_GUIDE.md", "docs/core/GATE_EXECUTION_CHECKLIST.md",
    "docs/adapters/codex-gpt/GATE_PROMPTS.md", "docs/adapters/gemini/GATE_PROMPTS_GEMINI.md",
    ".agents/skills/vulcan-orchestrator/SKILL.md", ".agents/skills/vulcan-design/SKILL.md",
    ".agents/skills/vulcan-qa/SKILL.md",
)


class ProductWritingTests(unittest.TestCase):
    def temp_root(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        return Path(temp.name).resolve()

    @staticmethod
    def write(root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def render_template(self, name):
        return vulcan.render((ROOT / "docs/templates/product" / name).read_text(encoding="utf-8"),
                             {"PROJECT_NAME": "fixture", "GENERATED_DATE": "2026-09-10"})

    def fixture(self):
        root = self.temp_root()
        shutil.copytree(ROOT / "scripts/regression/fixtures/simple-todo-product", root, dirs_exist_ok=True)
        self.write(root, "session.json", json.dumps({"profile": "product", "current_gate": "gate4"}))
        self.write(root, "vulcan.config.json", json.dumps({"delivery_profile": "product"}))
        return root

    def test_init_routes_both_primaries_and_keeps_only_six_working_ledgers(self):
        for primary in ("codex-cli", "antigravity-cli"):
            with self.subTest(primary=primary):
                root = self.temp_root() / "project"
                with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(
                        vulcan.subprocess, "run", side_effect=OSError("Git disabled in fixture")):
                    vulcan.init(str(root), "fixture", "Tester", profile="product", primary=primary)
                self.assertTrue((root / GUIDE).is_file())
                self.assertEqual({p.name for p in (root / "docs/product").glob("*.md")},
                                 {Path(dst).name for _, dst in vulcan.PRODUCT_ARTIFACT_TEMPLATES})
                for route in ROUTES:
                    self.assertIn("PRODUCT_DOCUMENT_WRITING.md", (root / route).read_text(encoding="utf-8"), route)
                for src, dst in vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES:
                    self.assertTrue((root / src).is_file(), src)
                    self.assertFalse((root / dst).exists(), dst)

    def test_upgrade_refreshes_optional_templates_without_rewriting_authored_sources(self):
        root = self.temp_root() / "project"
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(
                vulcan.subprocess, "run", side_effect=OSError("Git disabled in fixture")):
            vulcan.init(str(root), "fixture", "Tester", profile="product", primary="codex-cli")
        authored = [dst for _, dst in vulcan.PRODUCT_ARTIFACT_TEMPLATES]
        authored += [dst for _, dst in vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES]
        for i, path in enumerate(authored):
            self.write(root, path, f"# Authored {i}\nOriginal contract and pending obligation.\n")
        before = {p: (root / p).read_bytes() for p in authored}
        for src, _ in vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES:
            self.write(root, src, "# Old template\n")
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.object(
                vulcan.subprocess, "run", side_effect=AssertionError("No external processes in upgrade fixture")):
            vulcan.cmd_upgrade(str(root))
        self.assertEqual(before, {p: (root / p).read_bytes() for p in authored})
        for src, _ in vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES:
            expected = vulcan.render((ROOT / src).read_text(encoding="utf-8"), vulcan.extract_variables(str(root)))
            self.assertEqual((root / src).read_text(encoding="utf-8"), expected)

    def test_contract_detail_templates_have_no_conflicting_primary_id_definitions(self):
        root = self.fixture()
        links = []
        for src, dst in vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES:
            if "/02-design/" not in dst:
                continue
            self.write(root, dst, self.render_template(Path(src).name).replace("TBD", "Defined contract"))
            links.append(f"[detail](../artifacts/{dst.split('docs/artifacts/')[1]})")
        self.write(root, "docs/product/PRODUCT_CONTRACTS.md", "# Contracts\n" + "\n".join(links))
        docs = ProductDocuments(root, ["PRODUCT_CONTRACTS.md"])
        records = docs.records("PRODUCT_CONTRACTS.md", r"(?:API|DATA|DB|UI|SCR|SEC)-\d{3}", vulcan.parse_markdown_tables)
        self.assertEqual(docs.issues, [], docs.issues)
        self.assertEqual([r["id"] for r in records].count("API-001"), 1)
        self.assertEqual(vulcan.product_definition_ids(docs, "PRODUCT_CONTRACTS.md", r"SEC-\d{3}"), {"SEC-001"})
        issues, _ = vulcan.collect_product_profile_findings(str(root), "gate4")
        self.assertEqual(issues, [], issues)

    def test_requirement_detail_does_not_redefine_brief_scenario(self):
        root = self.fixture()
        content = self.render_template("PRODUCT_REQUIREMENTS_TEMPLATE.md").replace("TBD", "Defined requirement")
        self.write(root, "docs/artifacts/01-requirements/tasks.md", content)
        brief = root / "docs/product/PRODUCT_BRIEF.md"
        self.write(root, "docs/product/PRODUCT_BRIEF.md", brief.read_text(encoding="utf-8") +
                   "\n[requirements](../artifacts/01-requirements/tasks.md)\n")
        docs = ProductDocuments(root, ["PRODUCT_BRIEF.md"])
        docs.records("PRODUCT_BRIEF.md", r"(?:REQ|SCN)-\d{3}", vulcan.parse_markdown_tables)
        self.assertEqual(docs.issues, [], docs.issues)
        self.assertIn("REQ-001", vulcan.product_requirement_ids(docs))

    def test_documented_api_link_keeps_surface_validation_and_implementation_boundary(self):
        root = self.fixture()
        guide = (ROOT / GUIDE).read_text(encoding="utf-8")
        example = re.search(r"```markdown\n(.*?)\n```", guide, re.S).group(1)
        self.write(root, "docs/product/PRODUCT_CONTRACTS.md", "# Contracts\n" + example)
        self.write(root, "docs/artifacts/02-design/api/tasks.md",
                   self.render_template("PRODUCT_API_CONTRACT_TEMPLATE.md").replace("TBD", "Defined contract"))
        docs = ProductDocuments(root, ["PRODUCT_CONTRACTS.md"])
        self.assertEqual(docs.issues, [], docs.issues)
        for section in ("## 2. API Surface", "## 3. Request / Response Contract",
                        "## 4. Validation And Error Policy", "## 5. Implementation Boundary"):
            self.assertIn(section, docs.text("PRODUCT_CONTRACTS.md"))

    def test_test_plan_and_execution_templates_remain_separate_and_block_not_run(self):
        root = self.fixture()
        self.write(root, "docs/product/REGRESSION_AND_RELEASE_REPORT.md",
                   "# Report\n## Regression Plan\n[plan](../artifacts/03-test/tasks.md)\n"
                   "## Current Execution Results\n[result](../artifacts/04-review/batch/results.md)\n")
        plan = self.render_template("PRODUCT_TEST_PLAN_TEMPLATE.md").replace("TBD", "Defined test")
        result = self.render_template("PRODUCT_VERIFICATION_RESULT_TEMPLATE.md").replace("TBD", "Observed basis")
        self.write(root, "docs/artifacts/03-test/tasks.md", plan)
        path = self.write(root, "docs/artifacts/04-review/batch/results.md", result)
        docs = ProductDocuments(root, ["REGRESSION_AND_RELEASE_REPORT.md"])
        findings = vulcan.product_verification_result_findings(docs.texts("REGRESSION_AND_RELEASE_REPORT.md"), "gate4", [])
        self.assertTrue(any("REG-001" in i for i in findings), findings)
        self.assertTrue(any("SEC-REG-001" in i for i in findings), findings)
        path.write_text(result.replace("| Not Run |", "| Pass |"), encoding="utf-8")
        docs = ProductDocuments(root, ["REGRESSION_AND_RELEASE_REPORT.md"])
        self.assertEqual(vulcan.product_verification_result_findings(docs.texts("REGRESSION_AND_RELEASE_REPORT.md"), "gate4", []), [])
        counts = vulcan._product_test_status_counts(str(root), docs)
        self.assertEqual((counts["total"], counts["passed"], counts["security"]["passed"]), (1, 1, 1))
        self.assertEqual((root / "docs/artifacts/03-test/tasks.md").read_text(encoding="utf-8"), plan)

    def test_optional_template_entries_and_guide_links_resolve(self):
        for src, _ in vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES:
            self.assertTrue((ROOT / src).is_file(), src)
        guide = (ROOT / GUIDE).read_text(encoding="utf-8")
        for name in re.findall(r"`(PRODUCT_[A-Z_]+_TEMPLATE\.md)`", guide):
            self.assertTrue((ROOT / "docs/templates/product" / name).is_file(), name)
        sections = _sections(guide)
        definitions = _reference_definitions("".join(s["visible"] for s in sections))
        for section in sections:
            for link in _links(ROOT, GUIDE, section["visible"], definitions):
                self.assertEqual(link["status"], "available", link)


if __name__ == "__main__":
    unittest.main()
