# PoC Profile Template Set Strategy

> 목적: PoC profile을 audit 템플릿의 느슨한 버전으로 운영하지 않고, 별도의 경량 산출물 세트로 운영할 수 있는 방향을 정리한다.

## 1. 판단

PoC는 Phase 0만으로 끝낼 수 없다.

PoC의 목적은 아이디어 문서가 아니라 동작하는 코드, 실행 결과, 검증 가능한 증거로 핵심 가설을 확인하는 것이다.
따라서 Gate 흐름은 유지하되, audit 수준의 문서 개수와 정합성 검사를 그대로 요구하지 않는 별도 산출물 세트가 필요하다.

권장 방향은 다음과 같다.

```text
Audit:
Phase0 -> Gate1 -> Gate2 -> Gate3 -> Impl -> Gate4 -> Gate5
많은 산출물, 강한 traceability, 계약/증적 엄격도 높음

PoC:
Phase0 -> Gate1 -> Gate2 -> Gate3 -> Impl -> Gate4 -> Gate5
흐름은 유지, 산출물은 통합, 검사는 smoke/demo 중심
```

다만 실제 샘플에서 Gate 4까지 약 30분이 걸린 사례는 PoC profile이 아직 "빠른 실험"이라기보다 "경량 governance"에 가깝다는 신호다.
단순 화면/API PoC는 5~10분 안에 동작 결과를 확인하는 fast-track을 목표로 한다.
상세 전략은 `FAST-POC-AND-ENV-RUNWAY-STRATEGY.md`를 따른다.

## 2. 제안 산출물 세트

PoC profile은 기존 `docs/templates/`의 audit 문서를 모두 채우는 대신 `docs/templates/poc/` 아래의 통합 템플릿을 우선 사용한다.

| PoC 산출물 | 통합 대상 | 핵심 내용 |
| --- | --- | --- |
| `POC_REQUIREMENTS_TEMPLATE.md` | Phase 0, Gate 1 | 목표, 가설, 성공 기준, 핵심 시나리오, 제외 범위 |
| `POC_SYSTEM_DESIGN_TEMPLATE.md` | Gate 2 | 간단한 아키텍처, API/DB/UI 개요, 주요 기술 선택 |
| `POC_TEST_REPORT_TEMPLATE.md` | Gate 3, Gate 4, Gate 5 후보 판단 | 테스트 계획, 실행 결과, 로그/스크린샷, 결론 |

Gate 5 성격은 별도 문서로 늘리지 않고 `POC_TEST_REPORT_TEMPLATE.md`의 결론 섹션에 포함할 수 있다.

권장 결론 값은 다음과 같다.

| 결론 | 의미 |
| --- | --- |
| `Continue` | PoC 방향을 유지하고 다음 실험을 진행한다. |
| `Pivot` | 목표 또는 기술 선택을 바꿔 다시 실험한다. |
| `Stop` | 가설이 성립하지 않거나 투자 가치가 낮아 중단한다. |
| `Promote to solution/audit` | 제품화 또는 감리형 프로젝트로 승격한다. |

## 3. 승격 레이어

PoC 결과가 유효하다고 해서 바로 audit profile로 가야 하는 것은 아니다.
대부분의 제품형 작업에서는 중간에 solution profile을 두는 편이 자연스럽다.

```text
PoC
가설 검증, 빠른 구현, 최소 문서, smoke/demo 증적

        -> promote

Solution
제품 백로그, 운영 가능한 아키텍처, API/DB 계약, 회귀 테스트, 릴리즈 기준

        -> promote

Audit
상세 요구추적, 세부 설계, 공식 QA 증적, FIND/CR, 승인 문서
```

Solution profile은 audit의 가벼운 버전이 아니라 제품화/운영 가능 기준선이다.
PoC에서 확인한 가설과 데모 코드를 바로 감리 문서로 늘리기 전에, solution 단계에서 다음을 정리한다.

