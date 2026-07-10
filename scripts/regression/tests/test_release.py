import os
import tempfile
import unittest

from vulcan_core.release import (
    build_release_pr_body,
    release_pr_body_path,
    release_pr_commands,
    release_profile_policy,
)


def _body(profile):
    policy = release_profile_policy(profile)
    evidence_status = {path: True for path in policy["evidence_documents"]}
    return build_release_pr_body(
        project_name="release-fixture",
        profile=profile,
        base_branch="main",
        head_branch="dev",
        title="Fixture release",
        diff_stat="1 file changed",
        commit_log="abc123 fixture commit",
        evidence_status=evidence_status,
    )


class ReleaseBodyTests(unittest.TestCase):
    def test_audit_body_keeps_full_gate5_evidence_contract(self):
        body = _body("audit")

        self.assertIn("Profile: `audit`", body)
        self.assertIn("DOC-QA-G4-002_Test-Result_v0.1.md", body)
        self.assertIn("DOC-CORE-G4-001_Traceability-Matrix_v0.1.md", body)
        self.assertIn("Independent PR review completed or explicitly waived", body)
        self.assertIn("must not be auto-merged", body)

    def test_product_body_uses_product_ledger_without_audit_only_docs(self):
        body = _body("product")

        self.assertIn("Profile: `product`", body)
        self.assertIn("docs/product/PRODUCT_TRACEABILITY.md", body)
        self.assertIn("docs/product/REGRESSION_AND_RELEASE_REPORT.md", body)
        self.assertNotIn("DOC-QA-G4-002_Test-Result", body)
        self.assertNotIn("DOC-CORE-G4-001_Traceability-Matrix", body)

    def test_poc_body_uses_compact_poc_evidence(self):
        body = _body("poc")

        self.assertIn("Profile: `poc`", body)
        self.assertIn("docs/poc/POC_TEST_REPORT.md", body)
        self.assertIn("PoC continue/pivot/stop decision reviewed", body)
        self.assertNotIn("DOC-PM-G5-001_Release-Approval", body)

    def test_release_path_and_gh_commands_remain_stable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            body_path = release_pr_body_path(temp_dir)

            self.assertEqual(
                body_path,
                os.path.join(temp_dir, ".vulcan", "release", "release-pr-body.md"),
            )
            self.assertTrue(os.path.isdir(os.path.dirname(body_path)))
            commands = release_pr_commands("main", "dev", "Fixture release", body_path)
            self.assertEqual(commands["create"][:3], ["gh", "pr", "create"])
            self.assertIn("--body-file", commands["create"])
            self.assertEqual(commands["list"][:3], ["gh", "pr", "list"])


if __name__ == "__main__":
    unittest.main()
