# Product Worker Guide

Use this for an assigned Product build/scaffold Run. You are the implementation
worker, not the Orchestrator. The Run defines the approved task and writable paths.

## Read

- Read AGENTS.md, this guide, and the assigned Run. Use its confirmed Gate/profile;
  inspect selected session fields only if that context is missing or inconsistent.
- Read the assigned contract IDs/sections and their enclosing constraints from
  the Run's source documents. Follow referenced API, data, UI, and security rules.
- Always check shared authorization, input validation, sensitive-data/logging,
  and compatibility constraints relevant to the change. An absent SEC seed does
  not exempt the implementation from the project's security baseline.
- Expand references when the contract is incomplete or conflicting. Do not read
  every ledger, historical Run, or Orchestrator protocol by default. Report a
  missing public contract instead of inventing one or silently dropping it.

## Implement and verify

- Work only inside scope.writable. Preserve other agents' changes.
- Implement the assigned code and tests; run the concrete verification.commands
  from their specified directories. Report command, cwd, exit status, results,
  and source/environment identity when observable. Never invent missing metadata.
- If dependencies or the environment block a required command, report
  environment_blocked/not_run with the failed command and evidence. Do not mark Pass.
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
