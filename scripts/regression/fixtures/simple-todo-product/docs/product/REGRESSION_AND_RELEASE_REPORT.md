# Regression And Release Report

---
document_id: PROD-REL
title: Regression And Release Report
title_ko: 제품 회귀 검증 및 릴리즈 보고
project: Product TODO v0.4.8 Replay
profile: product
gate_scope: gate3-gate5
status: Draft
version: v0.1
owner_role: QA / Release Owner
author: Agent
reviewer: User
approver: User
created_at: 2026-06-16
updated_at: 2026-06-16
related_documents:
  - docs/product/PRODUCT_TRACEABILITY.md
---

## 1. Gate 3 Regression Plan

| REG ID | 검증 대상 | 명령/방법 | 성공 기준 | 관련 Scenario |
| --- | --- | --- | --- | --- |
| REG-001 | TODO API CRUD 회귀 | `python -m pytest tests -q` | 추가/조회/완료토글/삭제 테스트가 모두 통과한다. | SCN-001, SCN-002, SCN-003 |
| REG-002 | TODO UI smoke | 브라우저 또는 Playwright로 주요 화면 흐름 확인 | 새 할 일 추가, 완료 토글, 삭제 흐름이 화면에서 동작한다. | SCN-001, SCN-002, SCN-003 |

## 2. Gate 3 Security Smoke Plan

Product profile의 보안 smoke는 취약점 진단 전체가 아니라 릴리즈 전에 놓치면 안 되는 기본 보안 확인이다.
실행할 수 없는 항목은 `Not Run`으로 숨기지 말고 `environment_blocked` 또는 backlog/issue로 분리한다.

| SEC-REG ID | 검증 대상 | 명령/방법 | 성공 기준 | 관련 SEC/Scenario |
| --- | --- | --- | --- | --- |
| SEC-REG-001 | Product security smoke | `python -m pytest tests -q`와 API 오류 응답 확인 | 입력 검증, not found 오류, 내부 구현 상세 미노출, 민감정보 미저장이 확인된다. | SEC-001~SEC-003, SCN-001~SCN-003 |

## 3. Gate 4 Execution Result

| REG ID | 실행 일시 | 결과 | 로그/증적 | 비고 |
| --- | --- | --- | --- | --- |
| REG-001 | 2026-06-16 | Pass | docs/product/evidence/G4_pytest.log | API CRUD 회귀 포함, 5 passed |
| REG-002 | 2026-06-16 | Pass | docs/product/evidence/G4_pytest.log | UI shell/static asset smoke 포함 |

## 4. Gate 4 Security Check Result

| SEC-REG ID | 실행 일시 | 결과 | 로그/증적 | 비고 |
| --- | --- | --- | --- | --- |
| SEC-REG-001 | 2026-06-16 | Pass | docs/product/evidence/G4_pytest.log | 입력 검증, not found 오류, 내부 구현 상세 미노출을 API 테스트로 확인 |

## 5. Known Issues

| Issue ID | 내용 | 영향 | 릴리즈 판단 |
| --- | --- | --- | --- |
| ISSUE-NONE | 현재 Gate 4 기준 알려진 차단 이슈 없음 | N/A | 릴리즈 후보 가능 |
| ISSUE-G4-001 | FastAPI/Starlette/Python 3.14 deprecation warning이 pytest 로그에 남음 | 제품 동작 차단은 아님 | Backlog |

## 6. Gate 5 Release Decision

| 항목 | 내용 |
| --- | --- |
| 릴리즈 후보 | Conditional |
| 포함 범위 | SCN-001~SCN-003 |
| 제외 범위 | 인증, 다중 사용자, 검색/필터, 태그, 마감일, 외부 배포 |
| 남은 리스크 | Python 3.14 dependency deprecation warning은 후속 backlog로 관리 |
| 다음 릴리즈 후보 | 검색/필터, 접근성 보강, 저장소 설정 개선 |
