# SI Sequential Gate + Module Parallel Ideal

> 상태: ideal draft v0.1
> 목적: Vulcan-Anvil Ex가 지향할 SI형 개발 프로세스 모델을 정리한다. 이 문서는 아직 Core 규약이 아니라, 향후 Core/Adapter/Dashboard 개선을 위한 참고 설계다.

## 1. 문제의식

개발 프로세스에는 Agile, Lean Startup, Waterfall, Hybrid 등 여러 모델이 있다.
하지만 SI 프로젝트 현실에서는 실제 구현에 들어가기 전까지는 대부분의 판단이 순차적으로 진행된다.

요구사항이 정리되지 않은 상태에서 설계를 병렬로 나누기 어렵고, 공통 설계가 고정되지 않은 상태에서 구현을 병렬화하면 통합 단계에서 큰 비용이 발생한다.

따라서 Vulcan-Anvil Ex의 이상적인 방향은 다음에 가깝다.

```text
초기 단계 = 순차 Gate 중심
설계 완료 후 = 모듈/서비스 경계 기준 병렬 구현
각 Gate와 Wave 사이 = 교차검증과 통합 검증
```

즉 Ex는 단순히 많은 에이전트를 동시에 돌리는 시스템이 아니다.
Ex는 사람이 승인해야 하는 순차 판단 지점을 보존하면서, 병렬화 가능한 구현 단위만 안전하게 분리하는 Orchestrated Delivery Framework다.

## 2. 기본 결론

SI형 프로젝트에서는 다음 원칙이 현실적이다.

1. Phase 0, Gate 1, Gate 2, Gate 3는 기본적으로 순차 진행한다.
2. 구현 병렬화는 요구사항, 공통 설계, 테스트 기준이 일정 수준 고정된 뒤 시작한다.
3. 병렬화 단위는 기능 하나가 아니라 모듈, 서비스, 포털, 배치, 공통 컴포넌트 같은 경계가 명확한 단위여야 한다.
4. 병렬 구현 결과는 Wave 단위로 통합하고, 설계/요구사항/테스트 기준에 대한 교차검증을 거친다.
5. 교차검증은 구현 속도를 늦추는 절차가 아니라, 뒤늦은 통합 실패와 범위 오염을 줄이는 장치다.

한 문장으로 요약하면 다음과 같다.

```text
Ex는 SI형 순차 Gate를 유지하되, 설계가 고정된 뒤 모듈 단위 Build Wave를 병렬화하고, 각 Gate와 Wave 사이에 교차검증을 넣는 전달 프레임워크다.
```

## 3. 순차로 가야 하는 영역

다음 단계는 기본적으로 순차 진행이 적합하다.

| 단계 | 순차가 필요한 이유 |
| --- | --- |
| Phase 0 Discovery | 목표, 범위, 제약, 이해관계자, 위험이 먼저 정리되어야 한다. |
| Gate 1 Requirements | 요구사항, 비기능, 인수기준이 정리되어야 설계 범위가 정해진다. |
| Gate 2 Shared Design | 공통 아키텍처, 데이터, 인증, API, 화면 구조가 합의되어야 모듈을 나눌 수 있다. |
| Gate 3 Test Design | AC, 보안, 비기능, UI 기준이 테스트 가능한 형태로 내려와야 구현 검증이 가능하다. |

이 구간에서 무리하게 병렬화하면 다음 문제가 생긴다.

- 모듈마다 용어와 데이터 해석이 달라진다.
- API request/response contract가 맞지 않는다.
- 화면과 backend 책임 경계가 흔들린다.
- 보안/권한 기준이 모듈별로 다르게 구현된다.
- 테스트 기준이 없어 구현 완료 판정이 주관화된다.
- 통합 단계에서 CR인지 FIND인지 판단하기 어려워진다.

따라서 구현 전까지는 빠른 병렬화보다 설계 정합성과 교차검증이 더 중요하다.

## 4. 병렬화 가능한 영역