| 영역 | Solution에서 정리할 것 |
| --- | --- |
| 요구사항 | 제품 백로그, 핵심 사용자 시나리오, 릴리즈 범위 |
| 설계 | 운영 가능한 아키텍처, 주요 API/DB 계약, ADR |
| 구현 | 모듈 경계, public interface, 테스트 가능한 구조 |
| QA | 회귀 테스트, 주요 화면/API 증적 |
| 운영 | 설정, 배포, 로그, 장애 대응 기준 |
| 릴리즈 | 버전, 변경로그, backlog, release note |

PoC 산출물은 버리지 않고 승격의 입력 재료로 사용한다.

| PoC 산출물 | Solution 후보 | Audit 후보 |
| --- | --- | --- |
| `POC_REQUIREMENTS_TEMPLATE.md` | 제품 백로그, 핵심 시나리오 | Requirements Spec, AC, NREQ 후보 |
| `POC_SYSTEM_DESIGN_TEMPLATE.md` | 아키텍처, ADR, API/DB 계약 | SW Architecture, API Spec, DB Spec, Program Design 후보 |
| `POC_TEST_REPORT_TEMPLATE.md` | 회귀 테스트 후보, release note, backlog | Gate 3 Test Cases, Gate 4 Test Result, FIND/CR 후보 |

승격은 자동 덮어쓰기가 아니라 gap report 기반으로 수행한다.
권장 흐름은 `promote-profile --to solution|audit --dry-run` 같은 후보 명령으로 부족한 산출물, ID, 테스트, 증적을 보고하고, Orchestrator가 사용자 승인 후 보강 Run을 만든다.

## 4. PoC 추적성 기준

PoC의 추적성 목적은 감리 제출용 완결성이 아니라 실험 가설과 실행 결과의 연결이다.

Audit profile의 강한 추적 체인은 다음과 같다.

```text
REQ -> AC -> FUNC -> SCR -> PGM -> API -> DB -> SEC -> UT -> IT -> UI -> EV
```

PoC profile은 다음 정도의 최소 체인을 우선한다.

```text
Hypothesis/REQ -> API/DB/UI or Implementation -> Test -> Evidence -> Decision
```

즉, PoC에서도 목표, 성공 기준, 실행 결과, 미실행 사유는 명확해야 한다.
다만 모든 PGM/IF/MTH/UT/IT/UI 세부 ID를 강제하지 않는다.

## 5. UI/E2E 증적 경계

PoC에서는 빠른 커스텀 Playwright script나 데모 캡처를 smoke evidence로 사용할 수 있다.

다만 다음 경계를 지킨다.

- PoC smoke/demo는 `Pass` 대신 `Smoke Pass`, `Demo Evidence`, `Observed`처럼 표현할 수 있다.
- 실행하지 않은 UI 테스트를 `Pass`로 쓰지 않는다.
- PoC 결과를 solution/audit로 승격할 때는 `@playwright/test`, `npx playwright test`, report/trace/screenshot 기준의 공식 UI 증적으로 보강한다.
- audit/solution profile의 Gate 4 UI Pass는 커스텀 Playwright library script만으로 확정하지 않는다.

## 6. CLI와 검사 영향

PoC 전용 템플릿 세트를 도입하면 CLI도 profile별 필수 산출물 원장을 다르게 봐야 한다.

새 PoC 프로젝트는 `docs/poc/` 3종을 공식 작업 문서로 생성한다. Audit 산출물 템플릿 파일은 기본 생성하지 않고, Solution/Audit 승격 판단 시 후보 문서와 Gap Report로 만든다.

| 영역 | PoC 기준 |
| --- | --- |
| `gate-start` | PoC profile에서는 통합 산출물 초안을 생성하거나 다음 작성 후보를 안내한다. |
| `run-new` | 기본 필수가 아니며, 외부 worker, 긴 위임, 독립검수, 재현 가능한 실험 기록이 필요할 때 compact Run만 만든다. |
| `status --check` | audit 산출물 개수 누락이 아니라 PoC 필수 3종, 목표/성공 기준/실행 결과/결론 존재 여부를 본다. |
| `check-trace` | 상세 ID 누락보다 가설/요구사항과 실행 결과의 연결을 우선 본다. |
| `check-contract` | 상세 class/interface/public method보다 선언한 API/DB/UI/진입점이 실제 코드에 존재하는지 가볍게 확인한다. |
| Dashboard | audit 문서 목록이 비어 보이지 않도록 PoC 산출물 묶음을 별도 표시한다. |

