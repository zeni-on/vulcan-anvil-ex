import hashlib
import importlib.util
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
from vulcan_core import document_context as dc

spec = importlib.util.spec_from_file_location("vulcan_document_context_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class DocumentContextTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="section fixture ")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def write(self, text, name="docs/product/contracts.md"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def lookup(self, seeds="API-001", **kwargs):
        return dc.lookup_sections(self.root, seeds, **kwargs)

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(ROOT / "vulcan.py"), "trace-context",
                               "--project-dir", str(self.root), *args], cwd=self.root,
                              capture_output=True, encoding="utf-8")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Fixture",
                               "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                               "-c", "core.hooksPath=/dev/null", "-c", "core.autocrlf=false", *args],
                              capture_output=True, check=True).stdout.decode().strip()

    def test_missing_graph_and_no_authority(self):
        self.write("# API-001\nContract\n")
        result = self.lookup()
        self.assertEqual(result["kind"], "derived_reference")
        self.assertFalse(result["authority"])
        self.assertEqual(result["sections"][0]["git"]["worktree_state"], "unknown")
        self.assertFalse((self.root / "session.json").exists())

    def test_exact_multi_seed_and_table_ids(self):
        self.write("# Wrong\nAPI-0010 REQ-001-01\n# Table\n| API-001 | UI-002 |\n")
        result = self.lookup("API-001,UI-002,REQ-001")
        self.assertEqual([s["heading"] for s in result["sections"]], ["Table"])
        self.assertEqual(result["sections"][0]["matching_ids"], ["API-001", "UI-002"])
        self.assertTrue(any("No exact match: REQ-001" in w for w in result["warnings"]))

    def test_line_hash_and_unicode(self):
        text = "# \uacc4\uc57d\r\nIntroduction\r\n## API-001\r\n\ud55c\uae00\r\n## Other\r\n"
        path = self.write(text, "docs/product/\ud55c\uae00 \uacc4\uc57d.md")
        result = self.lookup()
        item = next(s for s in result["sections"] if s["matching_ids"])
        self.assertEqual((item["start_line"], item["end_line"]), (3, 4))
        self.assertEqual(item["document_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(item["excerpt"], "".join(text.splitlines(keepends=True)[2:4]))
        self.assertEqual(item["ancestry"], ["\uacc4\uc57d"])

    def test_state_inheritance_override_and_legacy(self):
        self.write("# Root\n<!-- vulcan:state=current -->\n## API-001\nDesigned\n"
                   "### Candidate\n<!-- vulcan:state=candidate -->\nchange\n"
                   "### History\n<!-- vulcan:state=history -->\nold\n"
                   "# Legacy API-002 Delta 2099\nDesigned\n")
        result = self.lookup("API-001,API-002")
        states = {s["heading"]: s["state"] for s in result["sections"]}
        self.assertEqual(states["API-001"], "current")
        self.assertEqual(states["Candidate"], "candidate")
        self.assertEqual(states["History"], "history")
        self.assertEqual(states["Legacy API-002 Delta 2099"], "unclassified")

    def test_fenced_headings_and_markers_ignored_but_ids_searchable(self):
        self.write("# API-001\n```markdown\n# API-002\n<!-- vulcan:state=current -->\n```\n"
                   "~~~\n# API-003\n<!-- vulcan:state=history -->\n~~~\n")
        result = self.lookup("API-001,API-002,API-003")
        self.assertEqual(len(result["sections"]), 1)
        self.assertEqual(result["sections"][0]["state"], "unclassified")
        self.assertEqual(result["sections"][0]["matching_ids"], ["API-001", "API-002", "API-003"])
        self.assertIn("# API-002", result["sections"][0]["excerpt"])

    def test_shared_constraints_across_documents_and_descendants(self):
        self.write("# Contracts\nIntroduction\n## API-001\nroute\n### Response\nbody\n")
        self.write("# Contract Policy\nGlobal\n## Security\nSEC-001\n### Rules\nProtect\n"
                   "## Auth\nAuthorize\n## Error\nRedact\n## Compatibility\nKeep\n",
                   "docs/artifacts/02-design/policy.md")
        result = self.lookup()
        sections = {s["heading"]: s for s in result["sections"]}
        for title in ("Contract Policy", "Security", "Rules", "Auth", "Error", "Compatibility"):
            self.assertIn("shared", sections[title]["reasons"])
        self.assertIn("ancestor", sections["Contracts"]["reasons"])
        self.assertIn("direct_descendant", sections["Response"]["reasons"])

    def test_inline_marker_example_is_not_lifecycle_state(self):
        self.write("# API-001\nUse `<!-- vulcan:state=current -->` as an example.\n"
                   "> <!-- vulcan:state=history -->\n")
        result = self.lookup()
        self.assertEqual(result["sections"][0]["state"], "unclassified")
        self.assertTrue(result["incomplete"])

    def test_indented_code_marker_is_not_lifecycle_state(self):
        for indent in ("    ", "\t", " \t"):
            with self.subTest(indent=indent):
                self.write("# API-001\n\n" + indent + "<!-- vulcan:state=current -->\n")
                result = self.lookup()
                self.assertEqual(result["sections"][0]["state"], "unclassified")
                self.assertTrue(result["incomplete"])

    def test_shared_constraints_not_displaced_by_many_descendants(self):
        self.write("# API-001\nroute\n" + "".join(f"## Detail {i}\nbody\n" for i in range(20)))
        self.write("# Security\nRequire authorization\n## Error\nRedact secrets\n",
                   "docs/product/security.md")
        result = self.lookup()
        headings = {section["heading"] for section in result["sections"]}
        self.assertTrue({"API-001", "Security", "Error"}.issubset(headings))
        self.assertTrue(result["incomplete"])

    def test_multiple_current_requires_review_no_winner(self):
        self.write("# API-001 A\n<!-- vulcan:state=current -->\n# API-001 B\n<!-- vulcan:state=current -->\n")
        result = self.lookup()
        self.assertEqual(len(result["sections"]), 2)
        self.assertTrue(any("Multiple current" in w for w in result["warnings"]))

    def test_conflicting_markers(self):
        self.write("# API-001\n<!-- vulcan:state=current -->\n<!-- vulcan:state=history -->\n")
        result = self.lookup()
        self.assertTrue(result["sections"][0]["state_conflict"])
        self.assertEqual(result["sections"][0]["state"], "unclassified")
        self.assertTrue(result["incomplete"])

    def test_whole_sections_omitted_not_clipped(self):
        self.write("# API-001\n" + "contract " * 200 + "\n")
        result = self.lookup(max_chars=100)
        self.assertEqual(result["sections"], [])
        self.assertEqual(result["omitted_sections"][0]["start_line"], 1)
        self.assertTrue(result["truncated"])
        self.assertTrue(result["incomplete"])

    def test_twelve_section_limit(self):
        self.write("".join(f"# API-001 Part {i}\ntext\n" for i in range(20)))
        result = self.lookup()
        self.assertEqual(len(result["sections"]), 12)
        self.assertEqual(len(result["omitted_sections"]), 8)
        self.assertLessEqual(result["excerpt_chars"], 12000)

    def test_links_reported_not_crawled(self):
        self.write("# API-001\n[detail](detail.md#part) [missing](missing.md) [web](https://example.invalid/x.md)\n")
        self.write("# Linked only\nnot included\n", "docs/product/detail.md")
        result = self.lookup()
        links = result["sections"][0]["source_links"]
        self.assertEqual([x["status"] for x in links], ["available", "missing_or_unsafe"])
        self.assertTrue(all(not x["followed"] for x in links))
        self.assertEqual(len(result["sections"]), 1)
        self.assertTrue(result["incomplete"])

    def test_only_permitted_default_roots(self):
        for name in ("docs/templates/a.md", "docs/runs/a.md", "docs/ref-docs/a.md",
                     "docs/product/private/a.md", "docs/artifacts/04-review/a.md"):
            self.write("# API-001\nsecret\n", name)
        self.assertEqual(self.lookup()["sections"], [])

    def test_explicit_documents_are_relative_regular_markdown(self):
        self.write("# API-001\n", "notes/a.md")
        self.assertEqual(len(self.lookup(documents=["notes/a.md"])["sections"]), 1)
        for name in ("../a.md", "notes/../notes/a.md", str(self.root / "notes/a.md"),
                     "C:a.md", "C:/a.md", "\\\\server\\a.md", "/a.md", "notes", "missing.md"):
            with self.subTest(name=name), self.assertRaises((ValueError, OSError)):
                self.lookup(documents=[name])

    def test_all_explicit_paths_validated_before_read(self):
        self.write("# API-001\n")
        with mock.patch.object(Path, "open", side_effect=AssertionError("source read")):
            with self.assertRaises(ValueError):
                self.lookup(documents=["docs/product/contracts.md", "../escape.md"])

    def test_symlink_rejected(self):
        source = self.write("# API-001\n")
        link = self.root / "linked.md"
        try:
            link.symlink_to(source)
        except OSError:
            self.skipTest("OS does not permit symlink creation")
        with self.assertRaises(ValueError):
            self.lookup(documents=["linked.md"])

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junction_rejected(self):
        self.write("# API-001\n")
        link = self.root / "junction"
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(self.root / "docs/product")],
                       check=True, capture_output=True)
        self.addCleanup(lambda: os.rmdir(link))
        with self.assertRaises(ValueError):
            self.lookup(documents=["junction/contracts.md"])

    def test_git_clean_dirty_and_untracked(self):
        self.write("# API-001\n")
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "fixture")
        first = self.lookup()["sections"][0]["git"]
        self.assertEqual(first["observed_head"], self.git("rev-parse", "HEAD"))
        self.assertEqual(first["worktree_state"], "clean")
        self.write("# API-001\nchanged\n")
        self.assertEqual(self.lookup()["sections"][0]["git"]["worktree_state"], "dirty")
        self.write("# API-002\n", "docs/product/new.md")
        self.assertEqual(self.lookup("API-002")["sections"][0]["git"]["worktree_state"], "dirty")

    def test_git_failure_optional(self):
        self.write("# API-001\n")
        with mock.patch.object(dc.subprocess, "run", side_effect=FileNotFoundError):
            self.assertEqual(self.lookup()["sections"][0]["git"]["worktree_state"], "unknown")

    def test_git_environment_cannot_point_document_to_another_repository(self):
        self.write("# API-001\n")
        self.git("init", "--quiet")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "fixture")
        with tempfile.TemporaryDirectory() as other:
            project = Path(other).resolve()
            source = project / "docs/product/contracts.md"
            source.parent.mkdir(parents=True)
            source.write_text("# API-001\nUnrelated document\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"GIT_DIR": str(self.root / ".git"),
                                              "GIT_WORK_TREE": str(self.root)}):
                provenance = dc.lookup_sections(project, "API-001")["sections"][0]["git"]
            self.assertEqual(provenance, {"observed_head": None, "worktree_state": "unknown"})

    def test_nested_directory_does_not_claim_parent_repository_identity(self):
        self.git("init", "--quiet")
        self.write("# API-001\n", "nested/docs/product/contracts.md")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "fixture")
        provenance = dc.lookup_sections(self.root / "nested", "API-001")["sections"][0]["git"]
        self.assertEqual(provenance, {"observed_head": None, "worktree_state": "unknown"})

    def test_cli_json_yaml_and_repeat_documents(self):
        self.write("# API-001\n")
        self.write("# UI-002\n", "notes.md")
        for emit in ("json", "yaml"):
            result = self.cli("--id", "API-001,UI-002", "--sections", "--emit", emit,
                              "--document", "docs/product/contracts.md", "--document", "notes.md")
            self.assertEqual(result.returncode, 0, result.stderr)
            # JSON serialization is valid YAML 1.2 and requires no optional package.
            self.assertEqual(len(json.loads(result.stdout)["sections"]), 2)

    def test_cli_errors(self):
        for args in (("--max-chars", "0"), ("--max-chars", "100001"), ("--document", "../a.md")):
            result = self.cli("--id", "API-001", "--sections", *args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("trace-context:", result.stderr)

    def test_old_graph_mode_single_seed_unchanged(self):
        direct = vulcan.trace_context(self.root, "API-001")
        result = self.cli("--id", "API-001", "--emit", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), direct)
        self.assertNotIn("sections", direct)

    def test_existing_graph_fixture(self):
        # Locate only an existing public trace fixture, without generating project artifacts.
        traces = sorted((ROOT / "scripts/regression/fixtures").glob("*/docs/artifacts/02-traceability/*.md"))
        self.assertTrue(traces, "Expected an existing trace fixture")
        fixture = traces[0].parents[3]
        result = vulcan.trace_context(fixture, "API-001", direction="both")
        self.assertIn("API-001", result["related_ids"])
        self.assertIn("API-001", result["target_contracts"]["api"])
        self.assertTrue(result["nodes"])

    def test_metadata_lookup_optional_and_short(self):
        self.assertEqual(vulcan.format_trace_context_metadata({"seeds": []}), "")
        info = vulcan.trace_context_run_enrichment(self.root, "API-001,UI-002")
        text = vulcan.format_trace_context_metadata(info)
        self.assertIn("section_lookup:", text)
        self.assertIn("--id API-001,UI-002 --sections --emit json", text)
        self.assertNotIn("excerpt", text)

    def test_input_limits_and_oversize_document(self):
        for seeds in ("", "API-001;whoami", ",".join(f"API-{i}" for i in range(33))):
            with self.assertRaises(ValueError):
                self.lookup(seeds)
        self.write("# API-001\n" + "x" * dc.MAX_BYTES)
        result = self.lookup()
        self.assertEqual(result["sections"], [])
        self.assertTrue(any("Oversized" in w for w in result["warnings"]))

    def test_setext_heading(self):
        self.write("Root\n====\nIntroduction\n\nAPI-001\n-------\ncontract\n")
        result = self.lookup()
        item = next(s for s in result["sections"] if s["matching_ids"])
        self.assertEqual(item["heading"], "API-001")
        self.assertEqual((item["start_line"], item["end_line"]), (5, 7))

    def test_fenced_yaml_contract_id_search(self):
        self.write("# Interface\n<!-- vulcan:state=current -->\n```yaml\nprogram: PGM-050\n"
                   "# fake heading\n<!-- vulcan:state=history -->\n```\n")
        result = self.lookup("PGM-050")
        self.assertEqual(len(result["sections"]), 1)
        self.assertEqual(result["sections"][0]["heading"], "Interface")
        self.assertEqual(result["sections"][0]["state"], "current")

    def test_direct_matches_precede_shared_and_omissions_bounded(self):
        self.write("# Policy\nIntro\n" + "".join(f"## Security {i}\nconstraint\n" for i in range(100)),
                   "docs/product/a-policy.md")
        self.write("# Root\nIntro\n## Delta\nScope\n### PGM-050\n"
                   "<!-- vulcan:state=candidate -->\nContract\n", "docs/product/z-contract.md")
        result = self.lookup("PGM-050")
        self.assertEqual(result["sections"][0]["heading"], "PGM-050")
        self.assertEqual(result["sections"][0]["state"], "candidate")
        self.assertEqual([s["heading"] for s in result["sections"][1:3]], ["Root", "Delta"])
        self.assertEqual(result["omitted_sections_total"], 92)
        self.assertEqual(result["omitted_sections_listed"], 12)
        self.assertEqual(result["omitted_sections_remaining"], 80)
        self.assertTrue(any("constraint sections" in w for w in result["warnings"]))

    def test_unclassified_direct_explicit_uncertainty(self):
        self.write("# API-001 Delta Designed 2099\ncontract\n")
        result = self.lookup()
        self.assertTrue(result["incomplete"])
        self.assertTrue(any("Unclassified direct match" in w for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