설계와 테스트 기준이 고정된 뒤에는 다음과 같은 단위로 병렬 구현할 수 있다.

| 병렬 단위 | 예시 |
| --- | --- |
| API Gateway / 공통 서비스 | 인증 연계, routing, 공통 error, rate limit |
| 업무 서비스 모듈 | 게시판, 회원, 결제, 신청, 승인, 통계 등 |
| 사용자 포털 | 사용자 화면, 사용자 API 연동, 사용자 UX flow |
| 관리자 포털 | 관리 화면, 권한별 메뉴, 운영 기능 |
| 배치 프로세스 | 정산, 통계, 파일 수집/전송, 알림 batch |
| 공통 UI 컴포넌트 | layout, form, table, modal, validation message |
| 외부 연계 adapter | legacy API, SSO, payment, notification, storage |
| 데이터/코드 공통 모듈 | 공통 코드, 용어, enum, validation, mapper |

이 병렬화는 “각자 알아서 구현”이 아니다.
각 모듈은 사전에 합의된 contract 안에서만 독립적으로 움직인다.

## 5. 병렬 구현 전 고정해야 하는 것

모듈별 병렬 구현 전에 다음 항목은 최소한 합의되어야 한다.

| 구분 | 고정 대상 |
| --- | --- |
| 용어 | 업무 용어, 표준 단어, 코드명, enum |
| 데이터 | 주요 entity, PK/FK, ownership, migration 기준 |
| API | endpoint, method, request/response schema, error code |
| 인증/권한 | session/token, role, permission, menu visibility |
| 화면 | screen id, route, menu, layout shell, 상태 정의 |
| 배치 | input/output, file format, schedule, retry, idempotency |
| event/message | topic, payload, producer/consumer, ordering, retry |
| 테스트 | 단위/통합/UI/evidence 기준, AC 연결 |
| 추적성 | REQ, AC, FUNC, SCR, PGM, DB, SEC, UT, IT, UI ID 연결 |

이 항목이 고정되지 않으면 병렬 구현은 속도 향상이 아니라 리스크 증폭이 된다.

## 6. 권장 전체 흐름

### 6.1 Phase 0: Discovery

목표:

- 프로젝트 배경과 목적 정리
- 사용자와 이해관계자 식별
- 범위 후보와 비범위 후보 정리
- 기존 시스템, 외부 연계, 제약 확인
- 주요 위험과 질문 도출

주요 산출물:

- Project Brief
- Stakeholder Scope
- Risk / Assumption
- AS-IS / TO-BE 초안
- 질문 목록

병렬화:

- 원칙적으로 병렬 구현 없음
- 자료 조사나 현행 분석은 subtask로 나눌 수 있으나, 결론은 Orchestrator가 통합한다.

### 6.2 Gate 1: Requirements

목표:

- REQ, NREQ, AC 정의
- 업무 흐름과 사용자 시나리오 정리
- 범위와 비범위 명확화
- 요구사항 추적표 초안 작성

주요 산출물:

- Requirements Spec
- Traceability Matrix 초안
- Acceptance Criteria
- Non-functional Requirements

교차검증:

- Phase 0 목표와 Gate 1 요구사항의 정합성 확인
- 빠진 이해관계자나 범위 확장 여부 확인
- AC가 검증 가능한 문장인지 확인

### 6.3 Gate 2: Shared Design + Module Design

목표:

- 전체 아키텍처 정의
- 공통 데이터/보안/개발표준 확정
- 기능, 화면, 프로그램, DB 설계 작성
- 모듈/서비스 경계 정의
- 병렬 구현 가능한 단위 식별

주요 산출물:

- SW Architecture
- Function Spec
- Screen Spec
- Program Design
- Database Spec
- API Spec
- Security Guide
- Development Standard
- Module Slicing 문서

교차검증:

