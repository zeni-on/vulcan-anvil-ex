# Product Fixture Smoke Strategy

> 상태: v0.1
> 목적: Product profile이 Audit 산출물 기준에 끌려가지 않으면서도 릴리즈 가능한 제품 기준선을 유지하는지 fixture와 실제 샘플로 반복 확인한다.

## 1. 배경

Product profile은 PoC보다 무겁고 Audit보다 가볍다.
따라서 회귀 검증도 Audit fixture를 그대로 통과시키는 방식이 아니라, Product가 의도한 문서 세트와 릴리즈 판단 기준을 별도로 확인해야 한다.

현재 `scripts/regression/run_fixture_smoke.py`는 `scripts/regression/fixtures/simple-todo-product/` fixture를 사용해 Product profile의 핵심 회귀를 확인한다.
이 smoke는 AI worker를 호출하지 않고, 정규화된 완료 프로젝트 모양을 임시 프로젝트에 적용한 뒤 CLI와 문서 해석이 깨지지 않았는지 본다.

## 2. 확인할 것

Product fixture smoke는 다음을 보장해야 한다.

| 영역 | 확인 기준 |
| --- | --- |
| Product 문서 세트 | `docs/product/PRODUCT_BRIEF.md`, `PRODUCT_ARCHITECTURE.md`, `ADR_LOG.md`, `PRODUCT_CONTRACTS.md`, `PRODUCT_TRACEABILITY.md`, `REGRESSION_AND_RELEASE_REPORT.md`가 Product 원장으로 동작한다. |
| Product release evidence | `release-pr --dry-run`이 Product 원장, backlog, Gate 5 승인서를 evidence로 사용하고 Audit 전용 QA Finding/Test Result/Traceability Matrix를 필수로 요구하지 않는다. |
| Product traceability | `SCN`, `REQ`, `API`, `DATA`, `UI`, `REG` ID가 보존되고 `status --check`에서 완료 프로젝트로 해석된다. |
| Product Build Wave | `wave-start --trace-seed` 또는 Run 문서 해석에서 Product 관련 ID가 누락되지 않는다. |
| ADR empty-state | 의사결정이 없으면 `ADR-NONE`이 정상이다. placeholder ADR을 억지로 채우지 않는다. |
| Regression report | 주요 회귀 테스트와 known issue가 Product 릴리즈 판단에 필요한 수준으로 남는다. |
| QA/doctor 경계 | 환경 진단은 `doctor` 또는 QA-000 입력으로 분리하고, 제품 테스트 Pass/Fail을 대신하지 않는다. |

## 3. 실행 명령

로컬 회귀 smoke:

```powershell
python scripts/regression/run_fixture_smoke.py
```

시간이 오래 걸리거나 실패 지점을 보존해야 할 때:

```powershell
python scripts/regression/run_fixture_smoke.py --keep --timeout-seconds 240
```

`--keep`로 생성된 임시 프로젝트에서는 다음을 직접 확인한다.

```powershell
python vulcan.py status --check
python vulcan.py release-pr --dry-run
python vulcan.py profile-gap --to audit
python vulcan.py doctor
```

`doctor`는 환경 진단이다.
`doctor`의 `warn`/`fail`은 Product 결함으로 바로 확정하지 않고, QA-000 또는 ISSUE 후보로 분리한다.

## 4. 실제 샘플 재실행 기준

fixture smoke는 빠른 회귀 확인이고, 실제 샘플 재실행은 Orchestrator 운영 감각을 확인한다.
Product 샘플 재실행은 다음 기준으로 평가한다.

| 단계 | 합격 기준 |
| --- | --- |
| Init | `--profile product`로 시작하고 `docs/product/` 6종 문서를 생성한다. |
| Phase 0~Gate 3 | Product 원장 문서를 중심으로 목표, 시나리오, 계약, 회귀 기준을 채운다. Audit 산출물을 없다는 이유로 임의 생성하지 않는다. |
| Impl | native worker/subagent/thread/native branch agent를 기본으로 사용하고, Run이 필요하면 Product 문서 세트를 입력으로 삼는다. |
| Gate 4 | QA-000에서 환경 준비와 `doctor` 필요 여부를 분리한다. QA-001~QA-003은 Product 회귀 결과와 evidence를 `REGRESSION_AND_RELEASE_REPORT.md`에 연결한다. |
| Gate 5 | `release-pr --dry-run`이 Product evidence 기준으로 통과한다. Audit 전용 문서 부재가 차단 사유가 되면 실패다. |
| Dashboard | profile, status, Product 문서, evidence, delegation 기록이 누락 없이 보인다. |

## 5. 실패 분류

Product fixture 또는 실제 샘플에서 실패가 나오면 다음처럼 분류한다.

| 분류 | 의미 | 조치 |
| --- | --- | --- |
| Product rule gap | Product 기준 자체가 불명확하거나 문서가 부족하다. | `PRODUCT_PROFILE_BASELINE.md` 또는 Product template 보강 |
| Audit leakage | Product인데 Audit 전용 산출물을 요구한다. | `status --check`, `release-pr`, `profile-gap` 기준 수정 |
| Environment blocked | npm, Playwright, runner, Dashboard, port, cache 문제다. | `doctor`, QA-000, ISSUE 후보로 분리 |
| Real product defect | 실제 기능/계약/회귀 테스트가 실패한다. | FIND 또는 qa-fix-loop 후보 |
| Dashboard visibility issue | 문서는 맞는데 Dashboard 표시가 부족하다. | Dashboard parser/UI 보강 후보 |

## 6. 다음 고정 후보

다음 fixture 확장은 실제 Product 샘플 재실행에서 나온 반복 실패를 기준으로 추가한다.

- Product `doctor --json` 결과를 QA-000 결과서에 자동 연결할지 여부
- Product `profile-gap --to audit`이 Audit 전환 gap만 보여주고 현재 Product 완료를 훼손하지 않는지
- Product Dashboard에서 `SCN/API/DATA/UI/REG` 추적이 충분히 읽히는지
- Product release body가 known issue/backlog를 지나치게 관대하게 처리하지 않는지

## 7. 판단

Product profile 안정화의 다음 단계는 새 기능 추가가 아니라, fixture smoke와 실제 샘플 재실행으로 같은 실패가 반복되지 않는지 확인하는 것이다.
이 문서는 그 확인 기준을 고정한다.
