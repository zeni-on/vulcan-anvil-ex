---
name: vulcan-impl-wave
description: Use for Vulcan implementation phase work, BW-000 scaffold, Build Wave planning, worker Run creation, run-preflight, agent-run/run-exec execution, run-integrate, wave-complete, and implementation traceability.
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
6. Run `python vulcan.py run-preflight <run-file>` before worker/subagent/runner execution.
7. Use worker/subagent/`agent-run --mode work` for code, test, UI, API, or DB implementation.
8. Integrate worker output only after diff/scope verification.
9. Complete the Wave with `wave-complete` and `sync-session` only after relevant tests pass.

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
