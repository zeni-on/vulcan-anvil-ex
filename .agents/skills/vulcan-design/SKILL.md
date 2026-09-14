---
name: vulcan-design
description: Create or review design contracts for a Vulcan project.
---

# Vulcan Design

Use the assigned requirements, acceptance criteria, open decisions and design scope.
Read only the contract sources affected by the design.

## Select the process

For `process_model`, use [Core CLI section 4.1](../../../docs/core/ORCHESTRATOR_CLI_GUIDE.md)
instead of legacy Gate steps. Do not add the marker or reinterpret an unsupported
model as legacy. Inspect selected `session.json` fields only if the assigned state
is missing or inconsistent.
For unmarked projects, use [legacy design](references/legacy-gates.md) for Gate 2 work.
Product scope and verification follow [Product section 7](../../../docs/core/PRODUCT_PROFILE_BASELINE.md).

## Design outcome

Use [Product document writing](../../../docs/core/PRODUCT_DOCUMENT_WRITING.md)
when authoring Product contracts: keep one owned source and link from the ledger.
Preserve requirements, API/data/UI/security constraints and existing approved sources.
Use [design sequence](../../../docs/core/GATE2_DESIGN_SEQUENCE.md) only when the
design order or a legacy contract dependency is unclear.

Resolve blocking conflicts or scope changes with the Orchestrator; continue other
authorized design work. Design review does not imply implementation permission.
