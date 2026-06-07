---
name: vulcan-orchestrator
description: Use for Vulcan-Anvil Ex project orchestration, Gate status checks, Run planning, approval boundaries, worker/reviewer routing, traceability checks, and autonomous follow-up across Phase 0 through Gate 5.
---

# Vulcan Orchestrator

Use this as the entry skill for Vulcan-Anvil Ex work. Keep Core rules in project documents; this skill is only a short routing card.

## Start

1. Read `GEMINI.md` (or `AGENTS.md` depending on the primary runner), `session.json`, and the user's latest request.
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
- When the user has approved autonomous orchestration or custom-agent assistance, use helper agents from `.gemini/agents/` or `.codex/agents/` selectively:
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
- Native subagent/thread outputs should be normalized into `delegation_records`; external CLI runner outputs keep the full Run Execution Record and `_exec` logs.
- Do not treat global memory or other sample projects as project facts.

## CLI Quick Commands Map (Do not run --help, use this immediately)

- **Gate Control**:
  - Start Gate: `python vulcan.py gate-start <gate>` (e.g. `phase0`, `gate1`, `gate2`, `gate3`, `impl`, `gate4`, `gate5`)
  - Complete Gate: `python vulcan.py session --gate <gate> --status done` (Optional: `--feature <name>`)
  - Sync Remote/Local: `python vulcan.py sync-session`
- **Run Lifecyle**:
  - Create Orchestrator Plan: `python vulcan.py orchestrator-plan --goal "<goal>" --gate <gate>`
  - Create New Run: `python vulcan.py run-new --skill <skill> --title "<title>" --related-ids "<ids>"`
  - Preflight Check: `python vulcan.py run-preflight <run_file>`
  - Complete Check: `python vulcan.py run-check <run_file>`
  - Static Trace Check: `python vulcan.py check-trace`
- **Build Wave & QA**:
  - Integration Branch Status: `python vulcan.py branch-status`
  - Start Integration Branch: `python vulcan.py branch-start impl`
  - Start Build Wave: `python vulcan.py wave-start <BW-ID> --trace-seed <seed_id>`
  - Complete Build Wave: `python vulcan.py wave-complete <BW-ID> --status Verified`
  - Integrate Run: `python vulcan.py run-integrate <run_file>`
- **Release & Upgrade**:
  - Dry-run Release PR: `python vulcan.py release-pr --dry-run`
  - Upgrade framework: `python vulcan.py upgrade`

## Report

End with the current Gate, changed files, verification commands, remaining issues, and the next approval point.
