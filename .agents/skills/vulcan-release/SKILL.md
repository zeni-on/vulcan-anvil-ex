---
name: vulcan-release
description: Prepare or review a Vulcan project's release readiness, notes and publication approval.
---

# Vulcan Release

Use the current release scope, applicable verification results, unresolved
obligations and approval record. Preparing notes is not permission to publish.

## Select the process

For `process_model`, use [Core CLI section 4.1](../../../docs/core/ORCHESTRATOR_CLI_GUIDE.md)
instead of legacy Gate steps. Do not add the marker or reinterpret an unsupported
model as legacy. Inspect selected `session.json` fields only if the assigned state
is missing or inconsistent.
For unmarked projects, use [legacy release](references/legacy-gates.md) for Gate 5.
Product evidence and verification follow [Product section 7](../../../docs/core/PRODUCT_PROFILE_BASELINE.md).

## Release outcome

Separate blocking defects from accepted backlog and keep notes tied to actual
changes and known limits. No new Run or Git evidence is needed just to write notes.
Use `release-pr --dry-run` for readiness; in the iterative process it is a
read-only candidate, not automatic publication or approval.
Perform externally visible publication only under explicit release authorization.
Report what was verified, published or still blocked without expanding that authority.
