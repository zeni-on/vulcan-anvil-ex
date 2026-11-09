"""Synthetic Markdown targets; no live project data or process transitions."""

from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import test_product_readiness as fixtures
from test_product_process import vulcan
from vulcan_core import document_context as dc, product_readiness as checks
from vulcan_core.product_documents import ProductDocuments


class HTMLAnchorTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()

    def write(self, text, path="docs/product/detail.md"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
        return target

    def view(self, anchor, path="docs/product/detail.md"):
        reference = checks.local_reference(self.root, path + "#" + anchor, markdown=True)
        return checks._document_view(self.root, reference)

    def headings(self, anchor):
        _, sections, selected = self.view(anchor)
        return [s["heading"] for i, s in enumerate(sections) if i in selected]

    def test_explicit_id_after_heading_resolves_same_section_as_slug(self):
        path = self.write('# Product\n## REQ-009-10 Request receipt\n'
                          '<!-- vulcan:state=current -->\n<a id="req-009-10"></a>\n'
                          'Acknowledge a received request.\n### Detail\nKeep context.\n'
                          '## Other\nUnrelated.\n')
        before = path.read_bytes()
        self.assertEqual(self.headings("req-009-10"),
                         self.headings("req-009-10-request-receipt"))
        self.assertEqual(self.headings("req-009-10"), ["Product", "REQ-009-10 Request receipt", "Detail"])
        self.assertEqual(path.read_bytes(), before)

    def test_heading_slugs_and_duplicate_heading_suffixes_are_unchanged(self):
        text = '# Product\n## Same\n<a id="custom"></a>\nA\n## Same\nB\n'
        sections = dc._sections(text)
        self.assertEqual(dc._anchor_indices(sections), {"product": 0, "same": 1, "same-1": 2, "custom": 1})

    def test_empty_anchor_before_heading_targets_following_section(self):
        for gap in ("", "\n", "\n\n"):
            with self.subTest(gap=repr(gap)):
                self.write('# Product\n## Previous\nOld content.\n'
                           '<a id="selected"></a>\n' + gap +
                           '## Chosen\nCurrent content.\n## Other\nUnrelated.\n')
                self.assertEqual(self.headings("selected"), ["Product", "Chosen"])

    def test_anchor_before_first_heading_does_not_select_entire_document(self):
        self.write('<a id="selected"></a>\n\n# Chosen\nA\n# Other\nB\n')
        self.assertEqual(self.headings("selected"), ["(document introduction)", "Chosen"])

    def test_body_anchor_or_intervening_example_does_not_jump_to_next_heading(self):
        for content in ("Text.", "`example`", "    code", "```\ncode\n```", "<!-- note -->"):
            with self.subTest(content=content):
                self.write('# Product\n## Chosen\n<a id="selected"></a>\n' + content +
                           '\n## Other\nUnrelated.\n')
                self.assertEqual(self.headings("selected"), ["Product", "Chosen"])
        self.write('# Chosen\nText <a id="selected"></a> inline.\n# Other\nB\n')
        self.assertEqual(self.headings("selected"), ["Chosen"])

    def test_unicode_case_quotes_name_alias_and_crlf_positions(self):
        self.write("# Product\r\n## Chosen\r\n<a ID='선택-A'></a>\r\n"
                   "<a name=old-target></a>\r\nRetain this.\r\n## Other\r\nB\r\n")
        self.assertEqual(self.headings("%EC%84%A0%ED%83%9D-A"), ["Product", "Chosen"])
        self.assertEqual(self.headings("old-target"), ["Product", "Chosen"])
        with self.assertRaisesRegex(ValueError, "does not exist"):
            self.view("선택-a")

    def test_html_parser_handles_multiline_and_quoted_tag_attributes(self):
        self.write('# Product\n<a title="one > two"\n id="selected"></a>\n'
                   '## Chosen\nBody.\n## Other\nB\n')
        self.assertEqual(self.headings("selected"), ["Product", "Chosen"])

    def test_non_anchor_html_id_stays_with_its_containing_section(self):
        self.write('# Product\n## Chosen\n<span id="selected">A</span>\n## Other\nB\n')
        self.assertEqual(self.headings("selected"), ["Product", "Chosen"])

    def test_fake_anchors_in_code_comments_and_escaped_html_are_not_targets(self):
        anchor = '<a id="fake"></a>'
        for example in (f'```html\n{anchor}\n```', f'~~~\n{anchor}\n~~~',
                        f'`{anchor}`', f'``a ` {anchor}``', f'`start\n{anchor}`',
                        '    ' + anchor, '\t' + anchor, '<!-- ' + anchor + ' -->',
                        '<!--\n## Fake heading\n' + anchor + '\n-->',
                        '<pre>\n' + anchor + '\n</pre>', '<code>' + anchor + '</code>',
                        '<script>' + anchor + '</script>', '\\' + anchor,
                        '&lt;a id="fake"&gt;&lt;/a&gt;'):
            with self.subTest(example=example):
                self.write('# Product\n## Chosen\n' + example +
                           '\n<a id="real"></a>\nBody.\n## Other\nB\n')
                with self.assertRaisesRegex(ValueError, "does not exist"):
                    self.view("fake")
                self.assertEqual(self.headings("real"), ["Product", "Chosen"])
                self.assertNotIn("fake-heading", dc._anchor_indices(dc._sections(
                    (self.root / "docs/product/detail.md").read_text(encoding="utf-8"))))

    def test_duplicate_explicit_ids_or_heading_collision_are_ambiguous(self):
        for text in ('# Chosen\n<a id="duplicate"></a>\n<a id="duplicate"></a>\n',
                     '# Chosen\n<a id="duplicate"></a>\nA\n# Other\n<a id="duplicate"></a>\nB\n',
                     '# Duplicate\n<a id="duplicate"></a>\n',
                     '# Duplicate\nA\n# Other\n<a id="duplicate"></a>\nB\n',
                     '# Chosen\n<a id="duplicate" id="other"></a>\n'):
            with self.subTest(text=text):
                self.write(text)
                self.assertIsNone(dc._anchor_indices(dc._sections(text))["duplicate"])
                with self.assertRaisesRegex(ValueError, "ambiguous"):
                    self.view("duplicate")

    def test_id_and_legacy_name_on_same_element_are_one_target(self):
        self.write('# Chosen\n<a id="selected" name="selected"></a>\nBody.\n')
        self.assertEqual(self.headings("selected"), ["Chosen"])

    def test_before_and_after_anchors_do_not_promote_candidate_or_history(self):
        for state in ("candidate", "history"):
            for before in (True, False):
                with self.subTest(state=state, before=before):
                    marker = '<a id="selected"></a>\n'
                    self.write('# Product\n<!-- vulcan:state=current -->\n' +
                               (marker if before else '') + '## Chosen\n' +
                               f'<!-- vulcan:state={state} -->\n' +
                               ('' if before else marker) + 'Not current.\n## Other\nB\n')
                    with self.assertRaisesRegex(ValueError, "candidate/history"):
                        self.view("selected")

    def test_shared_conditions_remain_selected_without_unrelated_siblings(self):
        self.write('# Product\n## Chosen\n<a id="selected"></a>\nA\n'
                   '## Security\nProtect.\n### Rules\nApply globally.\n'
                   '## Other\nNot part of this scope.\n')
        self.assertEqual(self.headings("selected"), ["Product", "Chosen", "Security", "Rules"])

    def test_anchor_at_empty_peer_or_restricted_state_boundary_cannot_widen_scope(self):
        for state in ("current", "candidate", "history"):
            with self.subTest(state=state):
                self.write(f'# Product\n## Empty\n<!-- vulcan:state={state} -->\n'
                           '<a id="selected"></a>\n## Next\n<!-- vulcan:state=current -->\nBody.\n')
                with self.assertRaisesRegex(ValueError, "ambiguous"):
                    self.view("selected")
        self.write('# Product\n## Past\n<!-- vulcan:state=history -->\nOld content.\n'
                   '<a id="selected"></a>\n## Next\n<!-- vulcan:state=current -->\nBody.\n')
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.view("selected")

    def test_lookup_reports_missing_and_ambiguous_without_whole_file_fallback(self):
        for anchor, expected in (("absent", "missing_anchor"), ("duplicate", "ambiguous_anchor")):
            with self.subTest(anchor=anchor):
                self.write(f'# REQ-001\n[rule](detail.md#{anchor})\n', "docs/product/feature.md")
                self.write('# Chosen\n<a id="duplicate"></a>\nA\n'
                           '# Other\n<a id="duplicate"></a>\nB\n')
                result = dc.lookup_sections(self.root, "REQ-001", documents=["docs/product/feature.md"])
                self.assertEqual(result["references"][0]["status"], expected)
                self.assertFalse(result["references"][0]["followed"])
                self.assertEqual([s["heading"] for s in result["sections"]], ["REQ-001"])

    def test_lookup_preserves_linked_candidate_state_and_shared_context(self):
        self.write('# REQ-001\n[rule](detail.md#selected)\n', "docs/product/feature.md")
        self.write('# Product\n## Chosen\n<!-- vulcan:state=candidate -->\n'
                   '<a id="selected"></a>\nProposal.\n## Security\nProtect.\n## Other\nB\n')
        result = dc.lookup_sections(self.root, "REQ-001", documents=["docs/product/feature.md"])
        self.assertFalse(result["authority"])
        self.assertEqual(next(s["state"] for s in result["sections"] if s["heading"] == "Chosen"), "candidate")
        self.assertIn("Security", [s["heading"] for s in result["sections"]])
        self.assertNotIn("Other", [s["heading"] for s in result["sections"]])

    def test_product_documents_follow_only_current_target_and_reject_ambiguity(self):
        self.write('# Brief\n[requirements](detail.md#selected)\n', "docs/product/PRODUCT_BRIEF.md")
        body = '# Chosen\n<a id="selected"></a>\n| ID | Requirement |\n| --- | --- |\n| REQ-001 | A |\n'
        self.write(body + '# Other\n| ID | Requirement |\n| --- | --- |\n| REQ-002 | B |\n')
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertEqual(docs.issues, [])
        self.assertEqual(vulcan.product_requirement_ids(docs), {"REQ-001"})
        self.write(body + '<a id="selected"></a>\n')
        docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
        self.assertTrue(any("anchor ambiguous" in issue for issue in docs.issues), docs.issues)
        for state in ("candidate", "history"):
            self.write(body.replace('# Chosen\n', f'# Chosen\n<!-- vulcan:state={state} -->\n'))
            docs = ProductDocuments(self.root, ["PRODUCT_BRIEF.md"])
            self.assertEqual(vulcan.product_requirement_ids(docs), set())

    def test_readiness_binds_html_links_but_keeps_missing_scope_and_shared_checks(self):
        fixture = fixtures.ScopedReadinessTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.write("docs/contracts.md", fixtures.CONTRACT.replace('## Resubmit',
                      '## Resubmit\n<a id="resubmit-stable"></a>\n[rule](rules.md#stable)'))
        fixture.write("docs/rules.md", '# Rules\n## Selected\n<a id="stable"></a>\nUse the owner.\n'
                      '## Other\n<a id="other-stable"></a>\nUnrelated.\n')
        fixture.scope["contracts"] = [fixture.ref("docs/contracts.md#resubmit-stable")]
        fixture.assert_blocked(fixture.collect(), "unbound_reference")
        fixture.scope["contracts"].append(fixture.ref("docs/rules.md#other-stable"))
        fixture.assert_blocked(fixture.collect(), "unbound_reference")
        fixture.scope["contracts"][-1] = fixture.ref("docs/rules.md#stable")
        self.assertEqual(fixture.collect()["status"], "ready")
        before = deepcopy(fixture.scope)
        text = (fixture.root / "docs/contracts.md").read_text(encoding="utf-8")
        fixture.write("docs/contracts.md", text.replace("Only the owner can resubmit.", "TBD"))
        fixture.assert_blocked(fixture.collect(), "revision changed")
        fixture.scope["contracts"][0] = fixture.ref("docs/contracts.md#resubmit-stable")
        fixture.assert_blocked(fixture.collect(), "SEC-001 needs a substantive definition")
        self.assertEqual(before["related_ids"], fixture.scope["related_ids"])


if __name__ == "__main__":
    unittest.main()
