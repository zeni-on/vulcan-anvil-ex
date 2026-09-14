---
name: vulcan-qa
description: Coordinate acceptance testing and QA results in a Vulcan project.
---

# Vulcan QA

Use the assigned QA scope, test plan and verification or fix authority.
A verification-only worker returns fix candidates; an assigned fix does not
authorize unrelated contract changes.

## Select the process

For `process_model`, use [Core CLI section 4.1](../../../docs/core/ORCHESTRATOR_CLI_GUIDE.md)
instead of legacy Gate steps. Do not add the marker or reinterpret an unsupported
model as legacy. Inspect selected `session.json` fields only if the assigned state
is missing or inconsistent.

In Product acceptance, `execute --dry-run --json` without a Run prepares the native
handoff and an empty return request. It does not launch a delegate or approve QA.
Follow Core 4.1 for verification-only assignment, `execute --verify`, result review
and the separate acceptance decision.

For unmarked projects, read [legacy QA](references/legacy-gates.md) when executing
Gate 4. Product uses [Product section 7](../../../docs/core/PRODUCT_PROFILE_BASELINE.md)
for scoped checks, permitted fixes and result reuse, not four mandatory Runs.

## Results

Run the applicable agreed tests; preserve failure, missing and environment-blocked
results. Product/Audit official UI Pass requires `@playwright/test` and
`npx playwright test`; custom browser scripts are auxiliary evidence only.
Use [Product document writing](../../../docs/core/PRODUCT_DOCUMENT_WRITING.md)
for owned test definitions and execution records. Actual command success and a
worker summary are not QA approval. Report-only edits do not justify rerunning
unchanged product tests. Keep required security, evidence and review obligations.
