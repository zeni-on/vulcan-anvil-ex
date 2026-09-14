---
name: vulcan-orchestrator
description: Coordinate Vulcan project scope, process state, approvals and delegation; not ordinary code edits.
---

# Vulcan Orchestrator

Use this when coordinating a project's work or deciding its next process action.
For an assigned task, follow the handoff and the matching stage skill directly;
do not repeat the Orchestrator's startup or load every reference below.

## Select the process

Use the confirmed profile, role and scope; inspect selected session fields or
`status` when they are missing, stale or inconsistent.
For `process_model`, use [Core CLI section 4.1](../../../docs/core/ORCHESTRATOR_CLI_GUIDE.md).
Do not add the marker or reinterpret an unsupported model as legacy.
New Product init already creates planning: agree scope with `open-work`, not
`start` or Phase 0/Gate 1. Upgrade does not migrate unmarked projects.
Unmarked projects keep their existing Gate lifecycle in Core CLI section 4.

For Product execution, start with [Product section 7](../../../docs/core/PRODUCT_PROFILE_BASELINE.md)
and the current task sources. Run/Wave and a fresh worker are optional.
Other profiles retain their [delivery rules](../../../docs/core/DELIVERY_PROFILES.md).

## Read only for the current decision

| Decision | Reference |
| --- | --- |
| Product business scope, requirements or document authoring | [Product document writing](../../../docs/core/PRODUCT_DOCUMENT_WRITING.md) |
| Current contract versus accumulated history | [Current context](../../../docs/core/CURRENT_CONTEXT_AND_EVIDENCE.md) |
| Stage work | Matching design, implementation, QA or release skill; no umbrella reread |
| State, readiness or CLI arguments | [Core CLI](../../../docs/core/ORCHESTRATOR_CLI_GUIDE.md); `status --check` for readiness |
| Existing role-based collaboration | [Ownership and handoff](../../../docs/core/COLLABORATION_PROTOCOL.md), [Codex tools](../../../docs/adapters/codex-gpt/PERSONA_DELEGATION.md) |
| Native delegation or independent review | [Agent protocol section 5.4](../../../docs/core/AGENT_RUN_PROTOCOL.md), [Native model policy section 3.1](../../../docs/core/CODEX_MODEL_POLICY.md) |
| Legacy Gate authority or coordination remains unclear | Relevant section of [Orchestrator protocol](../../../docs/core/ORCHESTRATOR_PROTOCOL.md) |

Continue authorized work through its agreed checks and result handoff. Keep
scope/approval boundaries in AGENTS.md; a delegate's completion is not verified
acceptance or release approval. Report actual results and unresolved blockers,
not invented metadata or a new Run solely for reporting.
