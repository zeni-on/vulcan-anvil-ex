---
name: vulcan-orchestrator
description: Use for Vulcan-Anvil Ex project orchestration, Gate status checks, Run planning, approval boundaries, worker/reviewer routing, traceability checks, and autonomous follow-up across Phase 0 through Gate 5.
---

# Vulcan Orchestrator

Use this as the entry skill for Vulcan-Anvil Ex work. Keep Core rules in project documents; this skill is only a short routing card.

## Start

1. Read `AGENTS.md` and the user's latest request when Codex is the primary runner. Inspect current Gate/profile/branch fields or `status`; do not print the full accumulated `session.json` by default.
2. Confirm `session.json.current_gate` and do not create artifacts beyond the current approved Gate.
3. Run `python vulcan.py status` first when current Gate, profile, branch, Run, or next action is unclear.
4. Confirm the delivery profile from `session.json`, `python vulcan.py status`, or `python vulcan.py profile-status`.
5. Apply profile-specific depth, evidence, review, and Run-weight rules from `docs/core/DELIVERY_PROFILES.md`.
   - In `poc`, prefer subagent/result-summary flow for short experiments; create compact Runs only for external workers, independent review, long delegation, or reproducible experiment records.
   - In `poc`, do not create Gate-level Orchestrator Plan Runs by habit. Use `docs/poc` plus `python vulcan.py status --check` unless a Run is needed for handoff or replay.
   - In `poc`, allow `TBD` only with reason and next decision timing. Do not leave goals, success criteria, or actual execution results as `TBD`.
6. If the task is non-trivial, read `docs/core/ORCHESTRATOR_PROTOCOL.md`.
7. Use `docs/core/ORCHESTRATOR_CLI_GUIDE.md` for CLI usage; use `python vulcan.py branch-status` only when branch detail is needed beyond `status`.
8. Run `python vulcan.py doctor` only when local runtime readiness matters: after init/upgrade on an unfamiliar machine, before first worker if toolchain state is unknown, before Gate 4 QA-000/UI evidence, or after npm/Playwright/runner/Dashboard/environment-blocked failures.

## Route

- Discovery, requirements, design, implementation, QA, and release work should stay inside the active Gate.
- If a narrower Vulcan skill matches, use it before continuing:
  - `vulcan-design`
  - `vulcan-impl-wave`
  - `vulcan-qa`
  - `vulcan-release`
- Use existing Core and adapter docs for details. Do not copy full Core rules into prompts.
- When the user chooses persistent role-based collaboration, read `docs/core/COLLABORATION_PROTOCOL.md` and `docs/adapters/codex-gpt/PERSONA_DELEGATION.md`. Route approved work to the selected existing tasks when messaging tools are available; use subagents for bounded subtasks. Keep one Orchestrator for shared state, and do not create user-visible tasks without a user request.
- For accumulated contract documents or unclear evidence source revisions, use `docs/core/CURRENT_CONTEXT_AND_EVIDENCE.md`. Retrieve relevant sections; do not treat the newest paragraph as approved or copy entire ledgers into each handoff.
- When the user has approved autonomous orchestration or custom-agent assistance, use helper agents from `.gemini/agents/` or `.codex/agents/` selectively:
  - `trace-scout`: related IDs/source documents are broad or unclear.
  - `run-drafter`: a Run needs worker handoff quality review.
  - `contract-reviewer`: design, implementation, API, DB, UI, or release contract consistency is risky.
  - `qa-reader`: QA logs/evidence contain mixed failures, stale results, or unclear root causes.
- Custom agent results are advisory. Record whether execution was native custom agent or prompt-contract fallback when reporting.
- Use `docs/core/CODEX_MODEL_POLICY.md` section 3.1: inherit the user's model configuration, choose supported effort per task (normally medium), and preserve explicit user overrides. Do not rewrite user/global model settings.
- Apply `docs/core/AGENT_RUN_PROTOCOL.md` section 5.4 before independent review. In Product, assess risk instead of invoking reviewers for every Wave; preserve mandatory Audit/customer/user reviews. Use a new reviewer without parent conversation (`fork_context: false` when available), with scoped contracts/diff/evidence rather than the implementer's success narrative. External models are optional unless explicitly required.
- See `docs/reference/CODEX-CUSTOM-AGENT-STRATEGY.md` for details.

## Guardrails

- Gate transitions require explicit user approval or an explicit proceed instruction.
- Gate status is changed through `vulcan.py` commands, not by editing `session.json` directly.
- Use `python vulcan.py status --check` for Gate transition readiness summary. Use `prepare-transition` only when detailed/compatibility transition diagnostics are needed. Use `check-trace` only when traceability needs detailed debugging or trace-only regression verification.
- Use `doctor` as a local environment diagnostic, not as a Gate readiness substitute. `doctor fail/warn` should be reported as environment readiness, `environment_blocked`, or an ISSUE candidate unless a product defect is separately reproduced.
- Use `run-check`, `run-preflight`, and `check-contract` as applicable.
- Before native worker delegation, confirm `run-preflight` passes, directly or through `execute --dry-run`. Recheck after Run/contract/scope/project-state changes. External work execution auto-runs preflight; native delegation does not.
- Treat `prepare-transition` preflight findings as a safety net for completed current-Gate worker Runs, not as a substitute for pre-worker handoff preflight.
- Worker, subagent, and external runner outputs are candidates until the Orchestrator verifies them.
- For Product, use `PRODUCT_PROFILE_BASELINE.md` section 7 for scoped handoff, warning handling, and conditional reruns. Keep Gate approval and required QA checks intact.
- Use native completion notifications or a long wait when available. Do independent authorized work while a worker runs; send new instructions only for changed scope, a blocker, or a necessary correction.
- Native subagent/thread outputs should be normalized into `delegation_records`; external CLI runner outputs keep the full Run Execution Record and `_exec` logs.
- Do not treat global memory or other sample projects as project facts.

## CLI

Do not run `python vulcan.py --help` repeatedly to discover routine commands. Use `docs/core/ORCHESTRATOR_CLI_GUIDE.md` and start with:

- Current overview: `python vulcan.py status`
- Transition readiness summary: `python vulcan.py status --check`
- Local environment check: `python vulcan.py doctor`
- Retrospective/performance summary: `python vulcan.py metrics`

## Report

End with the current Gate, changed files, verification commands, remaining issues, and the next approval point.
