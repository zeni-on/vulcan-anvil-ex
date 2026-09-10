# Product API Contract

---
document_id: PROD-API
title: Product API Contract
title_ko: 제품 API 계약
project: {{PROJECT_NAME}}
profile: product
gate_scope: gate2-impl
status: Draft
version: v0.1
owner_role: Technical Architect
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
related_documents:
  - docs/product/PRODUCT_CONTRACTS.md
  - docs/product/PRODUCT_TRACEABILITY.md
---

## 1. Purpose

이 문서는 Product profile의 선택 상세 산출물이다.
`PRODUCT_CONTRACTS.md`의 API 요약만으로 worker 구현 또는 release regression 판단이 부족할 때 작성한다.
Audit 제출용 API 정의서가 아니라 public API surface, DTO, 오류 계약, 검증 기준을 고정하기 위한 문서다.
이 상세를 원본으로 선택하면 원장의 API 행은 ID·제목·상대 Markdown 링크로 바꾼다. 작성 기준은 `docs/core/PRODUCT_DOCUMENT_WRITING.md`다. 기존 승인 문서의 이동은 별도 확인/승인을 거친다.

## 2. API Surface

| API ID | Method | Path / Entry | 목적 | 관련 Scenario | 상태 |
| --- | --- | --- | --- | --- | --- |
| API-001 | TBD | TBD | TBD | SCN-001 | Draft |

## 3. Request / Response Contract

### API-001

| 항목 | 계약 / 원본 |
| --- | --- |
| 권한 / 적용 REQ·SEC | TBD |
| Request DTO / Params | TBD |
| Response DTO | TBD |
| Status / Error | TBD |
| 중복 / 재시도 / timeout / 호환성 | TBD |

schema 원본이 있으면 위치와 적용 버전을 연결하고 같은 schema 전문을 별도 표에 복제하지 않는다. 구현에서 생성한 schema가 승인된 의도와 같은지는 별도 확인한다.

## 4. Validation And Error Policy

| API ID | 입력/상황 | 기대 동작 | Error Code / Message | 관련 SEC/REG |
| --- | --- | --- | --- | --- |
| [API-001](#api-001) | TBD | TBD | TBD | SEC-001, REG-001 |

## 5. Implementation Boundary

| API ID | 구현 위치 | 변경 허용 | 변경 금지 |
| --- | --- | --- | --- |
| [API-001](#api-001) | TBD | 내부 구현 세부 | public path, DTO shape, error shape |

## 6. Open Issues

| Issue ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| ISSUE-API-001 | TBD | TBD | Backlog / Fix before release |
