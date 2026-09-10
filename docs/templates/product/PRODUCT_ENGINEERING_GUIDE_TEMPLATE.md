# Product Engineering Guide

---
document_id: PROD-ENG
title: Product Engineering Guide
title_ko: 제품 개발/빌드/배포 기준
project: {{PROJECT_NAME}}
profile: product
gate_scope: gate2-impl-gate4
status: Draft
version: v0.1
owner_role: Engineering Owner
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
related_documents:
  - docs/product/PRODUCT_ARCHITECTURE.md
  - docs/product/PRODUCT_CONTRACTS.md
  - docs/product/REGRESSION_AND_RELEASE_REPORT.md
---

## 1. Purpose

이 문서는 Product profile의 선택 상세 산출물이다.
개발자가 같은 방식으로 빌드, 실행, 테스트, 배포 후보 검증을 수행하도록 최소 기준을 고정한다.
실행 명령/개발 기준은 이 원본에 두고 Architecture/Contracts에서는 상대 Markdown 링크로 연결한다. 기술 선택 이유는 ADR, 실제 도구/의존성 버전은 manifest/lockfile을 참조한다. 작성 기준은 `docs/core/PRODUCT_DOCUMENT_WRITING.md`다.

## 2. Technology Stack

| Layer | 선택 | 버전/제약 | 비고 |
| --- | --- | --- | --- |
| Frontend | TBD | TBD | TBD |
| Backend | TBD | TBD | TBD |
| Data Store | TBD | TBD | TBD |
| Test / QA | TBD | TBD | TBD |

## 3. Development Rules

실제 코드 구조, 공개 계약과 오류/로그/주석 관례, 테스트 입력·기대값 설명 기준을 정한다. 존재하지 않는 스택의 규칙이나 에이전트 운영 절차 전문을 복사하지 않는다.

| Rule ID | 기준 | 적용 대상 | 검증 |
| --- | --- | --- | --- |
| ENG-001 | 코드 스타일 / lint 기준 | TBD | REG-001 |
| ENG-002 | 테스트 작성 기준 | TBD | REG-001 |
| ENG-003 | 로그/오류 처리 기준 | TBD | SEC-REG-001 |

## 4. Build / Run / Test Commands

| Surface ID | 목적 | 명령 | 성공 기준 |
| --- | --- | --- | --- |
| BUILD-001 | Build | TBD | TBD |
| RUN-001 | Local Run | TBD | TBD |
| TEST-001 | Unit/Integration Test | TBD | TBD |
| UI-TEST-001 | UI Regression | TBD | TBD |

## 5. Configuration And Deployment

설정 이름/필수 여부/secret 취급, 배포·migration·롤백·복구 절차와 성공/중단 조건을 적는다. secret 값과 매 실행 로그는 넣지 않는다. 운영 절차가 길어지면 `docs/operations/`의 원본을 명시적으로 연결하고 담당자가 직접 확인한다.

| Config/Deploy ID | 항목 | 기준 | Secret 여부 | 검증 |
| --- | --- | --- | --- | --- |
| CONF-001 | TBD | TBD | Yes / No | SEC-REG-001 |
| DEPLOY-001 | TBD | TBD | No | REG-001 |

## 6. Open Issues

| Issue ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| ISSUE-ENG-001 | TBD | TBD | Backlog / Fix before release |
