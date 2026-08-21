import json
import os
import tempfile
import unittest

from vulcan_core.status import (
    collect_dashboard_comments,
    collect_model_fallbacks,
    implementation_display_counts,
    render_status_report,
    status_next_actions,
)


GATES = ["phase0", "gate1", "gate2", "gate3", "impl", "gate4", "gate5"]


class StatusCoreTests(unittest.TestCase):
    def test_impl_and_profile_gap_actions_keep_existing_priority(self):
        actions = status_next_actions(
            session_exists=True,
            current_gate="impl",
            current_branch="main",
            integration_branch="dev",
            active_waves=[],
            known_gates=GATES,
            profile_gap={"summary": {"missing": 1, "content_issues": 0}},
            gap_target="product",
            qa_workspace_followup=[],
        )

        self.assertEqual(actions[0], "python vulcan.py status --check")
        self.assertEqual(actions[1], "python vulcan.py profile-gap --to product")
        self.assertEqual(actions[2], "python vulcan.py branch-start impl")

    def test_qa_blocked_actions_override_normal_gate_actions(self):
        actions = status_next_actions(
            session_exists=True,
            current_gate="gate4",
            current_branch="dev",
            integration_branch="dev",
            active_waves=[],
            known_gates=GATES,
            profile_gap=None,
            gap_target="product",
            qa_workspace_followup=["blocked"],
        )

        self.assertEqual(actions, [
            "QA-000 doctor JSON/evidence 확인",
            "환경 문제는 ISSUE/environment_blocked로 보류",
            "제품 수정 필요 시 qa-fix-loop 생성",
        ])

    def test_sidecar_collectors_preserve_status_vocabulary_and_fallbacks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            comments_dir = os.path.join(temp_dir, ".vulcan", "comments")
            os.makedirs(comments_dir)
            comments_path = os.path.join(comments_dir, "comments.jsonl")
            with open(comments_path, "w", encoding="utf-8") as file_obj:
                file_obj.write(json.dumps({
                    "comment_id": "CMT-001",
                    "document": "docs/example.md",
                    "status": "open",
                    "category": "question",
                    "anchor": {"start_line": 12},
                    "body": "status sidecar comment",
                }) + "\n")
                file_obj.write(json.dumps({"comment_id": "CMT-002", "status": "resolved"}) + "\n")

            exec_dir = os.path.join(temp_dir, "docs", "runs", "_exec")
            os.makedirs(exec_dir)
            with open(os.path.join(exec_dir, "RUN-001.json"), "w", encoding="utf-8") as file_obj:
                json.dump({
                    "run_id": "RUN-001",
                    "runner": "codex-cli",
                    "model": "gpt-5.5",
                    "model_fallback_reason": "unsupported model fallback",
                }, file_obj)

            comments = collect_dashboard_comments(temp_dir)
            fallbacks = collect_model_fallbacks(temp_dir)

            self.assertEqual(comments["total"], 2)
            self.assertEqual(comments["open"], 1)
            self.assertEqual(comments["closed"], 1)
            self.assertEqual(comments["items"][0]["line"], 12)
            self.assertEqual(fallbacks[0]["target_id"], "RUN-001")
            self.assertEqual(fallbacks[0]["model"], "gpt-5.5")

    def test_render_and_implementation_counts_remain_stable(self):
        implementation = {
            "requirements": {"implemented": 2, "total": 4},
            "waves": {"completed": 1, "total": 2, "current": "BW-002"},
        }
        counts = implementation_display_counts(implementation)
        self.assertEqual(counts["percent"], 50)

        summary = {
            "project": "status-fixture",
            "profile": "product",
            "current_gate": "impl",
            "gate_status": "in-progress",
            "current_branch": "dev",
            "main_branch": "main",
            "integration_branch": "dev",
            "integration_exists": True,
            "dirty_blocking": False,
            "session_branch_role": "integration",
            "qa_workspace": {},
            "implementation": implementation,
            "active_runs": [],
            "active_waves": [{"id": "BW-002", "status": "InProgress", "run": "RUN-002"}],
            "model_fallbacks": [],
            "profile_gap": {},
            "dashboard_comments": {},
            "next_actions": ["python vulcan.py wave-complete <BW-ID> --status Verified"],
        }
        rendered = render_status_report(summary)
        self.assertIn("implemented: 2 / 4", rendered)
        self.assertIn("percent: 50", rendered)
        self.assertIn("BW-002 (InProgress) / RUN-002", rendered)


if __name__ == "__main__":
    unittest.main()
