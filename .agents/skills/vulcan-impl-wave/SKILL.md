---
name: vulcan-impl-wave
description: Plan or coordinate implementation in a Vulcan project; assigned Product workers use their handoff instead.
---

# Vulcan Implementation

Assigned Product workers use the handoff and [Product worker guide](../../../docs/core/PRODUCT_WORKER_GUIDE.md).
Do not perform Orchestrator planning, delegation or state updates under that assignment.

## Select the process

For `process_model`, use [Core CLI section 4.1](../../../docs/core/ORCHESTRATOR_CLI_GUIDE.md)
instead of legacy Gate steps. Do not add the marker or reinterpret an unsupported
model as legacy. Inspect selected `session.json` fields only if the assigned state
is missing or inconsistent.

For Product, use [Product section 7](../../../docs/core/PRODUCT_PROFILE_BASELINE.md):
implement the approved goal within its writable scope, with current contract
references and meaningful completion checks. Run/Wave and a fresh worker are optional.
Respect user-assigned roles. Continue authorized implementation, fixes and affected
checks through the agreed handoff; do not repeat tests for report-only edits.

For unmarked projects using Run/Wave, or Audit/PoC implementation, read
[legacy implementation](references/legacy-gates.md). Keep that lifecycle conditional;
do not introduce a Wave merely to follow the recipe.

## Completion

Return actual scoped results and unresolved issues. The Orchestrator verifies
the diff, scope and evidence under Product section 7; worker completion is not
acceptance or release approval. Use the [agent protocol](../../../docs/core/AGENT_RUN_PROTOCOL.md)
when delegation or independent review is needed, not for every edit.
