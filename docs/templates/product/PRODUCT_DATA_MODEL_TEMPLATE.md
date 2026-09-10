# Product Data Model

---
document_id: PROD-DATA
title: Product Data Model
title_ko: 제품 데이터 모델
project: {{PROJECT_NAME}}
profile: product
gate_scope: gate2-impl
status: Draft
version: v0.1
owner_role: Data / Backend Owner
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
related_documents:
  - docs/product/PRODUCT_CONTRACTS.md
  - docs/core/DATA_STANDARD_RULES.md
---

## 1. Purpose

이 문서는 Product profile의 선택 상세 산출물이다.
`PRODUCT_CONTRACTS.md`의 Data Contracts만으로 데이터 의미, 보안 분류, persistence shape, ERD 근거가 부족할 때 작성한다.
원장에는 이 원본의 ID·제목·상대 Markdown 링크만 연결한다. 생성 DDL/schema와 수동 표에 같은 전문을 중복 유지하지 않는다. 작성 기준은 `docs/core/PRODUCT_DOCUMENT_WRITING.md`다.

## 2. Data Entities

| DATA/DB ID | 이름 | 설명 | 주요 필드 | 보안 분류 | 관련 Scenario |
| --- | --- | --- | --- | --- | --- |
| DATA-001 | TBD | TBD | TBD | 일반 / 식별정보 / 개인정보 / 인증정보 / 민감정보 | SCN-001 |

## 3. Field Dictionary

| Field ID | 표준명 | 영문명 | 타입/길이 | 도메인 | 보안 분류 | 관련 API/UI |
| --- | --- | --- | --- | --- | --- | --- |
| FLD-001 | TBD | TBD | TBD | TBD | TBD | API-001, UI-001 |

## 4. ERD / Schema Evidence

| 산출물 | 권장 경로 | 설명 |
| --- | --- | --- |
| Logical ERD | docs/artifacts/02-design/data/erd/logical/ | 업무 엔티티와 관계 |
| Physical ERD / DBML | docs/artifacts/02-design/data/erd/physical/ | 테이블, 컬럼, 제약조건, 인덱스 |
| Export / Image | docs/artifacts/02-design/data/erd/exports/ | PNG, SVG, PDF 등 검토용 export |

## 5. Data Rules

키/제약/관계, 수명주기·보존, 이관/복구와 실패 시 처리 기준을 실제 제품 범위에 맞춰 적는다. 비적용이면 이유를 밝힌다.

| Rule ID | 규칙 | 적용 대상 | 검증 |
| --- | --- | --- | --- |
| DATA-RULE-001 | TBD | DATA-001 | REG-001 |

## 6. Open Issues

| Issue ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| ISSUE-DATA-001 | TBD | TBD | Backlog / Fix before release |
