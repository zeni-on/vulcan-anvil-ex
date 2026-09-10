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
원장에는 이 원본의 ID·제목·상대 Markdown 링크만 연결한다. 실제 시험 결과는 여기에 누적하지 않는다. 작성 기준은 `docs/core/PRODUCT_DOCUMENT_WRITING.md`다.

## 2. Screen / Flow Contract

사용자 여정/탐색, 권한에 따른 접근과 표시, 입력/오류 상태, 접근성·반응형 기준을 적는다. 이미지/퍼블리싱만으로 동작과 예외 조건을 대신하지 않는다.

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

| 관련 시험 | 시나리오 | 기대 화면 | 시험 정의 / 증적 계획 |
| --- | --- | --- | --- |
| REG-001 | TBD | TBD | TBD |

입력/기대값의 실행 가능한 시험 정의는 해당 Test Plan, 실제 관측/스크린샷은 실행 묶음의 결과에 둔다.

## 6. Open Issues

| Issue ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| ISSUE-UI-001 | TBD | TBD | Backlog / Fix before release |