- Gate 1 REQ/NREQ/AC가 설계로 누락 없이 전개됐는지 확인
- 설계가 승인 범위를 임의 확장하거나 축소하지 않았는지 확인
- 공통 설계와 모듈 설계가 충돌하지 않는지 확인
- 병렬 구현 경계가 실제로 분리 가능한지 확인

### 6.4 Gate 2 내부: Module Slicing / Parallelization Readiness

별도 Gate로 만들 필요는 없지만, Gate 2 안에 명시적인 section 또는 산출물로 두는 것이 좋다.

권장 문서 위치 예시:

```text
docs/artifacts/02-design/module/MODULE-SLICING.md
```

문서에 포함할 항목:

- 모듈 ID
- 모듈 이름
- 책임 범위
- owning data
- 제공 API
- 소비 API
- 연결 화면
- batch/event 연계
- 선행 의존성
- 병렬 구현 가능 여부
- 통합 테스트 기준
- 관련 REQ/AC/FUNC/SCR/PGM/DB/SEC/UT/IT/UI ID

예시:

| Module ID | 이름 | 병렬 가능 | 선행 의존성 | 주요 산출물 |
| --- | --- | --- | --- | --- |
| MOD-GW | API Gateway/Auth | 부분 가능 | 인증/권한 설계 확정 | SEC, API, PGM |
| MOD-USER-PORTAL | 사용자 포털 | 가능 | 화면 route, API contract | SCR, UI, PGM |
| MOD-ADMIN-PORTAL | 관리자 포털 | 가능 | 권한 matrix, API contract | SCR, UI, PGM |
| MOD-BATCH | 배치 프로세스 | 가능 | DB schema, file format | PGM, DB, IT |
| MOD-COMMON-UI | 공통 UI | 선행 권장 | design token, layout | SCR, UI |

### 6.5 Gate 3: Test Design

목표:

- AC를 테스트 케이스로 전개
- 보안/권한/비기능 검증 기준 정의
- UI 증적 기준 정의
- 모듈별 단위/통합 테스트 범위 정의
- Wave 완료 판정 기준 정리

주요 산출물:

- Test Plan
- Test Case
- UI Evidence Criteria
- Integration Test Criteria
- Security Test Criteria

교차검증:

- 모든 AC가 테스트로 연결됐는지 확인
- Gate 2 Module Slicing 결과와 테스트 범위가 맞는지 확인
- 통합 테스트가 모듈 간 contract를 검증하는지 확인

### 6.6 Implementation: Build Wave 기반 병렬 구현

구현은 Build Wave 단위로 진행한다.

권장 Wave 구조:

```text
Wave 0: Skeleton / 공통 기반
Wave 1: 공통 contract 구현
Wave 2: 모듈별 병렬 구현
Wave 3: 통합 구현
Wave 4: QA Fix / Hardening
```

예시:

| Wave | 목적 | 병렬화 수준 |
| --- | --- | --- |
| Wave 0 | repo 구조, app shell, CI, 기본 config | 낮음 |
| Wave 1 | auth, common error, DB migration, API skeleton | 낮음~중간 |
| Wave 2 | 사용자 포털, 관리자 포털, 업무 서비스, 배치 병렬 구현 | 높음 |
| Wave 3 | API/UI/batch/DB 통합 | 중간 |
| Wave 4 | QA FIND 수정, 회귀 테스트, 증적 보강 | 중간 |

Wave 2에서 병렬화가 가장 크다.
하지만 Wave 2가 가능하려면 Wave 0~1에서 공통 기반과 contract가 먼저 준비되어야 한다.

### 6.7 Gate 4: Integration QA / Evidence / Cross Review

목표:

- 모듈별 구현 결과 검증
- 모듈 간 통합 검증
- 화면 증적, 테스트 결과, 로그 증적 수집
- FIND / CR / ISSUE 분류
- 설계와 구현의 차이 확인

주요 검증:

- 단위 테스트
- 통합 테스트
- API contract test
- UI evidence
- batch dry-run 또는 sample run
- 권한별 접근 검증
- traceability check
- run-check

