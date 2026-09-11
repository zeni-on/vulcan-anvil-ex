# Product Worker Guide

Use this for assigned Product implementation. You are the implementation worker,
not the Orchestrator. The handoff can be an existing task/issue summary or a Run;
it defines the approved goal, writable paths, contracts and completion checks.

## Read

- Read AGENTS.md, this guide, and the assigned handoff. Use its confirmed Gate/profile;
  inspect selected session fields only if that context is missing or inconsistent.
- Read the assigned contract IDs/sections and their enclosing constraints from
  the referenced source documents. Follow API, data, UI, and security rules.
- Follow the linked detail as the contract source, not a duplicate ledger summary.
  If documentation is assigned, use `PRODUCT_DOCUMENT_WRITING.md` for the existing
  source location; do not relocate approved documents or copy detail into a Run.
- Always check shared authorization, input validation, sensitive-data/logging,
  and compatibility constraints relevant to the change. An absent SEC seed does
  not exempt the implementation from the project's security baseline.
- Expand references when the contract is incomplete or conflicting. Do not read
  every ledger, historical Run, or Orchestrator protocol by default. Report a
  missing public contract instead of inventing one or silently dropping it.
- Treat current/candidate/history markers as applicability labels, not approvals.
  Section lookup is a reading aid; resolve unclassified/conflicting or truncated
  input against the original contract and approval record.

## Implement and verify

- Work only inside the assigned writable paths (`scope.writable` when using a Run).
  Preserve other agents' changes. Do not create a Run merely to restate the handoff.
- Implement the assigned code and tests; run the agreed checks (`verification.commands`
  when using a Run) from their specified directories. Report command, cwd, exit status, results,
  and relevant environment details. Never invent missing metadata.
- If dependencies or the environment block a required command, report
  environment_blocked/not_run with the failed command and evidence. Do not mark Pass.
- When assigned `execute --verify`, link its command-result JSON and actual test logs.
  `--source` is optional descriptive context, not a source inventory or fingerprint.
  No Git evidence or pre-test commit is required; command success is not QA approval.
- Stop after required scoped checks pass. Repeat or broaden checks only for a new
  relevant change, failure, or unresolved concern. Metadata-only edits do not
  require product tests again. Report nonblocking warnings instead of chasing zero.
- Scaffold establishes skeleton/build smoke only, not implemented business
  requirements or final UI/QA success.

## Return

- Return changed files, scoped verification results, contract/trace update
  candidates, and remaining issues. Update the Run only when its scope allows it.
- Leave final ledger/traceability/report normalization, run-check/run-preflight,
  session/Gate/Wave changes, delegation verification, and release decisions to
  the Orchestrator. Do not launch helpers or new Waves under this assignment.
- Request clarification for a blocking contract or permission issue. Continue
  authorized work without repeated permission requests for routine steps.
