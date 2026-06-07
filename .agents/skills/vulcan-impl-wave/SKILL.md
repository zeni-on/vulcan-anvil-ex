---
name: vulcan-impl-wave
description: Use for Vulcan implementation phase work, BW-000 scaffold, Build Wave planning, worker Run creation, run-preflight, native subagent/thread delegation, optional agent-run/run-exec execution, run-integrate, wave-complete, and implementation traceability.
---

# Vulcan Impl Wave

Use this for `impl` Gate execution and follow-up implementation iterations.

## Preconditions

1. Confirm `session.json.current_gate` is `impl`.
2. Confirm previous Gate approval exists.
3. Confirm the delivery profile with `session.json` or `python vulcan.py profile-status`.
4. Apply profile-specific Run weight and trace depth rules from `docs/core/DELIVERY_PROFILES.md`.
5. Confirm implementation branch state with `python vulcan.py branch-status`.

## Workflow

1. Create or review an implementation plan Run when scope is more than a tiny change.
2. If buildable skeleton is missing, start `BW-000 implementation-scaffold` before feature waves.
3. Create one active Build Wave at a time.
4. Prefer `wave-start <BW-ID> --trace-seed <detailed-id>` or `run-new ... --trace-seed <id>`.
5. Narrow `scope.writable`, `target_contracts`, `interface_contract`, and verification commands before worker execution.
6. If related IDs/source documents are unclear, use `trace-scout` before finalizing the Run.
7. If the Run is important, newly generated, or previously problematic, use `run-drafter` before worker handoff.
8. Run `python vulcan.py run-preflight <run-file>` before native worker delegation. `run-exec` and `agent-run --mode work` auto-run preflight, but native subagent/thread/Agy Workspace branch delegation does not.
9. Use native worker delegation (subagent/thread/native branch agent) for code, test, UI, API, or DB implementation by default.
10. Use `agent-run --mode work` or `run-exec` only when external CLI process evidence, worktree isolation, watchdog/timeout, or cross-runner execution is needed.
11. After worker output, use `contract-reviewer` when runtime/API/DB/UI contract drift is plausible.
12. Integrate worker output only after diff/scope verification.
13. Record native subagent/thread output in `delegation_records`; external CLI workers also keep Run Execution Record and `_exec` logs.
14. Complete the Wave with `wave-complete` and `sync-session` only after relevant tests pass.

## Guardrails

- Orchestrator should not be the primary implementer.
- User silence about worker usage is not a direct-implementation exception.
- Do not mark Gate 3 planned tests as Pass during Impl just to satisfy trace checks.
- Full E2E/UI evidence belongs to Gate 4 unless explicitly scoped as smoke evidence.

## Verification

- `python vulcan.py run-check <run-file>`
- `python vulcan.py run-preflight <run-file>`
- Relevant backend/frontend tests for the Wave
- `python vulcan.py check-trace` after traceability updates