## 6.1 구현환경 Runway와 BW-000

PoC에서 `BW-000 implementation-scaffold`를 기본 생성하면 빠른 실험의 장점이 줄어든다.
따라서 PoC는 기본적으로 첫 구현 worker가 환경 생성, hello/build smoke, 핵심 기능 구현을 함께 수행한다.

모든 profile에서 개발환경 준비는 업무 기능 구현과 분리된 Environment Readiness Track으로 앞당길 수 있다.
이 Track은 Phase 0~Gate 3 동안 설계 문서를 보며 폴더 구조, dependency, lint/build/test script, hello world/health check, build smoke를 준비한다.
업무 요구사항 구현, 테스트 Pass 확정, 추적표 Implemented/Verified 반영은 금지한다.

Audit/Solution에서는 공식 계약 skeleton이 필요하거나 환경 준비가 기능 구현 수준으로 커질 때만 `BW-000`을 사용한다.
PoC에서는 `BW-000`을 기본값이 아니라 fallback으로 둔다.

## 7. Agy 제안 검토 반영

`sample-ex-agy-0608-1/docs/poc_profile_proposal.md`의 핵심 제안은 채택할 가치가 있다.

받을 부분:

- PoC 문서를 3개로 통합한다.
- PoC traceability를 핵심 가설과 결과 중심으로 줄인다.
- PoC에서 `check-contract`, `check-trace`를 audit 수준으로 적용하지 않는다.
- PoC 성공 후 solution/audit 승격 경로를 둔다.

수정해야 할 부분:

- 원 제안의 중첩 Markdown code fence 예시는 실제 템플릿 파일로 옮길 때 깨질 수 있으므로 4중 fence 또는 개별 파일로 분리한다.
- `node scripts/run-e2e.js` 같은 커스텀 Playwright script는 PoC smoke/demo로는 허용하되 audit/solution UI Pass로 쓰지 않는다.
- 경미한 버그를 현재 Wave 안에서 바로 고칠 수 있더라도 `Fix Log` 또는 `Experiment Iteration`에는 남긴다.
- `python vulcan.py session --profile audit`처럼 현재 CLI에 없는 명령은 문서에 현재 기능처럼 쓰지 않는다. profile 승격은 별도 `profile-switch` 또는 `promote-profile` 후보로 설계한다.
- `run-integrate`를 main 병합으로 설명하지 않는다. worker 결과는 현재 workspace 또는 integration branch에 통합하고, main 반영은 Gate 5 release 흐름에서 처리한다.

## 8. 이번 주 검증 계획

1차 PoC template set 검증은 다음 목표로 진행한다.

1. `docs/templates/poc/`에 3개 템플릿 초안을 추가한다. (1차 반영)
2. `init --profile poc` 또는 `upgrade`된 샘플에서 PoC 필수 산출물 3종만으로 Phase 0~Gate 5를 끝까지 진행해 본다.
3. `status --check`, `run-check`, `check-trace`가 audit 문서 누락으로 불필요하게 막히는 지점을 기록한다. (PoC 3종 원장 기반 `check-trace` 1차 반영)
4. 커스텀 Playwright smoke와 공식 `@playwright/test` 증적 경계를 실제 QA 문서에서 확인한다.
5. PoC 결과를 `Continue`, `Pivot`, `Stop`, `Promote to solution/audit` 중 하나로 정리할 수 있는지 확인한다.

## 9. 후속 후보

- `profile-switch` 또는 `promote-profile` CLI 설계
- PoC 산출물 3종 기반 `status --check` 원장
- PoC Dashboard 문서 묶음 표시
- PoC fixture smoke 추가
- PoC -> Solution 승격 Gap report
- Solution -> Audit 승격 Gap report
