# Product Security Checklist

---
document_id: PROD-SEC
title: Product Security Checklist
title_ko: 제품 보안 체크리스트
project: {{PROJECT_NAME}}
profile: product
gate_scope: gate2-gate4
status: Draft
version: v0.1
owner_role: Security / Technical Owner
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
related_documents:
  - docs/product/PRODUCT_ARCHITECTURE.md
  - docs/product/PRODUCT_CONTRACTS.md
  - docs/core/PRODUCT_PROFILE_BASELINE.md
  - docs/core/SECURITY_BASELINE.md
---

## 1. Purpose

이 문서는 Product profile의 선택 상세 산출물이다.
Audit 수준의 보안가이드가 아니라 릴리즈 전에 놓치면 안 되는 제품 보안 결정을 OWASP/CWE 기준으로 점검한다.

## 2. Security Scope

| SEC ID | 보안 영역 | 적용 대상 | 기준/참조 | 관련 Scenario |
| --- | --- | --- | --- | --- |
| SEC-001 | TBD | API-001 / DATA-001 / UI-001 | OWASP ASVS / Top 10 / API Top 10 / CWE | SCN-001 |

## 3. Checklist

| Check ID | 항목 | 기대 기준 | 결과 | 증적/비고 |
| --- | --- | --- | --- | --- |
| SEC-CHK-001 | 입력값 검증 | API/UI 입력이 검증되고 내부 오류가 노출되지 않음 | Planned | SEC-REG-001 |
| SEC-CHK-002 | 인증/인가 | 제품 범위에 맞는 접근통제 결정이 명시됨 | Planned | SEC-REG-001 |
| SEC-CHK-003 | 민감정보/secret | 화면, 로그, 저장소, config에 민감정보가 노출되지 않음 | Planned | SEC-REG-001 |
| SEC-CHK-004 | 오류/로그 | stack, SQL, token, 내부 경로가 사용자 화면에 노출되지 않음 | Planned | SEC-REG-001 |
| SEC-CHK-005 | 의존성 | lockfile과 알려진 취약점 처리 방침이 있음 | Planned | SEC-REG-001 |

## 4. Risk Acceptance

| Risk ID | 내용 | 영향 | 릴리즈 판단 |
| --- | --- | --- | --- |
| RISK-SEC-001 | TBD | TBD | Accept / Fix before release / Backlog |

## 5. Audit Upgrade Gap

| Gap ID | Audit 전환 시 보강할 항목 | 현재 Product 판단 |
| --- | --- | --- |
| GAP-SEC-001 | KISA/SR 또는 고객 보안 기준 공식 매핑 | 선택 / 필요 시 보강 |
