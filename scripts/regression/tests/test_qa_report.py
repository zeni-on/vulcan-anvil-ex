import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import unicodedata
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from vulcan_core import qa_report as qa

spec = importlib.util.spec_from_file_location("vulcan_qa_report_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class QaReportTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.source = self.root / "cases.json"
        (self.root / "evidence.log").write_text("actual test output", encoding="utf-8")

    def write(self, rows):
        self.source.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        return self.source

    def case(self, **kw):
        return {"id": "TC-001", "status": "Pass", "title": "Visibility",
                "expected": "admin link visible", "actual": "link visible",
                "evidence": ["evidence.log"], **kw}

    def test_legacy_counts_and_sources_unchanged(self):
        rows = [{"id": f"TC-{i}", "상태": s, "절차": "1 열기 2 선택 3 확인",
                 "단계별기대결과": "3 코드 표시", "실행메모": "선택 직후 공란"}
                for i, s in enumerate(("Pass", "Fail", "Blocked", "Not Run"))]
        self.write(rows)
        before = self.source.read_bytes()
        report = qa.collect(self.source)
        self.assertEqual(report["summary"]["reported"], dict(Pass=1, Fail=1, Blocked=1, **{"Not Run": 1, "Unknown": 0}))
        self.assertFalse(report["tests_executed"])
        self.assertFalse(report["acceptance_authorized"])
        self.assertEqual(report["cases"][1]["reported_status"], "Fail")
        self.assertEqual(report["summary"]["unstructured_cases"], 4)
        self.assertEqual(self.source.read_bytes(), before)

    def test_unknown_and_exclusion_are_not_pass(self):
        self.write([self.case(id=str(i), status=s) for i, s in enumerate(("Skipped", "Approved", "", "Pass / Fail"))])
        report = qa.collect(self.source)
        self.assertEqual(report["summary"]["reported"]["Unknown"], 4)
        self.assertEqual(report["summary"]["reported"]["Pass"], 0)

    def test_environment_blocked_normalizes_without_changing_original(self):
        self.write([self.case(status="environment_blocked", blocker="API")])
        case = qa.collect(self.source)["cases"][0]
        self.assertEqual(case["reported_status"], "Blocked")
        self.assertEqual(case["original_status"], "environment_blocked")

    def test_scope_counts_keep_undecided_cases(self):
        self.write([self.case(id="1", scope="current"), self.case(id="2", scope="undecided")])
        report = qa.collect(self.source)
        self.assertEqual(report["source_count"], 2)
        self.assertEqual(report["summary"]["scopes"], {"current": 1, "undecided": 1})

    def test_no_false_full_pass_from_partial_observations(self):
        observations = [{"id": "admin", "expected": "visible", "actual": "visible", "status": "Pass", "evidence": ["evidence.log"]},
                        {"id": "staff", "expected": "hidden", "status": "Not Run"}]
        self.write([self.case(observations=observations)])
        case = qa.collect(self.source)["cases"][0]
        self.assertEqual(case["reported_status"], "Pass")
        self.assertEqual(case["observation_summary"], "Not Run")
        self.assertIn("reported_observation_mismatch", case["diagnostics"])

    def test_observation_aggregate_priorities(self):
        for statuses, expected in [(('Pass', 'Blocked'), 'Blocked'), (('Fail', 'Blocked'), 'Fail'),
                                   (('Pass', 'Pass'), 'Pass')]:
            with self.subTest(statuses=statuses):
                self.write([self.case(observations=[{"id": str(i), "expected": "x", "actual": "x", "status": s,
                                                    "evidence": ["evidence.log"]} for i, s in enumerate(statuses)])])
                self.assertEqual(qa.collect(self.source)["cases"][0]["observation_summary"], expected)

    def test_empty_observations_are_not_a_pass(self):
        self.write([self.case(observations=[])])
        self.assertEqual(qa.collect(self.source)["cases"][0]["observation_summary"], "Not structured")

    def test_missing_actual_or_expected_observation_is_not_complete(self):
        for missing in ("expected", "actual"):
            obs = {"id": "x", "expected": "x", "actual": "x", "status": "Pass", "evidence": ["evidence.log"]}
            del obs[missing]
            self.write([self.case(observations=[obs])])
            case = qa.collect(self.source)["cases"][0]
            self.assertEqual(case["observation_summary"], "Not Run")
            self.assertIn("incomplete_observation_support", case["diagnostics"])

    def test_missing_evidence_does_not_rewrite_original(self):
        self.write([self.case(evidence="absent.md")])
        case = qa.collect(self.source)["cases"][0]
        self.assertEqual(case["reported_status"], "Pass")
        self.assertEqual(case["evidence"][0]["status"], "missing")
        self.assertIn("evidence_unavailable_or_unresolved", case["diagnostics"])

    def test_no_evidence_or_actual_is_diagnosed(self):
        self.write([self.case(evidence=[], actual="")])
        self.assertEqual(set(qa.collect(self.source)["cases"][0]["diagnostics"]),
                         {"missing_evidence_reference", "missing_actual_observation"})

    def test_unicode_filename_resolution(self):
        name = unicodedata.normalize("NFD", "실행관측.md")
        (self.root / name).write_text("observation", encoding="utf-8")
        self.write([self.case(evidence="실행관측.md")])
        self.assertEqual(qa.collect(self.source)["cases"][0]["evidence"][0]["status"], "available")

    def test_parent_reference_requires_explicit_root(self):
        child = self.root / "run"
        child.mkdir()
        self.source = child / "cases.json"
        self.write([self.case(evidence="../evidence.log")])
        self.assertEqual(qa.collect(self.source)["cases"][0]["evidence"][0]["status"], "unsafe")
        self.assertEqual(qa.collect(self.source, self.root)["cases"][0]["evidence"][0]["status"], "available")

    def test_paths_are_not_split_on_slashes_or_log_extension(self):
        (self.root / "logs").mkdir()
        (self.root / "logs/out.log").write_text("output", encoding="utf-8")
        self.write([self.case(evidence="logs/out.log / evidence.log / RUN-001")])
        refs = qa.collect(self.source)["cases"][0]["evidence"]
        self.assertEqual([r["status"] for r in refs], ["available", "available", "unresolved"])
        self.assertEqual(refs[0]["ref"], "logs/out.log")

    def test_unsafe_references_never_read(self):
        self.write([self.case(evidence=["../../secret.log", "C:/secret.log", "javascript:alert(1)",
                                       "https://example.org/test.log", ".env.local", "\\\\server\\log.txt"])])
        self.assertTrue(all(r["status"] == "unsafe" for r in qa.collect(self.source)["cases"][0]["evidence"]))

    def test_markdown_and_plain_references_are_all_preserved(self):
        self.write([self.case(evidence="[log](evidence.log) / missing.log / RUN-002")])
        refs = qa.collect(self.source)["cases"][0]["evidence"]
        self.assertEqual([r["ref"] for r in refs], ["evidence.log", "missing.log", "RUN-002"])
        self.assertEqual([r["status"] for r in refs], ["available", "missing", "unresolved"])

    def test_symlink_evidence_rejected(self):
        link = self.root / "link.log"
        try:
            link.symlink_to(self.root / "evidence.log")
        except OSError:
            self.skipTest("symlink creation unavailable")
        self.write([self.case(evidence="link.log")])
        self.assertEqual(qa.collect(self.source)["cases"][0]["evidence"][0]["status"], "unsafe")

    def test_duplicate_case_ids_rejected(self):
        self.write([self.case(), self.case()])
        with self.assertRaisesRegex(ValueError, "duplicate case"):
            qa.collect(self.source)

    def test_duplicate_json_keys_rejected(self):
        self.source.write_text('[{"id":"x","status":"Fail","status":"Pass"}]', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            qa.collect(self.source)

    def test_invalid_observation_shape_rejected(self):
        for obs in ("text", [{"id": "x", "required": "false"}], [{"id": "x"}, {"id": "x"}]):
            with self.subTest(obs=obs):
                self.write([self.case(observations=obs)])
                with self.assertRaises(ValueError):
                    qa.collect(self.source)

    def test_bad_input_and_size_rejected(self):
        for data in (42, {"cases": []}, {"schema_version": True, "cases": []}, [{"id": ""}], [{"id": 3}]):
            self.write(data)
            with self.assertRaises(ValueError):
                qa.collect(self.source)
        self.write([self.case()])
        with mock.patch.object(qa, "MAX_BYTES", 1), self.assertRaises(ValueError):
            qa.collect(self.source)

    def test_versioned_input_and_empty_totals(self):
        self.write({"schema_version": 1, "cases": []})
        report = qa.collect(self.source)
        self.assertEqual(report["source_count"], 0)
        self.assertEqual(sum(report["summary"]["reported"].values()), 0)

    def test_html_escapes_all_dynamic_text_and_is_offline(self):
        attack = '</script><script>alert(1)</script><img src=x onerror=alert(1)>'
        self.write([self.case(title=attack, input=attack, actual=attack, id="x' onclick='alert(1)")])
        html = qa.render_html(qa.collect(self.source))
        self.assertNotIn(attack, html)
        self.assertIn("&lt;script&gt;", html)
        self.assertEqual(html.count("<script>"), 1)
        self.assertNotIn("<img", html)
        self.assertIn("default-src 'none'", html)
        self.assertNotIn("fetch(", html)

    def test_html_preserves_optional_observations(self):
        self.write([self.case(observations=[{"id": "optional-1", "required": False,
                                            "actual": "optional-note", "status": "Fail"}])])
        report = qa.collect(self.source)
        self.assertEqual(report["cases"][0]["observation_summary"], "Not structured")
        self.assertIn("optional-note", qa.render_html(report))

    def test_export_is_new_file_only_and_does_not_touch_source(self):
        self.write([self.case()])
        before = self.source.read_bytes()
        with self.assertRaises(FileExistsError):
            qa.export(self.source, self.source)
        target = self.root / "report.html"
        qa.export(self.source, target, "html")
        with self.assertRaises(FileExistsError):
            qa.export(self.source, target, "html")
        self.assertEqual(self.source.read_bytes(), before)

    def test_cli_export_does_not_require_or_change_session(self):
        self.write([self.case()])
        with contextlib.redirect_stdout(io.StringIO()):
            vulcan.cmd_export("qa.json", str(self.root), kind="qa", input_file="cases.json")
        self.assertFalse((self.root / "session.json").exists())
        self.assertEqual(json.loads((self.root / "qa.json").read_text(encoding="utf-8"))["source_count"], 1)

    def test_snapshot_default_contract_remains(self):
        with mock.patch.object(vulcan, "load_session", return_value={"project": "existing"}), \
                mock.patch.object(vulcan, "workflow_policy", return_value={}), \
                mock.patch.object(vulcan, "git_current_branch", return_value="main"), \
                mock.patch.object(vulcan, "git_log_timeline", return_value=[]), \
                mock.patch.object(vulcan, "collect_documents", return_value=[]), \
                contextlib.redirect_stdout(io.StringIO()):
            vulcan.cmd_export(project_dir=str(self.root))
        self.assertEqual(json.loads((self.root / "snapshot.json").read_text(encoding="utf-8"))["schema_version"], "1.0")


if __name__ == "__main__":
    unittest.main()
