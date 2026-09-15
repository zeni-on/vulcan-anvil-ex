# Product Brief

---
document_id: PROD-BRIEF
title: Product Brief
title_ko: 제품/업무 앱 개요
project: {{PROJECT_NAME}}
profile: product
gate_scope: phase0-gate1
status: Draft
version: v0.1
owner_role: Product Owner
author: Agent
reviewer: User
approver: User
created_at: {{GENERATED_DATE}}
updated_at: {{GENERATED_DATE}}
---

제품 전체의 현재 합의와 이번 작업 범위를 구분하는 진입 문서다. 구현 완료 목록이나 작업 일지가 아니며, 상세 요구/설계/시험은 원본 링크로 연결한다. 작성 기준은 `docs/core/PRODUCT_DOCUMENT_WRITING.md` 1.2절이다.

**목차**
- [1. 문제·목표·성공 기준](#1-product-goal)
- [2. 사용자·업무 맥락·제품 경계](#2-users-and-boundary)
- [3. 핵심 시나리오·전체 흐름](#3-core-scenarios-and-flow)
- [4. 이번 작업 범위](#4-current-work-scope)
- [5. 핵심 제약·가정·열린 결정](#5-constraints-and-open-decisions)
- [6. 관련 원본·과거 기록](#6-references-and-history)

## 1. Product Goal

| 항목 | 내용 |
| --- | --- |
| 목표 | TBD |
| 해결하려는 문제 | TBD |
| 성공 기준 | TBD |
| 비목표 | TBD |

## 2. Users And Boundary

| 구분 | 사용자 / 이해관계자 | 주요 업무·필요 | 제품과의 관계 |
| --- | --- | --- | --- |
| 주요 사용자 | TBD | TBD | TBD |

| 항목 | 내용 |
| --- | --- |
| 현재 업무 방식과 사용 환경 | TBD |
| 제품 책임 / 사람·외부 시스템 책임 | TBD |
| 관련 시스템·자료와 경계 | TBD |

역할·책임은 제품 수준에서 설명한다. 개별 사업의 자료 목록, 상세 권한과 예외는 필요한 업무 흐름/정책 원본에 둔다. 이해관계자라는 이유만으로 제품 사용·자료 접근·발송 권한을 부여하지 않는다.

## 3. Core Scenarios And Flow

제품 전체의 핵심 시나리오를 연결한다. 시나리오에는 액터·시작 상황·얻을 결과를 요약하고, 여러 시나리오의 선후 관계는 필요할 때 설명한다. 이 목록에 있다는 사실이 이번 구현 대상이나 구현 완료를 뜻하지는 않는다.

먼저 대표 한 건의 액터·시작/종료·인계·중요 예외를 함께 확인한다. 상세 흐름이 필요하면 선택 `PRODUCT_BUSINESS_FLOW_TEMPLATE.md`를 같은 `01-requirements` 폴더에서 사용하고 연결한다. 작은 기능은 요구 상세에 함께 적는다. 미합의 시나리오/요구는 해당 절을 candidate로 구분하며 새 필수 산출물을 만들지 않는다.

요구 동작과 AC는 `PRODUCT_REQUIREMENTS_TEMPLATE.md`를 참고해 `docs/artifacts/01-requirements/<feature>.md`의 원본 한 곳에 작성하고 실제 상대 Markdown 링크로 연결한다. 작은 기능은 이 원장에 둘 수 있지만, 상세를 분리한 뒤 같은 정의를 양쪽에 남기지 않는다.

| Scenario ID | 시나리오 | 시작 계기·참여자·인계 | 종료 결과 / 사용자 가치 | 우선순위 | 관련 REQ |
| --- | --- | --- | --- | --- | --- |
| SCN-001 | TBD | TBD | TBD | Must | REQ-001 |

## 4. Current Work Scope

| 구분 | 내용 |
| --- | --- |
| 이번 작업명 | TBD |
| 출발 기준 / 기존 결과 링크 | TBD |
| 이번 목표 | TBD |
| 포함: 추가·변경·제거할 범위 / 관련 원본 링크 | TBD |
| 이번에 확인할 결과 / AC·시험 원본 링크 | TBD |
| 제외·후속 범위와 이유 / 기존 백로그 링크 | TBD |

파일럿·기능 확장·릴리즈 모두 이 절을 사용한다. 종료하면 당시 범위·결과·남은 한계를 기존 검증 기록에 보존하고, 다음 범위가 합의됐을 때 이 절을 교체한다. 다음 작업이 없으면 종료 결과 링크와 다음 범위 미정을 남긴다. 파일럿마다 릴리즈하거나 버전별 장을 추가하지 않는다. 제품 정의에 영향이 있으면 1~3절도 함께 현행화한다.

## 5. Constraints And Open Decisions

| ID | 유형 | 제약 / 가정 / 질문 | 영향받는 범위 | 확인 담당·시점 / 대응·근거 |
| --- | --- | --- | --- | --- |
| RISK-001 | Risk / Assumption / Question | TBD | TBD | TBD |

제품 방향이나 이번 범위에 중요한 항목만 남긴다. 상세 문서에 원본이 있으면 연결하고, 답변은 해당 원본에 반영한다. CLI 실행 순서·세션 정리·작업 일지는 여기에 누적하지 않는다.

## 6. References And History

공통 용어·정책·합의 근거는 필요한 원본으로 연결한다. 기능별 상세 링크는 해당 절에 두고 같은 색인을 반복하지 않는다.

### Past Records

<!-- vulcan:state=history -->
<!-- 이전 범위/기준선·실제 검증·발행한 릴리즈의 기존 기록 링크만 둔다. 본문 재복사, 매 반복 새 Brief 파일, 별도 Git 증적은 요구하지 않는다. 기존 앵커를 보존해야 하면 해당 기록으로 연결한다. -->
