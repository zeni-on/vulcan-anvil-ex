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

Native worker implementation:

```text
worker: Curie
mode: native subagent
run: RUN-001
```

Post-worker checks:

```powershell
python -m compileall app backend src
python -m pytest
npm test
npm run build
python vulcan.py run-check docs/runs/RUN-001_build-wave-BW-001_build-wave-bw-001-product-todo-core-implementation_v0.1.md
python vulcan.py run-preflight docs/runs/RUN-001_build-wave-BW-001_build-wave-bw-001-product-todo-core-implementation_v0.1.md
python vulcan.py wave-complete BW-001 --status Verified
python vulcan.py sync-session
python vulcan.py status --check
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

### Implementation execution

The generated Run was then executed with a native worker. The worker produced a small FastAPI + SQLite-backed TODO app with static UI assets:

- `app/main.py`
- `app/store.py`
- `static/index.html`
- `static/styles.css`
- `static/app.js`
- `tests/test_todo_api.py`
- `requirements.txt`
- `package.json`
- `docs/product/evidence/BW-001_impl_self_check.md`
- the generated `RUN-001` Build Wave document

The Orchestrator re-ran the worker self-check commands and confirmed:

- Python compile: pass
- pytest: pass, 5 tests
- `npm test`: pass
- `npm run build`: pass
- `run-check`: pass
- `run-preflight`: pass
- `wave-complete BW-001 --status Verified`: pass
- `status --check`: impl can transition to Gate 4

### Discovered stats issue

After the implementation was verified, Product status still showed implementation progress as `0/0`.
The Product profile does not use the audit `docs/artifacts/01-requirements` + full traceability matrix path, so the default implementation stats parser was not reading `docs/product/PRODUCT_TRACEABILITY.md`.

The fix:

- `compute_stats()` now uses Product trace rows for `product`/`solution` profiles.
- `status --json` surfaces the computed Product implementation stats instead of stale `session.json` counters.
- `refresh_session_stats()`, `wave-start`, and `wave-complete` no longer overwrite computed profile stats with stale implementation values.
- `scripts/regression/run_fixture_smoke.py` now checks that the completed Product fixture reports `3/3` implemented requirements.

## Verification After Fix

```powershell
python -m py_compile vulcan.py scripts/regression/run_fixture_smoke.py
python scripts/regression/run_fixture_smoke.py
python scripts/regression/run_audit_smoke.py
```

Result:

- `py_compile`: pass
- `run_fixture_smoke.py`: pass, 82 steps
- `run_audit_smoke.py`: pass, 12 steps
- Sample `execute --dry-run --run-id RUN-001 --json`: `inferred_role` changed to `build`
- Sample `status --json`: implementation requirements changed to `3/3`
- Sample `sync-session`: implementation requirements changed to `3/3`
- Sample `status --check`: impl to Gate 4 transition ready

## Gate 4 QA Rerun

The same sample was then continued through Gate 4.

Gate 4 execution commands:

```powershell
python vulcan.py session --gate impl --status done --approved --approval-evidence "BW-001 Verified; compileall, pytest, npm test, npm run build, run-check, run-preflight passed; Product implementation stats 3/3"
python vulcan.py doctor --json
python vulcan.py doctor
python -m compileall app backend src
python -m pytest
npm test
npm run build
npx --yes playwright test docs/product/evidence/G4_QA002_product_ui.spec.js --reporter=line --output=docs/product/evidence/playwright-output
python vulcan.py sync-session
python vulcan.py status --check
python vulcan.py session --gate gate4 --status done --approved --approval-evidence "Product Gate4 QA completed: doctor warn only, compileall/pytest/npm test/npm build passed, npx playwright test passed with UI screenshot evidence"
```

Gate 4 evidence created in the sample:

- `docs/product/evidence/G4_QA000_doctor.json`
- `docs/product/evidence/G4_QA000_doctor.log`
- `docs/product/evidence/G4_QA001_compileall.log`
- `docs/product/evidence/G4_QA001_pytest.log`
- `docs/product/evidence/G4_QA001_npm_test.log`
- `docs/product/evidence/G4_QA001_npm_build.log`
- `docs/product/evidence/G4_QA002_playwright.log`
- `docs/product/evidence/G4_QA002_product_ui.spec.js`
- `docs/product/evidence/G4_QA002_product_ui.png`

Gate 4 result:

- `doctor`: pass 10, warn 2, fail 0, info 2
- Warnings:
  - `node_modules` missing
  - `@playwright/test` not pinned in `package.json`
- Command QA: compileall, pytest, npm test, npm build passed
- UI QA: `npx --yes playwright test ...` passed, 1 test
- Product trace/report updated to Gate 4 Pass
- Gate 4 completed and the sample is now at Gate 5 pending

### Discovered Gate 4 readiness issue

Before executing Gate 4 QA, `status --check` incorrectly allowed transition readiness while Product regression rows still said `Not run yet | Planned`.
The Product checker already had a planned-regression guard, but its pattern did not include the Product template phrase `Not run yet`.

The fix:

- Product Gate 4 planned regression detection now treats `Not run yet | Planned` as a blocking execution result.
- `scripts/regression/run_fixture_smoke.py` now verifies the real `status --json --check` path fails while Product Gate 4 regression rows remain not executed.

## Current Sample State

The same sample was continued through Gate 5:

- branch: `dev`
- gate: `completed`
- Build Wave: `BW-001` Verified
- implementation requirements: `3/3`
- Gate 4 QA: completed
- Gate 5 release approval: completed
- `release-pr --dry-run`: passed
- active Runs: none
- active Waves: none

This is enough for the roadmap item "Product profile actual sample rerun" to validate Product document flow, worker handoff quality, native implementation, Product implementation stats, Product Gate 4 QA evidence flow, Gate 5 release approval, and Product `release-pr --dry-run` behavior.

## Gate 5 Release Approval

Commands verified in the sample:

```powershell
python vulcan.py release-pr --dry-run
python vulcan.py status --check
python vulcan.py session --gate gate5 --status done --approved --approval-evidence "release-pr dry-run passed; status --check passed; DOC-PM-G5-001 approved; ISSUE-QA-001 deferred as non-blocking"
```

Observed results:

- `release-pr --dry-run` generated `.vulcan/release/release-pr-body.md`.
- The PR body used Product evidence, not Audit-only QA documents.
- `docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md` was required as the release approval source of truth.
- `ISSUE-QA-001` was accepted as a non-blocking deferred issue in `docs/backlog/DOC-PM-OPS-001_Backlog_v0.1.md`.
- Final `status --check` reported the project as completed.

### Gate 5 readiness bug found

Before the release approval document existed, `release-pr --dry-run` correctly failed, but `status --check` still reported transition readiness.

The root cause was that `PRODUCT_REQUIRED_ARTIFACTS_BY_GATE` did not include `docs/artifacts/07-release/DOC-PM-G5-001_Release-Approval_v0.1.md` for `gate5` and `completed`.

The fix:

- Product Gate 5 and completed required artifacts now include the release approval document.
- `scripts/regression/run_fixture_smoke.py` now verifies that Product `status --json --check` fails at Gate 5 when the release approval document is missing.

## Follow-up

- Keep adding fixture cases only when sample reruns reveal repeated or blocking failures.
- Do not merge experimental scaffold automation until a sample proves it reduces Product Run drafting or skeleton setup time.
