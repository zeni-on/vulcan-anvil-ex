---
name: vulcan-orchestrator
description: Use for Vulcan-Anvil Ex project orchestration, Gate status checks, Run planning, approval boundaries, worker/reviewer routing, traceability checks, and autonomous follow-up across Phase 0 through Gate 5.
---

# Vulcan Orchestrator

Use this as the entry skill for Vulcan-Anvil Ex work. Keep Core rules in project documents; this skill is only a short routing card.

## Start

1. Read `AGENTS.md`, `session.json`, and the user's latest request.
2. Confirm `session.json.current_gate` and do not create artifacts beyond the current approved Gate.
3. Confirm the delivery profile from `session.json` or `python vulcan.py profile-status`.
4. Apply profile-specific depth, evidence, review, and Run-weight rules from `docs/core/DELIVERY_PROFILES.md`.
   - In `poc`, prefer subagent/result-summary flow for short experiments; create compact Runs only for external workers, independent review, long delegation, or reproducible experiment records.
   - In `poc`, allow `TBD` only with reason and next decision timing. Do not leave goals, success criteria, or actual execution results as `TBD`.
5. If the task is non-trivial, read `docs/core/ORCHESTRATOR_PROTOCOL.md`.
6. Use `python vulcan.py branch-status` when branch or implementation/QA workspace state is unclear.

## Route

- Discovery, requirements, design, implementation, QA, and release work should stay inside the active Gate.
- If a narrower Vulcan skill matches, use it before continuing:
  - `vulcan-design`
  - `vulcan-impl-wave`
  - `vulcan-qa`
  - `vulcan-release`
- Use existing Core and adapter docs for details. Do not copy full Core rules into prompts.
- When the user has approved autonomous orchestration or custom-agent assistance, use `.codex/agents/` helper agents selectively:
  - `trace-scout`: related IDs/source documents are broad or unclear.
  - `run-drafter`: a Run needs worker handoff quality review.
  - `contract-reviewer`: design, implementation, API, DB, UI, or release contract consistency is risky.
  - `qa-reader`: QA logs/evidence contain mixed failures, stale results, or unclear root causes.
- Custom agent results are advisory. Record whether execution was native custom agent or prompt-contract fallback when reporting.
- See `docs/reference/CODEX-CUSTOM-AGENT-STRATEGY.md` for details.

## Guardrails

- Gate transitions require explicit user approval or an explicit proceed instruction.
- Gate status is changed through `vulcan.py` commands, not by editing `session.json` directly.
- Use `run-check`, `run-preflight`, `check-trace`, and `check-contract` as applicable.
- Worker, subagent, and external runner outputs are candidates until the Orchestrator verifies them.
- Do not treat global memory or other sample projects as project facts.

## Report

End with the current Gate, changed files, verification commands, remaining issues, and the next approval point.
