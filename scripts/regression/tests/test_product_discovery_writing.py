"""Business-source routing, not automatic business agreement or product QA."""

from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest

from test_product_writing import vulcan
from vulcan_core import document_context, product_process, product_readiness
from vulcan_core.product_documents import ProductDocuments


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "scripts/regression/fixtures/product-discovery-writing"
BRIEF = "docs/product/PRODUCT_BRIEF.md"
FLOW = "docs/artifacts/01-requirements/requests-flow.md"
REQ = "docs/artifacts/01-requirements/requests.md"
PLAN = "docs/artifacts/03-test/resubmit.md"
CANDIDATE = "<!-- vulcan:state=candidate -->"
CURRENT = "<!-- vulcan:state=current -->"


class ProductDiscoveryWritingTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        shutil.copytree(FIXTURE / "docs", self.root / "docs")

    def files(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file()}

    def ref(self, path):
        return product_readiness.local_reference(self.root, path, markdown=True)

    def scope(self):
        return {"work": {"ref": "issue:synthetic-writing-test", "revision": "fixture:1"},
                "related_ids": ["REQ-001", "AC-001", "AC-002"],
                "contracts": [self.ref(REQ + "#req-001"), self.ref(FLOW + "#rules-and-examples")],
                "tests": [self.ref(PLAN + "#regression-plan")],
                "required_checks": ["REG-001", "REG-002"]}

    def adopt_in_test_only(self):
        # Simulated agreement for parser tests only. Published example stays candidate.
        path = self.root / REQ
        text = path.read_text(encoding="utf-8").replace(CANDIDATE, CURRENT, 1)
        text = text.replace("미정 권한·상태가 있으므로 아래 요구·AC는 후보이며 구현 허가가 아니다.",
                            "합성 파서 시험에서만 채택한 요구이며 실제 사용자 합의가 아니다.")
        text = text.replace("권한·상태·보존 정책의 미정 사항은 [열린 결정](requests-flow.md#open-decisions)에서 확인한다. 이 미정 사항은 관련 요구 확정에 영향을 준다.",
                            "이 합성 시험은 문서 연결만 검사한다. 실제 업무 권한/상태/보존 정책이나 구현을 승인하지 않는다.")
        path.write_text(text, encoding="utf-8")
        path = self.root / PLAN
        path.write_text(path.read_text(encoding="utf-8").replace(CANDIDATE, CURRENT, 1), encoding="utf-8")

    def test_candidate_example_is_not_a_current_requirement_definition(self):
        before = self.files()
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertEqual(docs.issues, [])
        self.assertEqual(docs.warnings, [])
        self.assertEqual(vulcan.product_requirement_ids(docs), set())
        self.assertEqual(vulcan.product_definition_ids(docs, "PRODUCT_BRIEF.md", r"AC-\d{3}"), set())
        self.assertIn("수량을 알려주세요", docs.text("PRODUCT_BRIEF.md"))
        self.assertEqual(before, self.files())

    def test_candidate_scope_cannot_be_implemented_by_selecting_its_ids(self):
        result = product_readiness.document_readiness(self.root, self.scope(), vulcan.parse_markdown_tables)
        self.assertFalse(result["ready"], result)
        self.assertTrue(any(i["code"] == "invalid_reference" for i in result["issues"]), result)

    def test_lookup_finds_candidates_and_rule_sources_without_authority(self):
        before = self.files()
        result = document_context.lookup_sections(self.root, "REQ-001,AC-002")
        paths = {s["path"] for s in result["sections"]}
        self.assertIn(REQ, paths)
        self.assertIn(FLOW, paths)
        self.assertIn(PLAN, paths)
        self.assertFalse(result["authority"])
        self.assertTrue(any(s["state"] == "candidate" for s in result["sections"]))
        self.assertEqual(before, self.files())

    def test_synthetic_current_sources_are_unique_and_plans_are_not_execution(self):
        self.adopt_in_test_only()
        before = self.files()
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertEqual(docs.issues, [])
        rows = docs.records("PRODUCT_BRIEF.md", r"(?:REQ|AC)-\d{3}", vulcan.parse_markdown_tables)
        self.assertCountEqual([r["id"] for r in rows], ["REQ-001", "AC-001", "AC-002"])
        self.assertTrue(all(r["source"].startswith(REQ + ":") for r in rows))
        session = product_process.new_session(self.scope())
        original = deepcopy(session)
        result = product_readiness.collect(self.root, session, vulcan.parse_markdown_tables)
        self.assertEqual(result["status"], "ready", result)
        self.assertEqual(result["execution"], "not_required_at_this_stage")
        self.assertFalse(result["transition"]["allowed"])
        self.assertEqual(session, original)
        self.assertEqual(before, self.files())

    def test_linked_rule_is_not_optional_when_preparing_a_scope(self):
        self.adopt_in_test_only()
        scope = self.scope()
        scope["contracts"] = scope["contracts"][:1]
        result = product_readiness.document_readiness(self.root, scope, vulcan.parse_markdown_tables)
        self.assertFalse(result["ready"])
        self.assertTrue(any(i["code"] == "unbound_reference" and i["path"] == REQ
                            for i in result["issues"]), result)

    def test_changed_or_missing_rule_cannot_reuse_the_previous_scope(self):
        self.adopt_in_test_only()
        scope = self.scope()
        path = self.root / FLOW
        path.write_text(path.read_text(encoding="utf-8") + "\nChanged business boundary.\n", encoding="utf-8")
        result = product_readiness.document_readiness(self.root, scope, vulcan.parse_markdown_tables)
        self.assertFalse(result["ready"])
        self.assertTrue(any("revision changed" in i["message"] for i in result["issues"]), result)
        path.unlink()
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(docs.issues)

    def test_requirement_template_defines_primary_req_and_observable_ac_rows(self):
        text = (ROOT / "docs/templates/product/PRODUCT_REQUIREMENTS_TEMPLATE.md").read_text(encoding="utf-8")
        text = vulcan.render(text, {"PROJECT_NAME": "synthetic", "GENERATED_DATE": "2026-09-12"})
        (self.root / REQ).write_text(text.replace("TBD", "Explicit scoped condition"), encoding="utf-8")
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        rows = docs.records("PRODUCT_BRIEF.md", r"(?:REQ|AC)-\d{3}", vulcan.parse_markdown_tables)
        self.assertCountEqual([r["id"] for r in rows], ["REQ-001", "AC-001"])
        ac = next(r for r in rows if r["id"] == "AC-001")
        self.assertEqual(len(ac["cells"]), 3)
        scope = self.scope()
        scope["related_ids"] = ["REQ-001", "AC-001"]
        scope["tests"] = [self.ref(PLAN + "#regression-plan")]
        result = product_readiness.document_readiness(self.root, scope, vulcan.parse_markdown_tables)
        self.assertFalse(any(i["code"] == "missing_definition" and "REQ-001" in i["message"]
                             for i in result["issues"]), result)

    def test_flow_template_is_optional_and_does_not_redefine_ids(self):
        entry = ("docs/templates/product/PRODUCT_BUSINESS_FLOW_TEMPLATE.md",
                 "docs/artifacts/01-requirements/PRODUCT_BUSINESS_FLOW.md")
        self.assertIn(entry, vulcan.PRODUCT_OPTIONAL_DETAIL_TEMPLATES)
        self.assertNotIn(entry, vulcan.PRODUCT_ARTIFACT_TEMPLATES)
        self.assertEqual(len(vulcan.PRODUCT_ARTIFACT_TEMPLATES), 6)
        for required in vulcan.PRODUCT_REQUIRED_ARTIFACTS_BY_GATE.values():
            self.assertNotIn(entry[1], required)
        text = (ROOT / entry[0]).read_text(encoding="utf-8")
        self.assertIn(CANDIDATE, text)
        for _, rows in vulcan.parse_markdown_tables(text):
            self.assertFalse(any(str(next(iter(row.values()), "")).startswith(("REQ-", "AC-", "SCN-")) for row in rows))
        self.adopt_in_test_only()
        rendered = vulcan.render(text, {"PROJECT_NAME": "synthetic", "GENERATED_DATE": "2026-09-12"})
        (self.root / FLOW).write_text(rendered.replace("TBD", "Explicit business example"), encoding="utf-8")
        before = self.files()
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertEqual(docs.issues, [])
        self.assertEqual(docs.warnings, [])
        self.assertIn("## Actors And Flow", docs.text("PRODUCT_BRIEF.md"))
        self.assertIn("Explicit business example", docs.text("PRODUCT_BRIEF.md"))
        checked = product_readiness.document_readiness(self.root, self.scope(), vulcan.parse_markdown_tables)
        self.assertTrue(checked["ready"], checked)
        self.assertEqual(before, self.files())

    def test_local_writing_links_and_anchors_resolve(self):
        paths = ["docs/core/PRODUCT_DOCUMENT_WRITING.md", "docs/core/ORCHESTRATOR_CLI_GUIDE.md",
                 "docs/reference/PRODUCT-DISCOVERY-AND-VALIDATION-GUIDE.md",
                 "docs/reference/PRODUCT-DISCOVERY-PILOT-REQUEST-BOARD.md"]
        paths += [p.relative_to(ROOT).as_posix() for p in FIXTURE.rglob("*.md")]
        for relative in paths:
            sections = document_context._sections((ROOT / relative).read_text(encoding="utf-8"))
            definitions = document_context._reference_definitions("".join(s["visible"] for s in sections))
            for section in sections:
                for link in document_context._links(ROOT, relative, section["visible"], definitions):
                    if link["status"] == "external":
                        continue
                    self.assertEqual(link["status"], "available", (relative, link))
                    if link["anchor"]:
                        target = document_context._sections((ROOT / link["path"]).read_text(encoding="utf-8"))
                        self.assertIn(link["anchor"], document_context._anchor_indices(target), (relative, link))

    def test_shared_guide_routes_planning_and_keeps_business_decisions_explicit(self):
        guide = (ROOT / "docs/core/PRODUCT_DOCUMENT_WRITING.md").read_text(encoding="utf-8")
        for phrase in ("## 0. 업무에서 요구로 연결한다", "사용자 답 하나는 전체 설계 확정, 구현 허가, 인수 승인이 아니다",
                       "기존 `<!-- vulcan:state=candidate -->`", "planning 안에서 업무·요구·설계·시험 계획을 반복",
                       "새 소유 폴더나 `00-discovery` 자동 수집을 추가하지 않는다"):
            self.assertIn(phrase, guide)
        cli = (ROOT / "docs/core/ORCHESTRATOR_CLI_GUIDE.md").read_text(encoding="utf-8")
        self.assertIn("PRODUCT_DOCUMENT_WRITING.md#0-업무에서-요구로-연결한다", cli)
        for adapter in ("AGENTS.md", "GEMINI.md", ".agents/skills/vulcan-orchestrator/SKILL.md"):
            self.assertIn("PRODUCT_DOCUMENT_WRITING.md", (ROOT / adapter).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