교차검증:

- 구현이 Gate 2 설계를 지켰는지 확인
- 테스트가 Gate 3 기준을 충족했는지 확인
- 발견사항이 FIND인지 CR인지 ISSUE인지 분류
- 구현자가 자기 구현을 최종 승인하지 않도록 별도 review 관점 적용

### 6.8 Gate 5: Release Approval

목표:

- 릴리즈 후보 정리
- 남은 FIND/CR/ISSUE 판단
- 인수인계와 운영 주의사항 정리
- 승인 여부 판단 지원

주의:

- 미해결 이슈를 숨긴 승인 선언을 금지한다.
- 승인은 에이전트가 아니라 사람 또는 명시된 승인 주체가 한다.

## 7. 교차검증 지점

교차검증은 Ex에서 핵심 장치로 다룬다.

| 지점 | 검증 질문 |
| --- | --- |
| Gate 1 종료 전 | 요구사항이 Phase 0 목표, 범위, 제약과 맞는가? |
| Gate 2 종료 전 | 설계가 REQ/NREQ/AC를 누락 없이 커버하는가? |
| Module Slicing 후 | 병렬 구현 경계가 실제로 분리 가능한가? |
| Gate 3 종료 전 | 테스트가 AC, 보안, 비기능, UI 기준을 검증하는가? |
| Wave 시작 전 | 해당 Wave의 선행 의존성과 contract가 준비됐는가? |
| Wave 완료 후 | 구현 결과가 설계와 테스트 기준을 만족하는가? |
| Gate 4 종료 전 | 통합 결과, 증적, traceability가 릴리즈 판단에 충분한가? |

교차검증은 별도 persona 또는 별도 실행 환경이 맡을 수 있다.
예를 들어 Hermes 환경에서는 `delegate_task`, `profile`, `kanban`을 사용해 review, security-review, ui-review, development-review 관점을 분리할 수 있다.

단, 교차검증 결과는 최종 승인 자체가 아니다.
Orchestrator가 결과를 통합하고, 필요한 경우 사용자 또는 승인 주체의 판단을 받아야 한다.

## 8. Module Slicing 기준

모듈은 다음 조건을 만족할수록 병렬 구현에 적합하다.

- 책임 범위가 명확하다.
- owning data가 명확하다.
- 외부 모듈과의 interface가 contract로 고정되어 있다.
- 수정 파일 범위가 비교적 분리되어 있다.
- 독립 테스트 또는 mock 기반 테스트가 가능하다.
- 통합 테스트 기준이 정의되어 있다.
- 관련 traceability ID가 연결되어 있다.

반대로 다음 경우에는 병렬 구현을 피한다.

- DB schema가 아직 크게 흔들린다.
- 인증/권한 모델이 확정되지 않았다.
- API contract가 논의 중이다.
- 화면과 backend 책임 경계가 불명확하다.
- 같은 파일 또는 같은 공통 모듈을 여러 worker가 동시에 수정해야 한다.
- 실패 원인이 요구사항 변경인지 구현 결함인지 구분되지 않는다.

## 9. Ex Orchestrator 관점

Orchestrator는 병렬화를 목표로 삼지 않는다.
Orchestrator의 목표는 올바른 순서와 안전한 병렬화 경계를 판단하는 것이다.

Orchestrator 판단 루프:

```text
Observe: 현재 Gate, 요구사항, 설계, 의존성 확인
Plan: 순차로 할 일과 병렬화 가능한 일 구분
Delegate: persona 또는 worker에 작업 위임
Verify: 결과를 테스트, trace, 설계 기준으로 검증
Decide: PASS, FIND, CR, ISSUE, 보류, 재작업 판단
Report: 사용자에게 상태와 승인 필요 지점 보고
```

구현 단계에서 Orchestrator는 기능 구현의 주 작성자가 되지 않는 것이 이상적이다.
구현은 build persona 또는 모듈 worker가 수행하고, Orchestrator는 다음을 책임진다.

