# Product Brief

---
document_id: PROD-BRIEF
title: Product Brief
title_ko: 제품/업무 앱 개요
project: Product TODO v0.4.8 Replay
profile: product
gate_scope: phase0-gate1
status: Draft
version: v0.1
owner_role: Product Owner
author: Agent
reviewer: User
approver: User
created_at: 2026-06-16
updated_at: 2026-06-16
---

## 1. Product Goal

| 항목 | 내용 |
| --- | --- |
| 목표 | 단일 사용자가 브라우저에서 할 일을 등록, 조회, 완료 처리, 삭제할 수 있는 작은 TODO 앱을 만든다. |
| 주요 사용자 | 개인 업무나 학습 항목을 빠르게 메모하고 완료 여부를 확인하려는 단일 사용자 |
| 해결하려는 문제 | 간단한 할 일을 별도 계정이나 협업 기능 없이 즉시 기록하고 현재 상태를 확인한다. |
| 성공 기준 | 사용자가 로컬 웹 화면에서 할 일 추가, 목록 조회, 완료 토글, 삭제를 수행할 수 있고 기본 회귀 테스트가 통과한다. |
| 비목표 | 인증, 다중 사용자, 협업, 태그, 마감일, 알림, 외부 배포, 모바일 앱은 이번 범위에서 제외한다. |

## 2. Core Scenarios

| Scenario ID | 시나리오 | 사용자 가치 | 우선순위 | 관련 REQ |
| --- | --- | --- | --- | --- |
| SCN-001 | 사용자가 새 할 일을 입력해 목록에 추가한다. | 해야 할 일을 잊지 않도록 즉시 기록한다. | Must | REQ-001 |
| SCN-002 | 사용자가 목록의 할 일을 완료/미완료로 전환한다. | 진행 상태를 빠르게 정리한다. | Must | REQ-002 |
| SCN-003 | 사용자가 필요 없는 할 일을 삭제한다. | 더 이상 필요 없는 항목을 제거해 목록을 깨끗하게 유지한다. | Should | REQ-003 |

## 3. Release Scope

| 구분 | 내용 |
| --- | --- |
| 이번 릴리즈 포함 | SCN-001, SCN-002, SCN-003의 로컬 웹 동작과 기본 회귀 테스트 |
| 이번 릴리즈 제외 | 인증, 서버 배포, 사용자별 데이터 분리, 검색/필터, 태그, 마감일 |
| 다음 릴리즈 후보 | 검색/필터, 로컬 저장소 영속화 개선, 접근성 보강 |

## 4. Product Risks And Assumptions

| ID | 유형 | 내용 | 대응 |
| --- | --- | --- | --- |
| RISK-001 | Assumption | Product profile 샘플 검증이 목적이므로 기능 범위는 단일 사용자 TODO에 제한한다. | 범위가 늘어나면 새 Scenario와 Release Scope 후보로 분리한다. |
| RISK-002 | Risk | Product profile 문서와 release-pr 검사가 audit 산출물을 과하게 요구할 수 있다. | `status --check`, `profile-gap`, `release-pr --dry-run` 결과로 확인한다. |
