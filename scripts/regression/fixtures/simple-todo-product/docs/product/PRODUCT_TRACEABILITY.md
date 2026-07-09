# Product Traceability

---
document_id: PROD-TRACE
title: Product Traceability
title_ko: 제품 시나리오 추적표
project: Product TODO v0.4.8 Replay
profile: product
gate_scope: gate3-gate5
status: Draft
version: v0.1
owner_role: Orchestrator
author: Agent
reviewer: User
approver: User
created_at: 2026-06-16
updated_at: 2026-06-16
related_documents:
  - docs/product/PRODUCT_BRIEF.md
  - docs/product/PRODUCT_CONTRACTS.md
  - docs/product/REGRESSION_AND_RELEASE_REPORT.md
---

## 1. Traceability Policy

Product 추적은 감리용 전체 추적표가 아니라 릴리즈 판단을 위한 연결이다.
핵심 시나리오가 어떤 계약, 구현, 회귀 테스트, 릴리즈 근거로 이어지는지 확인한다.

## 2. Scenario Trace

| Scenario ID | 관련 REQ | 시나리오 | Product Contract | Security | Implementation | Regression | Release Evidence | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-001 | REQ-001 | 새 할 일을 입력해 목록에 추가한다. | API-001, API-002, DATA-001, UI-001 | SEC-001, SEC-003 | `app/main.py`, `static/app.js`, `tests/test_todos.py` | REG-001, REG-002, SEC-REG-001 | docs/product/evidence/G4_pytest.log | Verified |
| SCN-002 | REQ-002 | 목록의 할 일을 완료/미완료로 전환한다. | API-001, API-003, DATA-001, UI-001 | SEC-002, SEC-003 | `app/main.py`, `static/app.js`, `tests/test_todos.py` | REG-001, REG-002, SEC-REG-001 | docs/product/evidence/G4_pytest.log | Verified |
| SCN-003 | REQ-003 | 필요 없는 할 일을 삭제한다. | API-001, API-004, DATA-001, UI-001 | SEC-002, SEC-003 | `app/main.py`, `static/app.js`, `tests/test_todos.py` | REG-001, REG-002, SEC-REG-001 | docs/product/evidence/G4_pytest.log | Verified |

## 3. Open Trace Gaps

| Gap ID | 누락 연결 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| GAP-NONE | 현재 Gate 3 기준 차단 trace gap 없음 | N/A | 구현/QA 결과에 따라 상태와 증적 갱신 |
