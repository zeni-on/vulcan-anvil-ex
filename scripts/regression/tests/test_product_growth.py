"""Synthetic document evolution, not application execution or QA evidence."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from vulcan_core.document_context import lookup_sections
from vulcan_core.product_documents import ProductDocuments

spec = importlib.util.spec_from_file_location("vulcan_product_growth_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class ProductGrowthTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.write("session.json", json.dumps({"profile": "product", "current_gate": "gate3"}))
        self.write("vulcan.config.json", json.dumps({"delivery_profile": "product", "workflow": {"enabled": False}}))
        self.feature("requests", (1, 2, 3))
        self.write("docs/product/PRODUCT_BRIEF.md", "# Product\nRequest board example.\n\n"
                   "| Scenario ID | Name | Related REQ |\n| --- | --- | --- |\n" +
                   "".join(f"| SCN-{i:03d} | Request action {i} | REQ-{i:03d} |\n" for i in (1, 2, 3)) +
                   "\n[requirements](../artifacts/01-requirements/requests.md)\n")
        self.write("docs/product/PRODUCT_ARCHITECTURE.md", "# Architecture\nLocal service and SQLite.\n"
                   "## Security Design Baseline\nServer access control at every entry.\n")
        self.write("docs/product/ADR_LOG.md", "# Decisions\nNo accepted decision in this synthetic example.\n")
        self.write("docs/product/PRODUCT_CONTRACTS.md", "# Contracts\nOwned contract sources.\n" + self.contract_links("requests") +
                   "\n| SEC ID | Policy | Verification |\n| --- | --- | --- |\n| SEC-001 | Server access control | SEC-REG-001 |\n")
        self.write("docs/product/PRODUCT_TRACEABILITY.md", "# Trace\nPlanned relationships only.\n\n"
                   "| Scenario ID | Related REQ | Scenario | Product Contract | Security | Implementation | Regression | Release Evidence | Status |\n"
                   "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" +
                   "".join(self.trace_row(i) for i in (1, 2, 3)))
        self.write("docs/product/REGRESSION_AND_RELEASE_REPORT.md", "# Report\nNo product tests executed.\n"
                   "## Regression Plan\n[plan](../artifacts/03-test/requests.md)\n"
                   "## Current Execution Results\n[results](../artifacts/04-review/v01/results.md)\n")
        self.write("docs/artifacts/04-review/v01/results.md", self.results((1, 2, 3)))

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def append(self, relative, text):
        self.write(relative, (self.root / relative).read_text(encoding="utf-8") + text)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*.md")}

    @staticmethod
    def trace_row(i):
        return (f"| SCN-{i:03d} | REQ-{i:03d} | Action {i} | API-{i:03d}, DATA-{i:03d}, UI-{i:03d} | SEC-001 | "
                f"Not implemented | REG-{i:03d}, SEC-REG-001 | None | Planned |\n")

    @staticmethod
    def contract_links(name):
        return "".join(f"[{kind}](../artifacts/02-design/{kind}/{name}.md)\n" for kind in ("api", "data", "screen"))

    def feature(self, name, ids):
        self.write(f"docs/artifacts/01-requirements/{name}.md", "# Feature requirements\n" + "".join(
            f"\n## REQ-{i:03d}\n### Conditions\nTitle maximum: 100 code points.\n### Acceptance Criteria\nReject 101 code points.\n"
            for i in ids))
        for directory, prefix in (("api", "API"), ("data", "DATA"), ("screen", "UI")):
            self.write(f"docs/artifacts/02-design/{directory}/{name}.md", f"# {directory} design\n"
                       "| ID | Contract |\n| --- | --- |\n" +
                       "".join(f"| {prefix}-{i:03d} | Title maximum: 100 code points. |\n" for i in ids))
        self.write(f"docs/artifacts/03-test/{name}.md", "# Regression Plan\n"
                   "| REG ID | Target | Input | Expected | Method |\n| --- | --- | --- | --- | --- |\n" +
                   "".join(f"| REG-{i:03d} | SCN-{i:03d}, REQ-{i:03d}, API-{i:03d} | 101 code points | Reject above 100 | Planned API test |\n" for i in ids) +
                   ("\n## Security Smoke Plan\n| SEC-REG ID | Target | Method |\n| --- | --- | --- |\n| SEC-REG-001 | SEC-001 | Planned access test |\n" if name == "requests" else ""))

    @staticmethod
    def results(ids):
        return ("# Current Execution Results\nNo execution; source baseline has not been tested.\n"
                "| REG ID | Result | Evidence |\n| --- | --- | --- |\n" +
                "".join(f"| REG-{i:03d} | Not Run | None |\n" for i in ids) +
                "| SEC-REG-001 | Not Run | None |\n")

    def add_comments(self):
        self.feature("comments", (4,))
        self.append("docs/product/PRODUCT_BRIEF.md", "\n| Scenario ID | Name | Related REQ |\n| --- | --- | --- |\n"
                    "| SCN-004 | Comments | REQ-004 |\n\n[comments](../artifacts/01-requirements/comments.md)\n")
        self.append("docs/product/PRODUCT_CONTRACTS.md", self.contract_links("comments"))
        self.append("docs/product/PRODUCT_TRACEABILITY.md", self.trace_row(4))
        self.write("docs/artifacts/04-review/v02/results.md", self.results((1, 2, 3, 4)))
        self.write("docs/product/REGRESSION_AND_RELEASE_REPORT.md", "# Report\nNo product tests executed.\n"
                   "## Regression Plan\n[requests](../artifacts/03-test/requests.md)\n[comments](../artifacts/03-test/comments.md)\n"
                   "## Current Execution Results\n[results](../artifacts/04-review/v02/results.md)\n"
                   "## History\n[previous](../artifacts/04-review/v01/results.md)\n")

    def evaluate(self, total):
        before = self.snapshot()
        issues, warnings = vulcan.validate_product_trace(str(self.root), "gate3")
        self.assertEqual(issues, [], issues)
        self.assertTrue(any("Gate 3 pending verification" in w for w in warnings), warnings)
        stats = vulcan.compute_product_stats(str(self.root))
        self.assertEqual(stats["product"]["requirements"]["total"], total)
        self.assertEqual(stats["product"]["scenarios"]["total"], total)
        self.assertEqual(stats["requirements"]["implemented"], 0)
        self.assertEqual((stats["tests"]["total"], stats["tests"]["pending"], stats["tests"]["passed"]), (total, total, 0))
        self.assertTrue(vulcan.validate_product_trace(str(self.root), "gate4")[0])
        self.assertEqual(len(list((self.root / "docs/product").glob("*.md"))), 6)
        self.assertEqual(self.snapshot(), before)
        return stats

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("-c", "user.name=Regression", "-c", "user.email=regression@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    @unittest.skipUnless(shutil.which("git"), "Git required for evolution history")
    def test_add_feature_then_edit_current_contract_without_growing_history_in_ledgers(self):
        self.git("init", "-q")
        self.evaluate(3)
        v01 = self.commit("v0.1 document baseline")
        plan = "docs/artifacts/03-test/requests.md"
        original_result = "docs/artifacts/04-review/v01/results.md"
        self.append(original_result, f"\nTest-definition reference (not an execution claim): {v01}:{plan}\n")
        self.commit("pin the original test-definition reference")
        baseline = self.snapshot()
        self.add_comments()
        self.evaluate(4)
        for p, content in baseline.items():
            if p.startswith("docs/artifacts/"):
                self.assertEqual((self.root / p).read_bytes(), content, p)
        v02 = self.commit("v0.2 add comments")
        before = self.snapshot()
        changed = [p for p in before if p.startswith("docs/artifacts/") and p.endswith("/requests.md")]
        for p in changed:
            self.write(p, before[p].decode().replace("100", "200").replace("101", "201"))
        self.evaluate(4)
        for p, content in before.items():
            if p not in changed:
                self.assertEqual((self.root / p).read_bytes(), content, p)
        v03 = self.commit("v0.3 update current title constraint")
        req = "docs/artifacts/01-requirements/requests.md"
        self.assertIn("maximum: 100", self.git("show", f"{v01}:{req}"))
        self.assertIn("maximum: 100", self.git("show", f"{v02}:{req}"))
        self.assertIn("maximum: 200", self.git("show", f"{v03}:{req}"))
        self.assertNotIn("maximum: 100", (self.root / req).read_text())
        self.assertIn(f"{v01}:{plan}", (self.root / original_result).read_text())
        old_plan = self.git("show", f"{v01}:{plan}")
        self.assertIn("101 code points | Reject above 100", old_plan)
        self.assertIn("201 code points | Reject above 200", (self.root / plan).read_text())
        self.assertEqual(set(self.git("diff", "--name-only", v02, v03).splitlines()), set(changed))
        lookup = lookup_sections(self.root, "REQ-001", documents=[req])
        text = "\n".join(s["excerpt"] for s in lookup["sections"])
        self.assertIn("maximum: 200", text)
        self.assertIn("Reject 201", text)
        self.assertEqual(lookup["omitted_sections_total"], 0)

    def test_missing_or_conflicting_new_detail_cannot_silently_pass(self):
        self.add_comments()
        target = self.root / "docs/artifacts/02-design/api/comments.md"
        original = target.read_text()
        target.unlink()
        self.assertTrue(any("reference" in issue for issue in vulcan.validate_product_trace(str(self.root), "gate3")[0]))
        self.write(target.relative_to(self.root), original)
        self.append("docs/product/PRODUCT_CONTRACTS.md", "\n| API ID | Contract |\n| --- | --- |\n| API-004 | Contradictory definition |\n")
        self.assertTrue(any("conflicting definitions API-004" in i for i in vulcan.validate_product_trace(str(self.root), "gate3")[0]))

    def test_old_synthetic_pass_never_supplies_new_scope_execution(self):
        old = "docs/artifacts/04-review/v01/results.md"
        self.write(old, self.results((1, 2, 3)).replace("Not Run", "Pass"))
        snapshot = (self.root / old).read_bytes()
        self.add_comments()
        self.evaluate(4)
        docs = ProductDocuments(self.root)
        self.assertNotIn(old, docs.diagnostics()["sources"])
        self.assertEqual((self.root / old).read_bytes(), snapshot)
        self.assertTrue(any("REG-004" in i for i in vulcan.validate_product_trace(str(self.root), "gate4")[0]))


if __name__ == "__main__":
    unittest.main()
