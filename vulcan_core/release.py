"""Release PR policy and rendering helpers for Vulcan-Anvil Ex."""

import os


def release_profile_policy(profile):
    if profile == "poc":
        return {
            "release_doc": "docs/poc/POC_TEST_REPORT.md",
            "evidence_documents": [
                "docs/poc/POC_REQUIREMENTS.md",
                "docs/poc/POC_SYSTEM_DESIGN.md",
                "docs/poc/POC_TEST_REPORT.md",
            ],
            "verification_checklist": [
                "`python vulcan.py status --check`",
                "PoC evidence logs and smoke result reviewed",
                "Open ISSUE/Backlog/promotion candidates reviewed",
                "PoC continue/pivot/stop decision reviewed",
                "Independent review completed or explicitly waived",
            ],
        }
    if profile == "product":
        release_doc = "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md"
        return {
            "release_doc": release_doc,
            "evidence_documents": [
                release_doc,
                "docs/product/PRODUCT_BRIEF.md",
                "docs/product/PRODUCT_CONTRACTS.md",
                "docs/product/PRODUCT_TRACEABILITY.md",
                "docs/product/REGRESSION_AND_RELEASE_REPORT.md",
                "docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md",
            ],
            "verification_checklist": [
                "`python vulcan.py status --check`",
                "Product regression result and release scope reviewed",
                "Product traceability and backlog/deferred items reviewed",
                "Gate 4 UI/API evidence reviewed",
                "Release approval document reviewed",
                "Independent PR review completed or explicitly waived",
            ],
        }

    release_doc = "docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md"
    return {
        "release_doc": release_doc,
        "evidence_documents": [
            release_doc,
            "docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md",
            "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md",
            "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md",
        ],
        "verification_checklist": [
            "`python vulcan.py check-trace`",
            "`python vulcan.py check-contract` if Program Design contracts are in scope",
            "Gate 4 QA command logs and evidence reviewed",
            "Open FIND/CR/ISSUE/Backlog items reviewed",
            "Release approval document reviewed",
            "Independent PR review completed or explicitly waived",
        ],
    }


def build_release_pr_body(
    *,
    project_name,
    profile,
    base_branch,
    head_branch,
    title,
    diff_stat,
    commit_log,
    evidence_status,
):
    policy = release_profile_policy(profile)
    diff_stat = diff_stat or "(no local diff stat available)"
    commit_log = commit_log or "(no local commits found between base/head)"
    doc_lines = []
    for rel_path in policy["evidence_documents"]:
        marker = "OK" if evidence_status.get(rel_path, False) else "MISSING"
        doc_lines.append(f"- [{marker}] `{rel_path}`")
    checklist_lines = "\n".join(f"- [ ] {item}" for item in policy["verification_checklist"])

    return f"""# {title}

## Release Candidate

- Project: `{project_name}`
- Profile: `{profile}`
- Base: `{base_branch}`
- Head: `{head_branch}`
- Source of truth: `{policy['release_doc']}`
- Merge policy: manual only after Gate 5 approval

## Gate 5 Evidence Documents

{chr(10).join(doc_lines)}

## Verification Checklist

{checklist_lines}

## Diff Stat

```text
{diff_stat}
```

## Commits

```text
{commit_log}
```

## Notes

This PR is a Gate 5 release candidate from the integration branch to the release baseline.
It must not be auto-merged by runner output alone. Merge requires explicit user approval or the project's Gate 5 release approval process.
"""


def release_pr_body_path(project_dir):
    body_dir = os.path.join(project_dir, ".vulcan", "release")
    os.makedirs(body_dir, exist_ok=True)
    return os.path.join(body_dir, "release-pr-body.md")


def release_pr_commands(base_branch, head_branch, title, body_path):
    return {
        "list": [
            "gh", "pr", "list",
            "--base", base_branch,
            "--head", head_branch,
            "--state", "open",
            "--json", "number,url",
            "--limit", "10",
        ],
        "create": [
            "gh", "pr", "create",
            "--base", base_branch,
            "--head", head_branch,
            "--title", title,
            "--body-file", body_path,
        ],
    }
