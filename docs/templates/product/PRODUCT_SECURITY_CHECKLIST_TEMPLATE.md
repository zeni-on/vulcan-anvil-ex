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
신뢰 경계/자산/사용자와 적용 위협을 먼저 정하고 실제 보호 정책을 쓴다. Architecture/Contracts에서는 동일 원본의 상대 Markdown 링크와 적용 범위를 연결한다. 작성 기준은 `docs/core/PRODUCT_DOCUMENT_WRITING.md`다.

## 2. Security Scope

| SEC ID | 보안 영역 / 보호 정책 | 적용 대상 | 기준/참조 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | TBD | API-001 / DATA-001 / UI-001 | OWASP ASVS / Top 10 / API Top 10 / CWE | SCN-001 | SEC-REG-001 |

## 3. Checklist

| Check ID | 항목 | 설계 시 확정할 기준 | 관련 시험 |
| --- | --- | --- | --- |
| SEC-CHK-001 | 입력값 검증 | 허용 형식/범위와 잘못된 입력 처리 | SEC-REG-001 |
| SEC-CHK-002 | 인증/인가 | 사용자/역할별 접근과 거부 동작 | SEC-REG-001 |
| SEC-CHK-003 | 민감정보/secret | 저장/전송/마스킹/설정 정책 | SEC-REG-001 |
| SEC-CHK-004 | 오류/로그 | 내부 정보·민감정보 노출 방지 정책 | SEC-REG-001 |
| SEC-CHK-005 | 의존성 | lockfile과 취약점 처리 방침 | SEC-REG-001 |

이 표는 설계 확인 관점이다. 실제 시험 입력/기대값은 Test Plan, 실행 결과와 증적은 해당 실행 묶음에 기록한다. 보안 기준 목록을 열거한 것만으로 안전성을 검증했다고 보고하지 않는다.

## 4. Risk Acceptance

| Risk ID | 내용 | 영향 | 릴리즈 판단 |
| --- | --- | --- | --- |
| RISK-SEC-001 | TBD | TBD | Accept / Fix before release / Backlog |

## 5. Audit Upgrade Gap

| Gap ID | Audit 전환 시 보강할 항목 | 현재 Product 판단 |
| --- | --- | --- |
| GAP-SEC-001 | KISA/SR 또는 고객 보안 기준 공식 매핑 | 선택 / 필요 시 보강 |