- Build Wave 정의
- worker 작업 범위 제한
- 결과 수집
- 검증 실행 또는 검증 계획 확인
- traceability 갱신
- FIND / CR / ISSUE 분류
- 사용자 승인 필요 지점 보고

## 10. Dashboard 관점

Dashboard는 이 ideal 모델에서 판단자가 아니라 관측자와 승인 보조 UI다.

Dashboard가 보여주면 좋은 정보:

- 현재 Gate
- Gate별 완료/보류/승인 상태
- Module Slicing 결과
- 모듈별 구현 상태
- Build Wave 진행 상태
- Wave별 worker 상태
- 교차검증 결과
- FIND / CR / ISSUE 목록
- traceability coverage
- 테스트/증적 상태
- 승인 필요 항목

Dashboard가 하면 안 되는 것:

- Core 규칙을 우회해 Gate를 자동 승인
- kanban task 완료만 보고 Run 완료 처리
- 테스트 미실행 상태를 PASS로 표시
- FIND와 CR을 임의로 합치거나 숨기기

## 11. Hermes 적용 관점

Hermes를 상위 Orchestrator로 쓸 경우 이 모델은 다음처럼 매핑할 수 있다.

| Ex 개념 | Hermes 기능 | 사용 방식 |
| --- | --- | --- |
| 짧은 교차검토 | `delegate_task` | review/security/ui 관점의 동기 검토 |
| 반복 역할 | `profile` | ex-builder, ex-reviewer, ex-security 등 역할별 실행 환경 |
| Build Wave queue | `kanban` | 모듈별 task를 durable queue로 배정 |
| 반복 점검 | `cron` | traceability, stale Run, CI, 문서 상태 주기 점검 |

중요한 점:

```text
Hermes 기능은 Ex Core 판단을 대체하지 않는다.
Hermes 기능은 Orchestrator가 Core 규칙을 더 안정적으로 실행하기 위한 수단이다.
```

## 12. 향후 Core 반영 후보

이 문서는 아직 ideal reference다.
바로 Core 규약으로 승격하지 말고, 실제 샘플 프로젝트에서 검증한 뒤 다음 항목만 Core에 반영하는 것이 좋다.

후보:

- Gate 2 안의 Module Slicing 산출물 정의
- Build Wave와 Module ID 연결 규칙
- 병렬 구현 가능 여부 판단 기준
- Wave 시작 전 readiness checklist
- Wave 완료 후 cross review checklist
- Dashboard가 읽을 module/wave 상태 필드
- FIND / CR / ISSUE와 module/wave 연결 규칙

아직 Core에 넣지 말아야 할 것:

- 특정 조직의 SI 산출물 이름 강제
- 모든 프로젝트에 동일한 module taxonomy 강제
- 모든 구현을 kanban으로만 수행하도록 강제
- 모든 Gate에 독립 검수를 의무화
- 특정 도구, 모델, provider 전제

## 13. 최종 요약

Vulcan-Anvil Ex의 현실적인 ideal은 다음이다.

```text
1. 앞단은 순차 Gate로 정합성을 확보한다.
2. Gate 2에서 공통 설계와 모듈 경계를 고정한다.
3. Gate 3에서 테스트 기준을 모듈과 AC에 연결한다.
4. 구현은 Build Wave로 나누고, 모듈/서비스 단위로 병렬화한다.
5. Wave 완료마다 설계, 테스트, traceability 기준으로 교차검증한다.
6. Dashboard는 Gate, Module, Wave, Review, Evidence 상태를 관측한다.
7. 최종 승인과 범위 변경 판단은 사람 또는 명시된 승인 주체가 한다.
```

이 모델은 Agile 흉내를 내는 무제한 병렬 개발이 아니다.
SI 프로젝트의 순차 판단 구조를 인정하면서, 병렬화가 가능한 지점만 명확한 contract와 검증 기준 위에서 활용하는 방식이다.
