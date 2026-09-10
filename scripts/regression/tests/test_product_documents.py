import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from vulcan_core import product_documents as pd

spec = importlib.util.spec_from_file_location("vulcan_product_document_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class ProductDocumentTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        shutil.copytree(ROOT / "scripts/regression/fixtures/simple-todo-product", self.root, dirs_exist_ok=True)
        self.write("session.json", json.dumps({"profile": "product", "current_gate": "gate4", "project": "fixture"}))
        self.write("vulcan.config.json", json.dumps({"delivery_profile": "product", "workflow": {"enabled": False}}))

    def write(self, path, text):
        path = self.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def split(self, name, directory):
        original = self.root / "docs/product" / name
        target = f"docs/artifacts/{directory}/{name}"
        self.write(target, original.read_text(encoding="utf-8"))
        self.write(f"docs/product/{name}", f"# Document index\n[detail](../artifacts/{directory}/{name})\n")
        return target

    def evaluate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            issues, warnings = vulcan.validate_product_trace(str(self.root), "gate4")
            stats = vulcan.compute_product_stats(str(self.root))
        return issues, warnings, stats

    def test_legacy_split_mixed_equivalent_checks_counts_and_no_writes(self):
        issues, warnings, baseline = self.evaluate()
        self.assertEqual(issues, [], issues)
        for name, directory in (
            ("PRODUCT_BRIEF.md", "01-requirements"),
            ("PRODUCT_ARCHITECTURE.md", "02-design/architecture"),
            ("ADR_LOG.md", "02-design/architecture"),
            ("PRODUCT_CONTRACTS.md", "02-design/api"),
            ("PRODUCT_TRACEABILITY.md", "02-traceability"),
            ("REGRESSION_AND_RELEASE_REPORT.md", "03-test"),
        ):
            self.split(name, directory)
            before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*.md")}
            with self.subTest(moved=name):
                new_issues, new_warnings, stats = self.evaluate()
                self.assertEqual(new_issues, issues)
                self.assertEqual(new_warnings, warnings)
                self.assertEqual(stats["requirements"], baseline["requirements"])
                self.assertEqual(stats["tests"], baseline["tests"])
                self.assertEqual(stats["product"]["requirements"], baseline["product"]["requirements"])
                self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*.md")})

    def test_plan_and_execution_count_once_with_separate_security_ids(self):
        _, _, stats = self.evaluate()
        self.assertEqual(stats["tests"]["total"], 2)
        self.assertEqual(stats["tests"]["passed"], 2)
        self.assertEqual(stats["tests"]["security"]["total"], 1)
        self.assertEqual(stats["tests"]["security"]["passed"], 1)

    def test_exact_duplicate_trace_rows_not_double_counted(self):
        path = self.root / "docs/product/PRODUCT_TRACEABILITY.md"
        content = path.read_text(encoding="utf-8")
        self.write("docs/artifacts/02-traceability/copy.md", content)
        self.write("docs/product/PRODUCT_TRACEABILITY.md", content + "\n[copy](../artifacts/02-traceability/copy.md)\n")
        issues, _, stats = self.evaluate()
        self.assertFalse(any("conflicting definitions" in issue for issue in issues))
        self.assertEqual(stats["requirements"]["groups"], 3)
        self.assertEqual(stats["requirements"]["total"], 3)

    def test_conflicting_trace_blocks_and_does_not_count_both_as_implemented(self):
        path = self.root / "docs/product/PRODUCT_TRACEABILITY.md"
        content = path.read_text(encoding="utf-8")
        altered = content.replace("Verified", "Planned").replace("`app/main.py`, `static/app.js`, `tests/test_todos.py`", "TBD")
        self.write("docs/artifacts/02-traceability/conflict.md", altered)
        self.write("docs/product/PRODUCT_TRACEABILITY.md", content + "\n[conflict](../artifacts/02-traceability/conflict.md)\n")
        issues, _, stats = self.evaluate()
        self.assertTrue(any("conflicting definitions SCN-001" in issue for issue in issues), issues)
        self.assertEqual(stats["requirements"]["groups"], 3)
        self.assertEqual(stats["requirements"]["implemented"], 0)
        self.assertTrue(stats["product"]["document_diagnostics"]["incomplete"])

    def test_planned_trace_with_code_path_is_not_implementation_completion(self):
        path = self.root / "docs/product/PRODUCT_TRACEABILITY.md"
        self.write("docs/product/PRODUCT_TRACEABILITY.md", path.read_text(encoding="utf-8").replace("Verified", "Planned"))
        _, _, stats = self.evaluate()
        self.assertEqual(stats["requirements"]["implemented"], 0)

    def test_current_trace_conflict_still_pending_even_if_both_rows_say_verified(self):
        path = self.root / "docs/product/PRODUCT_TRACEABILITY.md"
        content = path.read_text(encoding="utf-8")
        self.write("docs/artifacts/02-traceability/conflict.md", content.replace("API-001", "API-099"))
        self.write("docs/product/PRODUCT_TRACEABILITY.md", content + "\n[other](../artifacts/02-traceability/conflict.md)\n")
        _, _, stats = self.evaluate()
        self.assertEqual(stats["requirements"]["implemented"], 0)
        self.assertTrue(stats["product"]["document_diagnostics"]["incomplete"])

    def test_detailed_requirement_ids_not_collapsed_to_parent_and_untraced_is_pending(self):
        self.write("docs/product/PRODUCT_BRIEF.md", "# Requirements\n[detail](../artifacts/01-requirements/requirements.md)\n")
        self.write("docs/artifacts/01-requirements/requirements.md", "# Requirements\n| REQ ID | Contract |\n| --- | --- |\n| REQ-001-01 | A |\n| REQ-001-02 | B |\n| REQ-002-01 | Not traced |\n")
        self.write("docs/product/PRODUCT_TRACEABILITY.md", "# Trace\n| Scenario ID | REQ | Scenario | Contract | Security | Implementation | Regression | Evidence | Status |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n| SCN-001 | REQ-001-01, REQ-001-02 | A | API-001 | SEC-001 | app.py | REG-001 | log | Verified |\n")
        _, warnings, stats = self.evaluate()
        self.assertEqual(stats["product"]["requirements"]["ids"], ["REQ-001-01", "REQ-001-02", "REQ-002-01"])
        self.assertEqual(stats["requirements"]["implemented"], 2)
        self.assertEqual(stats["requirements"]["pending"], 1)
        self.assertTrue(any("REQ-002-01" in w for w in warnings))

    def test_empty_missing_candidate_and_history_sources_do_not_satisfy_contract(self):
        for content in ("# SEC-001\n", "# Security\n<!-- vulcan:state=candidate -->\nSEC-001 candidate\n", "# Security\n<!-- vulcan:state=history -->\nSEC-001 old\n"):
            with self.subTest(content=content):
                self.write("docs/product/PRODUCT_CONTRACTS.md", "# Index\n[SEC-001](../artifacts/02-design/security/contracts.md)\n")
                self.write("docs/artifacts/02-design/security/contracts.md", content)
                issues, _, _ = self.evaluate()
                self.assertTrue(any("required content missing" in issue for issue in issues), issues)
        self.write("docs/product/PRODUCT_CONTRACTS.md", "# Index\n[SEC-001](../artifacts/02-design/security/missing.md)\n")
        issues, _, _ = self.evaluate()
        self.assertTrue(any("source reference" in issue for issue in issues), issues)

    def test_index_security_id_plus_prose_cannot_replace_security_definition(self):
        self.write("docs/product/PRODUCT_CONTRACTS.md", "# Contracts\nAPI contracts are maintained here.\n[SEC-001](../artifacts/02-design/security/empty.md)\n")
        self.write("docs/artifacts/02-design/security/empty.md", "# Security\n")
        issues, _, _ = self.evaluate()
        self.assertTrue(any("security definition missing" in issue for issue in issues), issues)

    def test_business_history_term_does_not_hide_requirement(self):
        path = self.root / "docs/product/PRODUCT_BRIEF.md"
        self.write("docs/product/PRODUCT_BRIEF.md", path.read_text(encoding="utf-8") + "\n## REQ-004 View task history\nUsers can view completed task history.\n")
        _, warnings, stats = self.evaluate()
        self.assertIn("REQ-004", stats["product"]["requirements"]["ids"])
        self.assertTrue(any("REQ-004" in w for w in warnings))

    def test_requirement_body_in_descendants_is_discovered(self):
        path = self.root / "docs/product/PRODUCT_BRIEF.md"
        self.write("docs/product/PRODUCT_BRIEF.md", path.read_text(encoding="utf-8") + "\n## REQ-004\n### Acceptance Criteria\nUsers can export all tasks.\n")
        _, warnings, stats = self.evaluate()
        self.assertIn("REQ-004", stats["product"]["requirements"]["ids"])
        self.assertTrue(any("REQ-004" in w for w in warnings))

    def test_split_test_plan_requires_actual_current_execution(self):
        self.write("docs/product/REGRESSION_AND_RELEASE_REPORT.md", "# Report\n[plan](../artifacts/03-test/plan.md)\n[results](../artifacts/04-review/current.md)\n")
        self.write("docs/artifacts/03-test/plan.md", "# Regression Plan\n| REG ID | Target | Method |\n| --- | --- | --- |\n| REG-001 | API-001 | test |\n| REG-002 | API-002 | test |\n| SEC-REG-001 | SEC-001 | test |\n")
        current = "# Current Execution Results\n| REG ID | Result |\n| --- | --- |\n| REG-001 | Pass |\n| SEC-REG-001 | Pass |\n"
        self.write("docs/artifacts/04-review/current.md", current)
        issues, _, stats = self.evaluate()
        self.assertTrue(any("REG-002: missing successful" in issue for issue in issues), issues)
        self.assertEqual(stats["tests"]["pending"], 1)
        self.write("docs/artifacts/04-review/current.md", current + "| REG-002 | Pass |\n")
        self.assertEqual(self.evaluate()[0], [])

    def test_linked_historical_pass_does_not_hide_current_failure(self):
        self.write("docs/product/REGRESSION_AND_RELEASE_REPORT.md", "# Results\n[current](../artifacts/04-review/current.md)\n[old](../artifacts/04-review/history.md)\n")
        self.write("docs/artifacts/04-review/current.md", "# Current Execution Results\n| REG ID | Result |\n| --- | --- |\n| REG-001 | Fail |\n| SEC-REG-001 | Pass |\n")
        self.write("docs/artifacts/04-review/history.md", "# History\n<!-- vulcan:state=history -->\n| REG ID | Result |\n| --- | --- |\n| REG-001 | Pass |\n")
        issues, _, stats = self.evaluate()
        self.assertTrue(any("REG-001" in issue for issue in issues))
        self.assertEqual(stats["tests"]["failed"], 1)
        self.assertEqual(stats["tests"]["passed"], 0)

    def test_cycles_anchors_and_limits_never_silently_complete(self):
        self.write("docs/product/PRODUCT_BRIEF.md", "# Product\n[x](../artifacts/01-requirements/a.md#feature)\n")
        self.write("docs/artifacts/01-requirements/a.md", "# Feature\nREQ-001 requirement\n[back](../../product/PRODUCT_BRIEF.md)\n")
        docs = pd.ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertEqual(docs.issues, [])
        self.assertEqual(len(docs.documents("PRODUCT_BRIEF.md")), 2)
        with mock.patch.object(pd, "MAX_DEPTH", 0):
            docs = pd.ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(any("depth limit" in issue for issue in docs.issues))
        self.write("docs/product/PRODUCT_BRIEF.md", "# Product\n[x](../artifacts/01-requirements/a.md#absent)\n")
        docs = pd.ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(any("anchor missing" in issue for issue in docs.issues))

    def test_document_and_reference_limits_are_blocking(self):
        self.write("docs/product/PRODUCT_BRIEF.md", "# Product\n[x](../artifacts/01-requirements/a.md)\n")
        self.write("docs/artifacts/01-requirements/a.md", "# Feature\nREQ-001 requirement\n")
        with mock.patch.object(pd, "MAX_DOCUMENTS", 1):
            docs = pd.ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(any("document limit" in issue for issue in docs.issues))
        with mock.patch.object(pd, "MAX_REFERENCES", 0):
            docs = pd.ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(any("reference limit" in issue for issue in docs.issues))

    def test_unreadable_owned_source_is_not_silently_skipped(self):
        self.write("docs/product/PRODUCT_BRIEF.md", "# Product\n[x](../artifacts/01-requirements/a.md)\n")
        self.write("docs/artifacts/01-requirements/a.md", "temporary").write_bytes(b"\xff\xfe")
        docs = pd.ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(any("unreadable" in issue for issue in docs.issues))

    def test_linked_index_id_is_not_a_second_definition(self):
        self.split("PRODUCT_TRACEABILITY.md", "02-traceability")
        path = self.root / "docs/product/PRODUCT_TRACEABILITY.md"
        self.write("docs/product/PRODUCT_TRACEABILITY.md", path.read_text(encoding="utf-8") + "\n| Scenario ID | Title | Source |\n| --- | --- | --- |\n| [SCN-001](../artifacts/02-traceability/PRODUCT_TRACEABILITY.md) | Index only | detail |\n")
        issues, _, stats = self.evaluate()
        self.assertEqual(issues, [], issues)
        self.assertEqual(stats["requirements"]["groups"], 3)

    def test_split_format_reaches_existing_gate_transition_entrypoint(self):
        self.split("PRODUCT_BRIEF.md", "01-requirements")
        self.split("REGRESSION_AND_RELEASE_REPORT.md", "03-test")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), mock.patch.object(vulcan, "save_session"):
            code = 0
            try:
                vulcan.cmd_prepare_transition(str(self.root))
            except SystemExit as exc:
                code = exc.code
        self.assertEqual(code, 0, output.getvalue())

    def test_seed_expansion_reads_linked_scenario_tables(self):
        original = vulcan.product_related_ids_for_seeds(str(self.root), ["SCN-001"])
        self.split("PRODUCT_BRIEF.md", "01-requirements")
        self.split("PRODUCT_CONTRACTS.md", "02-design/api")
        self.split("PRODUCT_TRACEABILITY.md", "02-traceability")
        self.split("REGRESSION_AND_RELEASE_REPORT.md", "03-test")
        self.assertEqual(set(vulcan.product_related_ids_for_seeds(str(self.root), ["SCN-001"])), set(original))

    def test_non_product_trace_validation_unchanged(self):
        for profile in ("audit", "poc"):
            self.write("session.json", json.dumps({"profile": profile, "current_gate": "gate4"}))
            self.write("vulcan.config.json", json.dumps({"delivery_profile": profile}))
            self.assertEqual(vulcan.validate_product_trace(str(self.root), "gate4"), ([], []))


if __name__ == "__main__":
    unittest.main()
