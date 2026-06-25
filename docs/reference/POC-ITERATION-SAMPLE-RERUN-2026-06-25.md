# PoC Iteration Sample Rerun - 2026-06-25

> 목적: PoC profile이 빠른 산출물 생성보다 반복 실험 기록 복원성에 맞게 동작하는지 실제 샘플로 확인한다.

## Sample

- project: `sample-ex-poc-repeat-0625-1`
- profile: `poc`
- request focus: repeated TODO experiment, iteration records, smoke evidence
- final gate: `completed`
- branch: `dev`

## What Was Tested

The sample used only the PoC document set:

- `docs/poc/POC_REQUIREMENTS.md`
- `docs/poc/POC_SYSTEM_DESIGN.md`
- `docs/poc/POC_TEST_REPORT.md`

The PoC asked whether a small TODO experiment can preserve:

- the goal and success criteria,
- the lightweight API/data/UI shape,
- the reason and result for each experiment iteration,
- smoke evidence connected to the final decision.

## Observed Flow

### Phase 0 Guard

Initial `status --check` correctly blocked placeholder goals:

- `PoC 목표가 TBD입니다.`
- `성공 기준이 TBD입니다.`

After the goal, hypothesis, core scenarios, and scope were filled, Phase 0 passed.

### Premature Implementation Guard

An early attempt to add `poc_app.py` and `tests/` during Phase 0 was blocked:

```text
프로세스 위반: 현재 Gate는 phase0인데 구현/테스트 파일 후보가 존재합니다 (tests)
```

This is the right behavior. PoC is lighter than Audit, but it still should not create implementation/test files before the approved implementation phase.

### Missing Evidence Guard

The sample then revealed a real gap.

If `POC_TEST_REPORT.md` already says `Smoke Pass` but the evidence file does not exist, the old checker could report implementation progress as complete.

The fix:

- PoC implementation stats now require an existing pass evidence file before marking REQ items implemented.
- `status --check` now blocks `Pass` / `Smoke Pass` results without an existing evidence file.
- `scripts/regression/run_fixture_smoke.py` includes `poc-pass-blocks-missing-evidence`.

Expected diagnostic:

```text
docs/poc/POC_TEST_REPORT.md에 Pass/Smoke Pass 결과가 있으나 실제 증적 파일을 찾을 수 없습니다.
```

### Valid Impl Evidence

After entering Impl, the sample added:

- `poc_app.py`
- `tests/test_poc_app.py`
- `docs/poc/evidence/unittest.log`

Verification:

```powershell
python -m unittest discover -s tests -v
python vulcan.py status --check
```

Result:

- 3 unit tests passed.
- `implementation` became `3 / 3`.
- `status --check` passed.
- Gate 4 and Gate 5 were completed with the PoC decision `Continue`.

## Retrospective

PoC profile is usable for repeated experiments if the following remain true:

- Iterations are written as `ITER-001`, `ITER-002`, `ITER-003` in `POC_TEST_REPORT.md`.
- A `Pass` or `Smoke Pass` statement points to an actual evidence file.
- PoC still respects Gate boundaries for implementation and tests.
- Product promotion remains a later decision, not an automatic conversion.

The important improvement from this sample is not more automation. It is preventing optimistic PoC reports from claiming success before evidence exists.

