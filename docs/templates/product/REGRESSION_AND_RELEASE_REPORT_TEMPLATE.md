# Regression And Release Report

---
document_id: PROD-REL
title: Regression And Release Report
title_ko: 제품 회귀 검증 및 릴리즈 보고
project: {{PROJECT_NAME}}
profile: product
gate_scope: gate3-gate5
status: Draft
version: v0.1
owner_role: QA / Release Owner
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
related_documents:
  - docs/product/PRODUCT_TRACEABILITY.md
---

## 1. Gate 3 Regression Plan

| REG ID | 검증 대상 | 명령/방법 | 성공 기준 | 관련 Scenario |
| --- | --- | --- | --- | --- |
| REG-001 | TBD | TBD | TBD | SCN-001 |

## 2. Gate 3 Security Smoke Plan

Product profile의 보안 smoke는 취약점 진단 전체가 아니라 릴리즈 전에 놓치면 안 되는 기본 보안 확인이다.
실행할 수 없는 항목은 `Not Run`으로 숨기지 말고 `environment_blocked` 또는 backlog/issue로 분리한다.

| SEC-REG ID | 검증 대상 | 명령/방법 | 성공 기준 | 관련 SEC/Scenario |
| --- | --- | --- | --- | --- |
| SEC-REG-001 | TBD | TBD | 내부 오류/민감정보 노출, 입력 검증, 기본 접근통제 위험이 확인됨 | SEC-001, SCN-001 |

## 3. Gate 4 Execution Result

현재 릴리즈의 판단 근거를 중심으로 기록하고 과거 실행 상세는 기존 Run/증적 링크로 보존한다. 검증 JSON이 있으면 로그/증적 칸에서 연결한다. 실제 테스트한 소스 커밋과 이 결과 문서를 저장한 커밋은 다를 수 있으며, 미커밋 변경을 포함한 검증을 HEAD만 검증한 것으로 표시하지 않는다. 기준은 `docs/core/CURRENT_CONTEXT_AND_EVIDENCE.md`다.

| REG ID | 실행 일시 | 결과 | 로그/증적 | 비고 |
| --- | --- | --- | --- | --- |
| REG-001 | TBD | Planned / Pass / Fail / Not Run / environment_blocked | TBD | TBD |

## 4. Gate 4 Security Check Result

| SEC-REG ID | 실행 일시 | 결과 | 로그/증적 | 비고 |
| --- | --- | --- | --- | --- |
| SEC-REG-001 | TBD | Planned / Pass / Fail / Not Run / environment_blocked | TBD | TBD |

## 5. Known Issues

| Issue ID | 내용 | 영향 | 릴리즈 판단 |
| --- | --- | --- | --- |
| ISSUE-001 | TBD | TBD | Accept / Fix before release / Backlog |

## 6. Gate 5 Release Decision

| 항목 | 내용 |
| --- | --- |
| 릴리즈 후보 | Yes / No / Conditional |
| 포함 범위 | TBD |
| 제외 범위 | TBD |
| 남은 리스크 | TBD |
| 다음 릴리즈 후보 | TBD |
