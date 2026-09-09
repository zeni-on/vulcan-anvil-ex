"""Approval history is evidence, not an age-based exemption for future Runs."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("vulcan_product_history_tests", ROOT / "vulcan.py")
vulcan = importlib.util.module_from_spec(spec)
with mock.patch.object(sys, "platform", "linux"):
    spec.loader.exec_module(vulcan)


class ProductHistoryTests(unittest.TestCase):
    approval = {"approved_at": "2026-08-01T10:00:00+09:00", "approval_evidence": "User approved QA"}

    def approved_session(self):
        return {"approvals": {"gate4": self.approval}, "gate_status": {"gate4": "done"}}

    def test_history_over_200_commits_uses_one_batch_and_no_age_cutoff(self):
        session = self.approved_session()
        commits = [f"{index:040x}" for index in range(205, 0, -1)]
        snapshots = {ref: session for commit in commits for ref in (commit, f"{commit}^")}
        snapshots[f"{commits[-1]}^"] = {"approvals": {}, "gate_status": {"gate4": "pending"}}
        with mock.patch.object(vulcan, "git_text", return_value="\n".join(commits)) as query, \
                mock.patch.object(vulcan, "git_json_snapshots", return_value=snapshots) as batch:
            self.assertEqual(vulcan.product_gate_approval_snapshot(".", session, "gate4"), commits[-1])
        query.assert_called_once()
        batch.assert_called_once()
        self.assertIn("-G", query.call_args.args[0])
        self.assertNotIn("200", query.call_args.args[0])

    def test_batch_handles_missing_invalid_and_unicode_blobs(self):
        body = json.dumps({"approval_evidence": "사용자 승인"}, ensure_ascii=False).encode("utf-8")
        wire = b"a blob " + str(len(body)).encode() + b"\n" + body + b"\n"
        wire += b"absent:./session.json missing\nb blob 1\n{\n"
        with mock.patch.object(vulcan.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, wire)) as run:
            result = vulcan.git_json_snapshots(".", ["valid", "absent", "invalid"])
        self.assertEqual(result, {"valid": {"approval_evidence": "사용자 승인"}})
        run.assert_called_once()

    def test_ambiguous_approval_stays_unproved(self):
        for variant in ("no-evidence", "invalid-date", "no-parent", "not-done"):
            with self.subTest(variant=variant):
                session = self.approved_session()
                session["approvals"]["gate4"] = dict(self.approval)
                saved = self.approved_session()
                snapshots = {"commit": saved, "commit^": {"approvals": {}}}
                if variant == "no-evidence":
                    session["approvals"]["gate4"]["approval_evidence"] = ""
                elif variant == "invalid-date":
                    session["approvals"]["gate4"]["approved_at"] = "yesterday"
                elif variant == "no-parent":
                    snapshots.pop("commit^")
                else:
                    saved["gate_status"]["gate4"] = "pending"
                with mock.patch.object(vulcan, "git_text", return_value="commit"), \
                        mock.patch.object(vulcan, "git_json_snapshots", return_value=snapshots):
                    self.assertEqual(vulcan.product_gate_approval_snapshot(".", session, "gate4"), "")

    def test_malformed_approval_maps_remain_unproved(self):
        for location in ("session", "saved", "parent", "gate_status"):
            for invalid in (None, [], "unknown"):
                with self.subTest(location=location, invalid=invalid):
                    session = self.approved_session()
                    saved = self.approved_session()
                    parent = {"approvals": {}}
                    if location == "gate_status":
                        saved["gate_status"] = invalid
                    else:
                        {"session": session, "saved": saved, "parent": parent}[location]["approvals"] = invalid
                    with mock.patch.object(vulcan, "git_text", return_value="commit"), \
                            mock.patch.object(vulcan, "git_json_snapshots", return_value={"commit": saved, "commit^": parent}):
                        self.assertEqual(vulcan.product_gate_approval_snapshot(".", session, "gate4"), "")

    def test_actual_git_nested_project_preserves_approval_and_detects_changed_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project"
            project.mkdir()

            def git(*args):
                result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()

            def commit(message):
                git("add", "project")
                git("-c", "user.name=Regression", "-c", "user.email=regression@example.invalid", "commit", "-qm", message)
                return git("rev-parse", "HEAD")

            git("init", "-q")
            session_path = project / "session.json"
            session_path.write_text(json.dumps({"approvals": {}}), encoding="utf-8")
            commit("Before approval")
            run = project / "docs/runs/RUN-001.md"
            run.parent.mkdir(parents=True)
            run.write_text("# Completed QA\nstatus: Completed\n", encoding="utf-8")
            session = self.approved_session()
            session_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
            approved = commit("User approved QA")
            session["current_gate"] = "impl"
            session_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
            commit("New implementation cycle")
            with mock.patch.object(vulcan.subprocess, "run", wraps=subprocess.run) as calls:
                snapshot = vulcan.product_gate_approval_snapshot(str(project), session, "gate4")
            self.assertEqual(snapshot, approved)
            self.assertEqual(calls.call_count, 2)
            record = {"path": "docs/runs/RUN-001.md", "status": "Completed"}
            self.assertTrue(vulcan.product_run_matches_approval(str(project), record, snapshot))
            run.write_text("# Changed QA\nstatus: Completed\n", encoding="utf-8")
            self.assertFalse(vulcan.product_run_matches_approval(str(project), record, snapshot))
            record["status"] = "InProgress"
            self.assertFalse(vulcan.product_run_matches_approval(str(project), record, snapshot))


if __name__ == "__main__":
    unittest.main()
