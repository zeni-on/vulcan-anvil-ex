# Product Profile Sample Rerun - 2026-06-25

## Purpose

Validate the current Product profile with a real sample project instead of only relying on fixture smoke.

Sample project:

```text
C:\Users\user\Documents\antig-workspace\sample-ex-product-0625-1
```

Scenario:

- Single-user TODO app.
- Local execution.
- Core flows: add TODO, toggle completed, delete TODO.

## Commands

Initial framework checks in `vulcan-anvil-ex`:

```powershell
python scripts/regression/run_fixture_smoke.py
python scripts/regression/run_audit_smoke.py
```

Sample initialization:

```powershell
python vulcan.py init C:\Users\user\Documents\antig-workspace\sample-ex-product-0625-1 sample-ex-product-0625-1 --profile product --primary codex-cli
```

Sample checks:

```powershell
python vulcan.py status
python vulcan.py profile-status
python vulcan.py doctor --json
python vulcan.py status --check
```

Gate progression tested:

```powershell
python vulcan.py session --gate phase0 --status done --approved --approval-evidence "Product sample rerun approved by user request"
python vulcan.py gate-start gate1
python vulcan.py session --gate gate1 --status done --approved --approval-evidence "Product sample rerun: brief scenarios accepted"
python vulcan.py gate-start gate2
python vulcan.py session --gate gate2 --status done --approved --approval-evidence "Product sample rerun: architecture and product contracts accepted"
python vulcan.py gate-start gate3
python vulcan.py session --gate gate3 --status done --approved --approval-evidence "Product sample rerun: regression plan accepted"
python vulcan.py branch-start impl
python vulcan.py gate-start impl
python vulcan.py wave-start BW-001 --title "Build Wave BW-001 Product TODO core implementation" --trace-seed SCN-001
python vulcan.py execute --dry-run --run-id RUN-001 --json
```

## Observations

### Product profile flow

- `init --profile product` generated the expected `docs/product/` document set.
- Gate-level Orchestrator Plan Runs were skipped for Product, as intended.
- `PRODUCT_BRIEF.md` was enough to carry Phase 0 and Gate 1 once goal, user, success criteria, scope, and scenarios were filled.
- Gate 2 blocked until runtime, data store, API/data/UI contracts, and architecture gaps were resolved.
- Gate 3 blocked until the regression plan in `REGRESSION_AND_RELEASE_REPORT.md` was filled.
- Planned regression rows were accepted at Gate 3 as long as they were clearly marked as not yet executed.

### Handoff quality

`wave-start BW-001 --trace-seed SCN-001` produced a Product Build Wave Run that:

- expanded sibling scenarios and related IDs from Product trace context,
- used `docs/product/` documents as working documents,
- did not pull audit artifacts into the worker input,
- passed both `run-check` and `run-preflight`,
- produced a native delegation dry-run sidecar candidate.

### Discovered issue

`execute --dry-run --json` initially inferred the generated full-stack Product Build Wave as:

```json
"inferred_role": "build-frontend"
```

This was misleading because the Run included API, data, UI, backend, frontend, static, and test scope. The correct generic role is:

```json
"inferred_role": "build"
```

The issue was fixed in `infer_execution_role()` and locked into `scripts/regression/run_fixture_smoke.py`.

## Verification After Fix

```powershell
python -m py_compile vulcan.py scripts/regression/run_fixture_smoke.py
python scripts/regression/run_fixture_smoke.py
```

Result:

- `py_compile`: pass
- `run_fixture_smoke.py`: pass, 81 steps
- Sample `execute --dry-run --run-id RUN-001 --json`: `inferred_role` changed to `build`

## Current Sample State

The sample is intentionally left at the implementation handoff point:

- branch: `dev`
- gate: `impl`
- active wave: `BW-001`
- active Run: `RUN-001_build-wave-BW-001_build-wave-bw-001-product-todo-core-implementation_v0.1.md`
- worker implementation not executed yet

This is enough for the roadmap item "Product profile actual sample rerun" to validate Product document flow and worker handoff quality. Full implementation and Gate 4 QA should be a separate sample rerun because it involves native worker execution, code generation, tests, and evidence collection.

## Follow-up

- Continue the same sample with native worker implementation only when testing implementation throughput is the goal.
- Keep adding fixture cases only when sample reruns reveal repeated or blocking failures.
- Do not merge experimental scaffold automation until a sample proves it reduces Product Run drafting or skeleton setup time.
