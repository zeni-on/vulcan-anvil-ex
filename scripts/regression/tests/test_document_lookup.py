"""Synthetic legacy/split/mixed contracts, without private project content."""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from vulcan_core import document_context as dc


class DocumentLookupTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        provenance = mock.patch.object(dc, "_git", return_value={"observed_head": None, "worktree_state": "unknown"})
        provenance.start()
        self.addCleanup(provenance.stop)

    def write(self, path, body):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return target

    def lookup(self, seed="REQ-101", **kwargs):
        return dc.lookup_sections(self.root, seed, **kwargs)

    def test_legacy_split_mixed_preserve_contracts_and_never_write(self):
        required = "REQ-101 must retain the selected locale."
        constraint = "An absent locale uses the configured fallback."
        test = "T-101: input locale omitted; expect the configured fallback."
        for layout in ("legacy", "split", "mixed"):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                content = {
                    "docs/product/PRODUCT_CONTRACTS.md": "# Locale\n<!-- vulcan:state=current -->\n" + required + "\n" + constraint + "\n" + test + "\n"
                } if layout == "legacy" else {
                    "docs/artifacts/01-requirements/locale.md": "# Locale\n<!-- vulcan:state=current -->\n" + required + "\n[conditions](conditions.md)\n[verification](../03-test/locale.md)\n",
                    "docs/artifacts/01-requirements/conditions.md": "# Applicability\n<!-- vulcan:state=current -->\n" + constraint + "\n",
                    "docs/artifacts/03-test/locale.md": "# Verification\n<!-- vulcan:state=current -->\n" + test + "\n",
                }
                if layout == "mixed":
                    content["docs/product/PRODUCT_CONTRACTS.md"] = "# Index\n[Locale requirement](../artifacts/01-requirements/locale.md)\n"
                for path, body in content.items():
                    target = root / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(body, encoding="utf-8")
                before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                result = dc.lookup_sections(root, "REQ-101")
                text = "\n".join(s["excerpt"] for s in result["sections"])
                for obligation in (required, constraint, test):
                    self.assertEqual(text.count(obligation), 1)
                self.assertFalse(result["authority"])
                self.assertFalse(result["incomplete"], result["warnings"])
                after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
                for section in result["sections"]:
                    raw = before[Path(section["path"])]
                    self.assertEqual(section["document_sha256"], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(section["excerpt"], "".join(raw.decode().splitlines(keepends=True)[section["start_line"]-1:section["end_line"]]))

    def test_test_definition_is_discovered_without_explicit_document(self):
        self.write("docs/artifacts/03-test/locale.md", "# T-101\n<!-- vulcan:state=current -->\ninput -> expected\n")
        result = self.lookup("T-101")
        self.assertEqual(result["sections"][0]["heading"], "T-101")

    def test_anchor_subtree_and_ancestors_without_siblings(self):
        self.write("docs/product/feature.md", "# REQ-101\n[condition](conditions.md#selected)\n")
        self.write("docs/product/conditions.md", "# Rules\nScope\n## Selected\ncondition\n### Child\nexception\n## Unrelated\ndo not include\n")
        result = self.lookup()
        headings = {s["heading"] for s in result["sections"]}
        self.assertEqual(headings, {"REQ-101", "Rules", "Selected", "Child"})
        self.assertTrue(result["references"][0]["followed"])

    def test_linked_anchor_also_includes_shared_security_constraints(self):
        self.write("docs/product/feature.md", "# REQ-101\n<!-- vulcan:state=current -->\n[rule](rules.md#selected)\n")
        self.write("docs/product/rules.md", "# Rules\n<!-- vulcan:state=current -->\n## Selected\nSelected rule\n## Security\nRestriction\n### Exception\nConstraint detail\n## Other\nUnrelated\n")
        for kwargs in ({}, {"documents": ["docs/product/feature.md"]}):
            with self.subTest(kwargs=kwargs):
                result = self.lookup(**kwargs)
                self.assertEqual({s["heading"] for s in result["sections"]}, {"REQ-101", "Rules", "Selected", "Security", "Exception"})
                self.assertTrue(result["references"][0]["followed"])
                self.assertFalse(result["incomplete"], result["warnings"])

    def test_remote_links_cannot_hide_local_dependency_after_limit(self):
        self.write("docs/product/a.md", "# REQ-101\n<!-- vulcan:state=current -->\n" + "\n".join(f"[web](https://example.invalid/{i}.md)" for i in range(70)) + "\n[mandatory](missing.md)\n")
        result = self.lookup()
        self.assertEqual(len(result["references"]), 1)
        self.assertEqual(result["references"][0]["status"], "missing_or_unsafe")
        self.assertTrue(result["incomplete"])

    def test_balanced_and_escaped_parentheses_in_link_destinations(self):
        for target in ("rules(v2).md", r"rules\(v2\).md", "rules%28v2%29.md"):
            with self.subTest(target=target):
                self.write("docs/product/a.md", f"# REQ-101\n[mandatory]({target}#scope)\n")
                self.write("docs/product/rules(v2).md", "# Scope\nrestriction\n")
                result = self.lookup()
                self.assertTrue(result["references"][0]["followed"])

    def test_conflicting_reference_definitions_do_not_choose_a_winner(self):
        self.write("docs/product/a.md", "# REQ-101\n<!-- vulcan:state=current -->\n[rule][r]\n[r]: b.md\n[r]: c.md\n")
        self.write("docs/product/b.md", "# B\nAllow\n")
        self.write("docs/product/c.md", "# C\nDeny\n")
        result = self.lookup()
        self.assertEqual(result["references"][0]["status"], "ambiguous_definition")
        self.assertFalse(result["references"][0]["followed"])
        self.assertEqual(len(result["sections"]), 1)
        self.assertTrue(result["incomplete"])

    def test_direct_reference_has_budget_priority_over_global_heuristic_links(self):
        self.write("docs/product/a-policy.md", "# Security\n" + "\n".join(f"[unused](missing-{i}.md)" for i in range(100)))
        self.write("docs/product/z-feature.md", "# REQ-101\n[required](condition.md)\n")
        self.write("docs/product/condition.md", "# Condition\nRetained\n")
        result = self.lookup()
        self.assertEqual(result["references"][0]["target"], "condition.md")
        self.assertTrue(result["references"][0]["followed"])

    def test_reference_style_uses_definition_outside_selected_section(self):
        self.write("docs/product/feature.md", "# REQ-101\nSee [conditions][rules].\n# References\n[rules]: conditions.md#scope\n[unused]: private/nope.md\n")
        self.write("docs/product/conditions.md", "# Scope\nretained\n")
        result = self.lookup()
        self.assertEqual(len(result["references"]), 1)
        self.assertTrue(result["references"][0]["followed"])

    def test_missing_reference_definition_is_reported(self):
        self.write("docs/product/feature.md", "# REQ-101\nSee [conditions][absent].\n")
        self.assertEqual(self.lookup()["references"][0]["status"], "missing_definition")

    def test_fenced_and_inline_code_links_are_not_followed(self):
        self.write("docs/product/feature.md", "# REQ-101\n`[example](private/a.md)`\n```md\n[x](private/b.md)\n```\n![image](private/c.md)\n")
        self.assertEqual(self.lookup()["references"], [])

    def test_private_reviews_outside_roots_and_network_not_fetched(self):
        self.write("docs/product/feature.md", "# REQ-101\n[p](private/x.md)\n[r](../reviews/x.md)\n[n](../../notes.md)\n[w](https://example.invalid/x.md)\n")
        blocked = ["docs/product/private/x.md", "docs/reviews/x.md", "notes.md"]
        for path in blocked:
            self.write(path, "# Not for automatic lookup\nsecret\n")
        original = Path.open
        def guarded(path, *args, **kwargs):
            self.assertNotIn(path.relative_to(self.root).as_posix(), blocked)
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "open", guarded):
            result = self.lookup()
        self.assertEqual([r["status"] for r in result["references"]], ["outside_lookup_scope"] * 3)
        self.assertTrue(result["incomplete"])

    def test_explicit_extra_document_can_supply_linked_pending_obligation(self):
        self.write("docs/product/feature.md", "# REQ-101\n[pending](../artifacts/04-review/pending.md#follow-up)\n")
        self.write("docs/artifacts/04-review/pending.md", "# Follow-up\n<!-- vulcan:state=history -->\nPending until storage support ships.\n")
        result = self.lookup(documents=["docs/product/feature.md", "docs/artifacts/04-review/pending.md"])
        pending = next(s for s in result["sections"] if s["heading"] == "Follow-up")
        self.assertEqual(pending["state"], "history")
        self.assertIn("Pending", pending["excerpt"])

    def test_linked_current_candidate_history_and_unclassified_not_promoted(self):
        self.write("docs/product/feature.md", "# REQ-101\n<!-- vulcan:state=current -->\n[constraints](conditions.md)\n")
        self.write("docs/product/conditions.md", "# Candidate\n<!-- vulcan:state=candidate -->\nproposal\n# History\n<!-- vulcan:state=history -->\nprevious\n# Unknown\nreview first\n")
        result = self.lookup()
        states = {s["heading"]: s["state"] for s in result["sections"]}
        self.assertEqual(states, {"REQ-101": "current", "Candidate": "candidate", "History": "history", "Unknown": "unclassified"})
        self.assertTrue(any("Unclassified linked" in w for w in result["warnings"]))

    def test_conflicting_linked_contracts_not_silently_resolved(self):
        self.write("docs/product/feature.md", "# REQ-101\n<!-- vulcan:state=current -->\n[a](a.md) [b](b.md)\n")
        self.write("docs/product/a.md", "# REQ-101\n<!-- vulcan:state=current -->\nAllow\n")
        self.write("docs/product/b.md", "# REQ-101\n<!-- vulcan:state=current -->\nDeny\n")
        result = self.lookup(documents=["docs/product/feature.md"])
        self.assertTrue(any("Multiple current" in w for w in result["warnings"]))
        self.assertEqual(len(result["sections"]), 3)

    def test_cycle_and_repeated_targets_are_deduplicated(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md) [again](b.md)\n")
        self.write("docs/product/b.md", "# Constraint\n[a](a.md)\n")
        result = self.lookup(documents=["docs/product/a.md"])
        self.assertEqual(len(result["sections"]), 2)
        self.assertEqual(len(result["references"]), 2)
        self.assertTrue(all(r["followed"] for r in result["references"]))
        self.assertEqual(result["references"][1]["status"], "already_selected")

    def test_two_hop_limit_even_when_sources_were_scanned(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md)\n")
        self.write("docs/product/b.md", "# B\n[c](c.md)\n")
        self.write("docs/product/c.md", "# C\n[d](d.md)\n")
        self.write("docs/product/d.md", "# D\nnot followed\n")
        for kwargs in ({}, {"documents": ["docs/product/a.md"]}):
            with self.subTest(kwargs=kwargs):
                result = self.lookup(**kwargs)
                self.assertEqual({s["heading"] for s in result["sections"]}, {"REQ-101", "B", "C"})
                self.assertEqual(result["references"][-1]["status"], "depth_limit")

    def test_link_document_limit(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md) [c](c.md)\n")
        self.write("docs/product/b.md", "# B\nretained\n")
        self.write("docs/product/c.md", "# C\nnot read\n")
        with mock.patch.object(dc, "MAX_LINK_DOCUMENTS", 1):
            result = self.lookup(documents=["docs/product/a.md"])
        self.assertEqual(result["references"][-1]["status"], "document_limit")

    def test_total_document_limit_also_bounds_link_reads(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md)\n")
        self.write("docs/product/b.md", "# B\nnot read\n")
        with mock.patch.object(dc, "MAX_DOCUMENTS", 1):
            result = self.lookup(documents=["docs/product/a.md"])
        self.assertEqual(result["references"][0]["status"], "document_limit")

    def test_link_count_budget_is_reported(self):
        self.write("docs/product/a.md", "# REQ-101\n" + "\n".join(f"[x](missing-{i}.md)" for i in range(100)))
        result = self.lookup()
        self.assertEqual(len(result["references"]), dc.MAX_LINKS)
        self.assertTrue(any("link limit" in w for w in result["warnings"]))
        self.assertLessEqual(len(result["warnings"]), 48)

    def test_output_budget_marks_target_partial_even_if_read(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md)\n")
        self.write("docs/product/b.md", "# Conditions\n" + "condition " * 300 + "\n")
        result = self.lookup(max_chars=100)
        link = result["references"][0]
        self.assertEqual(link["status"], "output_limit")
        self.assertFalse(link["followed"])
        self.assertEqual(link["included_sections"], 0)
        self.assertTrue(result["incomplete"])

    def test_anchor_and_unicode_paths_and_duplicate_headings(self):
        self.write("docs/product/a.md", "# REQ-101\n[x](<%ED%95%9C%EA%B8%80 file.md#scope-1>)\n")
        self.write("docs/product/\ud55c\uae00 file.md", "# Scope\nfirst\n# Scope\nsecond\n")
        result = self.lookup()
        self.assertTrue(result["references"][0]["followed"])
        self.assertIn("second", result["sections"][1]["excerpt"])
        self.assertNotIn("first", "".join(s["excerpt"] for s in result["sections"]))

    def test_same_document_fragment_follows_only_selected_target(self):
        self.write("docs/product/a.md", "# REQ-101\n[x](#conditions)\n# Conditions\nrequired\n# Other\nnot required\n")
        result = self.lookup()
        self.assertEqual([s["heading"] for s in result["sections"]], ["REQ-101", "Conditions"])

    def test_source_revision_query_not_treated_as_current_file(self):
        self.write("docs/product/a.md", "# REQ-101\n[x](b.md?revision=old)\n")
        self.write("docs/product/b.md", "# New version\ncurrent\n")
        result = self.lookup()
        self.assertEqual(result["references"][0]["status"], "unsupported_query")
        self.assertFalse(result["references"][0]["followed"])

    def test_oversized_and_invalid_utf8_targets_report_unreadable(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md) [c](c.md)\n")
        self.write("docs/product/b.md", "# B\n" + "x" * dc.MAX_BYTES)
        self.write("docs/product/c.md", "temporary").write_bytes(b"\xff\xfe")
        result = self.lookup(documents=["docs/product/a.md"])
        self.assertEqual([r["status"] for r in result["references"]], ["unreadable", "unreadable"])

    def test_absolute_encoded_traversal_and_symlink_paths_not_read(self):
        self.write("docs/product/a.md", "# REQ-101\n[escape](%2e%2e/%2e%2e/%2e%2e/x.md)\n[absolute](%2fetc%2fx.md)\n[drive](C%3A/x.md)\n[linked](linked.md)\n")
        self.write("docs/product/linked.md", "# Secret\nno read\n")
        original_linked = dc._linked
        with mock.patch.object(dc, "_linked", side_effect=lambda p: p.name == "linked.md" or original_linked(p)):
            result = self.lookup(documents=["docs/product/a.md"])
        self.assertEqual(len(result["sections"]), 1)
        self.assertEqual([r["status"] for r in result["references"]], ["missing_or_unsafe"] * 4)

    def test_no_exact_match_does_not_crawl_unrelated_shared_links(self):
        self.write("docs/product/a.md", "# Security\n[b](b.md)\n")
        self.write("docs/product/b.md", "# B\nno relevance\n")
        result = self.lookup()
        self.assertEqual(result["references"], [])
        self.assertEqual(result["sections"], [])

    def test_linked_seed_found_during_explicit_lookup(self):
        self.write("docs/product/a.md", "# REQ-101\n[b](b.md)\n")
        self.write("docs/product/b.md", "# T-101\nverification\n")
        result = self.lookup("REQ-101,T-101", documents=["docs/product/a.md"])
        self.assertFalse(any("No exact match" in w for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
