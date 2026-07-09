# Product Contracts

---
document_id: PROD-CONTRACT
title: Product Contracts
title_ko: 제품 구현 계약 인덱스
project: Product TODO v0.4.8 Replay
profile: product
gate_scope: gate2-impl
status: Draft
version: v0.1
owner_role: Technical Architect
author: Agent
reviewer: User
approver: User
created_at: 2026-06-16
updated_at: 2026-06-16
related_documents:
  - docs/product/PRODUCT_BRIEF.md
  - docs/product/PRODUCT_ARCHITECTURE.md
---

## 1. Contract Policy

이 문서는 상세 설계서 복사본이 아니라 Product profile의 구현 계약 진입점이다.
상세 API/DB/UI/보안 설계가 필요한 경우 `docs/artifacts/02-design/` 산출물로 분리하고, 이 문서에서는 링크와 핵심 계약만 유지한다.

## 2. API Contracts

| API ID | Method | Path / Entry | Request | Response | 관련 Scenario | 상세 문서 |
| --- | --- | --- | --- | --- | --- | --- |
| API-001 | GET | `/api/todos` | 없음 | `{ "data": Todo[] }` | SCN-001, SCN-002, SCN-003 | 이 문서 |
| API-002 | POST | `/api/todos` | `{ "text": string }` | `{ "data": Todo }` 또는 validation error | SCN-001 | 이 문서 |
| API-003 | PATCH | `/api/todos/{todoId}` | `{ "completed": boolean }` | `{ "data": Todo }` 또는 not found error | SCN-002 | 이 문서 |
| API-004 | DELETE | `/api/todos/{todoId}` | 없음 | `{ "data": { "deleted": true } }` 또는 not found error | SCN-003 | 이 문서 |

## 3. Data Contracts

| DATA/DB ID | 이름 | 주요 필드 | 보안 분류 | 관련 API/Scenario | 상세 문서 |
| --- | --- | --- | --- | --- | --- |
| DATA-001 | Todo | `id`, `text`, `completed`, `created_at`, `updated_at` | 일반 데이터. 개인정보/인증정보/민감정보 없음 | API-001~API-004, SCN-001~SCN-003 | 이 문서 |

## 4. UI Contracts

| UI/SCR ID | 화면/상호작용 | 주요 상태 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- |
| UI-001 | TODO 단일 화면 | Empty / List / Loading / Validation Error / API Error | SCN-001~SCN-003 | REG-001 |

## 5. Security Contracts

Product profile의 보안 계약은 `docs/core/PRODUCT_PROFILE_BASELINE.md`, `docs/core/SECURITY_BASELINE.md`, `docs/core/REFERENCE_STANDARDS.md`를 기준으로 작성한다.
KISA/SR 매핑은 선택 참고이지만, OWASP/CWE 기반의 제품 보안 판단은 비워두지 않는다.

| SEC ID | 보안 계약 | 적용 대상 | 기준/참조 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | TODO text 입력은 공백 불가/길이 제한을 적용하고 오류 응답에 내부 구현 상세를 노출하지 않는다. | API-002, UI-001 | OWASP ASVS input validation, OWASP Top 10 A03, CWE-20 | SCN-001 | SEC-REG-001 |
| SEC-002 | TODO 상태 변경/삭제는 존재하지 않는 ID와 잘못된 completed 값을 안전한 오류로 처리한다. | API-003, API-004 | OWASP API Top 10, CWE-20, CWE-209 | SCN-002, SCN-003 | SEC-REG-001 |
| SEC-003 | Todo 데이터는 일반 데이터로 분류하며 개인정보/인증정보/민감정보를 저장하지 않는다. | DATA-001 | Product Security/Data Baseline | SCN-001~SCN-003 | SEC-REG-001 |

## 6. Security And Data Baseline

| 항목 | 기준 | 적용 위치 | 검증 |
| --- | --- | --- | --- |
| Security | docs/core/PRODUCT_PROFILE_BASELINE.md, docs/core/SECURITY_BASELINE.md | API 입력 검증, 오류 응답, UI 렌더링 | REG-001 |
| Data | docs/core/DATA_STANDARD_RULES.md | Todo 데이터 필드 정의와 보안 분류 | REG-001 |

## 7. Contract Gaps

| Gap ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| GAP-NONE | 현재 Gate 2 기준 차단 계약 gap 없음 | N/A | 구현 중 계약 변경이 필요하면 Product backlog 또는 ADR로 기록 |
