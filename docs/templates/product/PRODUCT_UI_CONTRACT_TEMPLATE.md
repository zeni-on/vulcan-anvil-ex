# Product UI Contract

---
document_id: PROD-UI
title: Product UI Contract
title_ko: 제품 UI 계약
project: {{PROJECT_NAME}}
profile: product
gate_scope: gate2-gate4
status: Draft
version: v0.1
owner_role: Product / Frontend Owner
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
related_documents:
  - docs/product/PRODUCT_CONTRACTS.md
  - docs/product/REGRESSION_AND_RELEASE_REPORT.md
---

## 1. Purpose

이 문서는 Product profile의 선택 상세 산출물이다.
`PRODUCT_CONTRACTS.md`의 UI Contracts만으로 구현자가 화면 흐름, 상태, 시각 기준, 증적 기준을 안정적으로 이해하기 어려울 때 작성한다.

## 2. Screen / Flow Contract

| UI/SCR ID | 화면/흐름 | 주요 사용자 행동 | 주요 상태 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- | --- |
| UI-001 | TBD | TBD | Empty / Loading / Success / Error | SCN-001 | REG-001 |

## 3. UI Design Baseline

| Baseline ID | 기준 산출물 | 경로 | 유지해야 할 요소 | 변경 허용 범위 |
| --- | --- | --- | --- | --- |
| UIBASE-001 | TBD | docs/artifacts/02-design/screen/images/ | TBD | TBD |

## 4. Publishing / Prototype Baseline

| Artifact ID | 유형 | 경로 | 구현 기준 여부 | 비고 |
| --- | --- | --- | --- | --- |
| UIPUB-001 | HTML/CSS/JS / Figma / Screenshot | docs/artifacts/02-design/screen/prototypes/ | Yes / Reference only | TBD |

## 5. UI Evidence Plan

| REG/UI ID | 시나리오 | 기대 화면 | 증적 경로 | 결과 |
| --- | --- | --- | --- | --- |
| REG-UI-001 | TBD | TBD | docs/artifacts/04-review/evidence/ui/ | Planned |

## 6. Open Issues

| Issue ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| ISSUE-UI-001 | TBD | TBD | Backlog / Fix before release |
