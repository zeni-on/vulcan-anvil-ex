"""Product historical completion uses session records, not a Git proof ledger."""

from copy import deepcopy
import unittest
from unittest import mock

from test_product_process import vulcan


class ProductHistoryTests(unittest.TestCase):
    def session(self):
        return {"approvals": {"gate4": {"approved_at": "2026-08-01T10:00:00+09:00",
                                       "approval_evidence": "User approved QA"}},
                "gate_status": {"gate4": "done"}}

    def record(self, status="Completed"):
        return {"gate": "gate4", "path": "docs/runs/RUN-001.md", "status": status}

    def test_recorded_approval_does_not_require_git_or_history_depth(self):
        session = self.session()
        before = deepcopy(session)
        with mock.patch.object(vulcan, "git_text", side_effect=AssertionError("no Git history lookup")):
            for status in ("Completed", "Verified", "Done"):
                self.assertTrue(vulcan.product_run_is_approved_history(session, self.record(status)))
        self.assertEqual(session, before)

    def test_active_or_unapproved_gate_is_not_historical_completion(self):
        for status in ("Draft", "InProgress", "Failed", "Blocked", ""):
            self.assertFalse(vulcan.product_run_is_approved_history(self.session(), self.record(status)))
        for field, value in (("gate_status", {}), ("approvals", {}),
                             ("gate_status", {"gate4": "in-progress"})):
            session = self.session()
            session[field] = value
            self.assertFalse(vulcan.product_run_is_approved_history(session, self.record()))

    def test_invalid_approval_metadata_cannot_create_permission(self):
        for field, invalid in (("approved_at", "yesterday"), ("approved_at", None),
                               ("approval_evidence", ""), ("approval_evidence", [])):
            session = self.session()
            session["approvals"]["gate4"][field] = invalid
            self.assertFalse(vulcan.product_run_is_approved_history(session, self.record()))
        for location in ("approvals", "gate_status"):
            for invalid in (None, [], "unknown"):
                session = self.session()
                session[location] = invalid
                self.assertFalse(vulcan.product_run_is_approved_history(session, self.record()))


if __name__ == "__main__":
    unittest.main()
