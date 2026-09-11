---
name: vulcan-release
description: Use for Vulcan Gate 5 release approval, release readiness review, backlog/non-blocking issue handling, release-pr dry-run/body generation, tag/release note preparation, and final approval boundaries.
---

# Vulcan Release

Use this for Gate 5 release and release preparation.

For projects with `process_model`, follow `docs/core/ORCHESTRATOR_CLI_GUIDE.md`
section 4.1 instead of the legacy Gate lifecycle below. Use the assigned scope and
authority; do not add the marker or reinterpret an unsupported model as legacy.
Unmarked projects keep the existing flow.

## Preconditions

1. Confirm `session.json.current_gate` is `gate5` or that Gate 4 is approved for Gate 5.
2. For Product, follow `PRODUCT_PROFILE_BASELINE.md` section 7 and read the current release scope, applicable test results, open issues and approval record. Other profiles read Release Approval, Test Result, QA Finding, Backlog, Change Request, and Traceability Matrix.
3. Run `python vulcan.py status` to confirm Gate, profile, branch, release readiness context, and dirty state.
4. Apply profile-specific release control from `docs/core/DELIVERY_PROFILES.md`.
5. Use `python vulcan.py branch-status` only if branch-only detail is needed beyond `status`.

## Workflow

1. Separate blocking defects from accepted backlog/non-blocking issues.
2. Verify QA results and Gate transition readiness before release approval.
3. Use `python vulcan.py release-pr --dry-run` before creating PR or final release material.
4. Keep release notes tied to actual changes, applicable Run/FIND/CR/ISSUE records and known residual risks. Product does not create Runs or separate Git evidence for release-note bookkeeping.
5. Do not claim final approval without explicit user approval.

## Verification

- `python vulcan.py status --check`
- `python vulcan.py prepare-transition` only when detailed/compatibility transition diagnostics are needed
- `python vulcan.py check-trace` only when traceability needs detailed debugging
- Relevant `run-check` commands for release Runs
- `python vulcan.py release-pr --dry-run`
- Project tests required by the release profile

## Report

Report release status, blocking issues, accepted backlog items, verification commands, PR/tag/release-note readiness, and the explicit approval needed.
