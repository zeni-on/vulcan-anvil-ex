---
name: vulcan-qa
description: Use for Vulcan Gate 4 QA execution, QA-000 workspace preparation, QA-001 command verification, QA-002 UI/E2E evidence, QA-003 result synthesis, QA findings, qa-fix-loop handoff, retest, and evidence normalization.
---

# Vulcan QA

Use this for Gate 4 QA and QA iterations.

## Preconditions

1. Confirm `session.json.current_gate` is `gate4`.
2. Confirm Impl was approved or explicitly completed for QA.
3. Run `python vulcan.py status` to confirm Gate, profile, branch, QA workspace, active Run, and dirty state.
4. Apply profile-specific QA evidence and review strictness from `docs/core/DELIVERY_PROFILES.md`.
5. Read the current QA scope and applicable test plan. Read the QA Run when one is used; Product may use an existing task summary and regression report under `PRODUCT_PROFILE_BASELINE.md` section 7.
6. Run `python vulcan.py doctor` before QA-000 when the machine/project has not been checked in this session, or when npm, Playwright, browser cache, runner, port, DB, or Dashboard readiness is uncertain.

## Staged QA

1. `QA-000`: prepare or confirm the QA workspace on the integration branch, dependencies, ports, DB, and smoke readiness.
2. `QA-001`: run command-based checks such as syntax, unit/integration tests, lint, build, and contract checks.
3. `QA-002`: collect UI/E2E evidence, screenshots, logs, and browser artifacts. For audit/product profiles, official UI Pass must be based on `@playwright/test` and `npx playwright test`; custom Playwright library scripts are PoC smoke/demo or auxiliary evidence only.
4. `QA-003`: synthesize Test Result, QA Finding, traceability status candidates, and approval/blocking issues.

`QA-001` to `QA-003` must reuse the workspace recorded by `QA-000`. A separate QA worktree is optional and should be used only when explicitly enabled by project policy.

For Product, use `docs/core/PRODUCT_PROFILE_BASELINE.md` section 7 for evidence
review and repeat-check decisions. Execute the approved release-candidate checks;
do not replace them with Impl self-checks. Subsequent report-only edits do not
require running the same product tests again. Record remaining warnings honestly.

## Failure Handling

- QA workers execute tests and collect evidence; they do not fix code immediately.
- If QA is delegated to a native subagent/thread, retain delegate, scope, evidence/log paths, result summary, and Orchestrator verification in the existing result summary. Use `delegation_records` when a Run is used; do not invent reruns that were not executed.
- If QA is delegated to an external CLI runner, keep the full Run Execution Record, `_exec` logs, watchdog/timeout status, and any recovered transcript.
- If logs, screenshots, transcripts, or previous failures are mixed, use `qa-reader` to classify evidence before deciding a fix path.
- If a QA command is `Not Run` or `environment_blocked` because of local tooling, run `doctor` before retrying or classifying it as a product failure.
- If QA failure appears related to Program/API/DB/UI contract drift, consider a fresh-context `contract-reviewer` under `AGENT_RUN_PROTOCOL.md` section 5.4 before creating a `qa-fix-loop`. Preserve mandatory reviews; do not treat an inherited implementation conversation as independent review.
- Classify failures as `FIND`, `CR`, `ISSUE`, or `environment_blocked`.
- Start `qa-fix-loop` only after Orchestrator/user decision.
- A `qa-fix-loop` Run must name the target `FIND-ID`, scope writable paths, and verification commands. Product may keep the approved fix scope and retest criteria in the existing issue/task summary instead of creating a Run.

## Verification

- Run `python vulcan.py run-check <run-file>` when QA or fix Runs are used.
- Run `python vulcan.py status --check` after QA result synthesis to check Gate readiness.
- Run `python vulcan.py prepare-transition` only when detailed/compatibility transition diagnostics are needed.
- Run `python vulcan.py check-trace` only if the readiness output points to traceability errors that need detailed debugging.
- Run `python vulcan.py check-contract` when Program Design contracts are relevant.
- When tested-source identity is needed, use the optional `execute --verify` path in `docs/core/ORCHESTRATOR_CLI_GUIDE.md`. Link its JSON through existing evidence fields; command success, source identity, and QA approval are separate facts.
