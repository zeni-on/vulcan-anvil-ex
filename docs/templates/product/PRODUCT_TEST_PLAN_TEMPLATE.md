# Product Test Plan

---
project: {{PROJECT_NAME}}
profile: product
status: Draft
owner_role: QA Owner
created_at: {{GENERATED_DATE}}
---

<!-- 선택 상세: docs/artifacts/03-test/<feature>.md. REGRESSION_AND_RELEASE_REPORT의 계획 절에서 실제 상대 Markdown 링크로 연결한다. 작성 기준: docs/core/PRODUCT_DOCUMENT_WRITING.md. 실행 결과는 여기에 쓰지 않는다. -->

## 1. Scope And Preconditions

대상 기능/릴리즈, 요구·AC/계약 원본, 시험 환경과 선행 데이터: TBD

## 2. Regression Plan

승인된 AC에서 기대값을 정하고, 그 기대가 틀렸다면 실패할 행동·검증 방법을 아래에 짝지어 적는다. 예: 지우기 버튼이 요구라면 버튼을 눌러 저장한 뒤 다시 연 값을 확인한다. API로 같은 상태를 만든 것만으로 그 행동을 대신하지 않는다.

| REG ID | 관련 Scenario / REQ / AC / 계약 | 입력 / 행동 | 기대값 | 명령 / 테스트 위치 |
| --- | --- | --- | --- | --- |
| REG-001 | SCN-001, REQ-001, AC-001, API-001 | TBD | TBD | TBD |

## 3. Security Smoke Plan

| SEC-REG ID | 관련 SEC / Scenario | 입력 / 행동 | 기대값 | 명령 / 테스트 위치 |
| --- | --- | --- | --- | --- |
| SEC-REG-001 | SEC-001, SCN-001 | TBD | TBD | TBD |

## 4. Test Data And Evidence

이 TC만 다시 실행할 때 쓸 고정 입력 또는 fixture/준비 명령: TBD

상태가 있는 시험은 시작 상태 확인, 격리·초기화/정리 방법, 필요한 증적 위치를 적는다. 기존 테스트 코드가 이를 수행하면 해당 위치만 연결한다.

## 5. Open Decisions

미확정/비적용 범위의 근거와 관리 원본: TBD

<!-- 복잡한 케이스는 해당 REG-ID 제목의 하위 절에 선행조건/입력/기대값을 풀어 쓴다. 계획 표와 다른 표에 같은 ID 정의를 반복하지 않는다. -->
