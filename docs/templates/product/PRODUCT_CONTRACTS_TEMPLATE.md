# Product Contracts

---
document_id: PROD-CONTRACT
title: Product Contracts
title_ko: 제품 구현 계약 인덱스
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
  - docs/product/PRODUCT_BRIEF.md
  - docs/product/PRODUCT_ARCHITECTURE.md
---

## 1. Contract Policy

이 문서는 상세 설계서 복사본이 아니라 Product profile의 구현 계약 진입점이다.
상세 API/DB/UI/보안 설계가 필요한 경우 `docs/artifacts/02-design/` 산출물로 분리하고, 이 문서에서는 링크와 핵심 계약만 유지한다.

## 2. API Contracts

| API ID | Method | Path / Entry | Request | Response | 관련 Scenario | 상세 문서 |
| --- | --- | --- | --- | --- | --- | --- |
| API-001 | TBD | TBD | TBD | TBD | SCN-001 | TBD |

## 3. Data Contracts

| DATA/DB ID | 이름 | 주요 필드 | 보안 분류 | 관련 API/Scenario | 상세 문서 |
| --- | --- | --- | --- | --- | --- |
| DATA-001 | TBD | TBD | 일반 / 식별정보 / 개인정보 / 인증정보 / 민감정보 | API-001, SCN-001 | TBD |

### 3.1 ERD / Data Model

ERD, DBML, schema export가 있으면 기존 상세 설계 폴더를 재사용한다.
Product에서는 이 상세 문서가 필수가 아니지만, 데이터 계약이 구현/릴리즈 판단에 중요해지면 `PRODUCT_DATA_MODEL.md`로 분리한다.

| 항목 | 권장 경로 | 내용 |
| --- | --- | --- |
| Product Data Model | `docs/artifacts/02-design/data/PRODUCT_DATA_MODEL.md` | 핵심 데이터 의미, 보안 분류, persistence shape |
| Logical ERD | `docs/artifacts/02-design/data/erd/logical/` | 업무 엔티티와 관계 |
| Physical ERD / DBML | `docs/artifacts/02-design/data/erd/physical/` | 테이블, 컬럼, 제약조건, 인덱스 |
| Export / Image | `docs/artifacts/02-design/data/erd/exports/` | PNG, SVG, PDF 등 검토용 export |

| ERD/DATA ID | 산출물 | 기준 | 관련 Scenario |
| --- | --- | --- | --- |
| DATA-ERD-001 | TBD | TBD | SCN-001 |

## 4. UI Contracts

| UI/SCR ID | 화면/상호작용 | 주요 상태 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- |
| UI-001 | TBD | Empty / Loading / Success / Error | SCN-001 | REG-001 |

### 4.1 UI Design / Publishing Baseline

UI design과 퍼블리싱 산출물은 Product에서도 구현자가 볼 수 있는 기준선으로 남긴다.
Figma, 이미지 시안, HTML/CSS/JS prototype, screenshot baseline 중 실제로 있는 것을 연결하고,
없으면 "없음"이 아니라 어떤 수준의 UI 기준으로 구현할지 적는다.
상세 기준이 필요하면 `PRODUCT_UI_CONTRACT.md`로 분리한다.

| 항목 | 권장 경로 | 내용 |
| --- | --- | --- |
| Product UI Contract | `docs/artifacts/02-design/screen/PRODUCT_UI_CONTRACT.md` | 화면 흐름, 상태, UI 기준선, 증적 계획 |
| UI Design | `docs/artifacts/02-design/screen/images/` | 화면 흐름, 와이어프레임, 시안, 디자인 결정 |
| UI Publishing | `docs/artifacts/02-design/screen/prototypes/` | HTML/CSS/JS prototype, static baseline, 구현 기준 파일 |
| UI Evidence 후보 | `docs/artifacts/04-review/evidence/ui/` | Gate 4 또는 release regression screenshot |

| UI Baseline ID | 기준 산출물 | 유지해야 할 요소 | 변경 허용 범위 | 관련 UI/Scenario |
| --- | --- | --- | --- | --- |
| UIBASE-001 | TBD | TBD | TBD | UI-001, SCN-001 |

## 5. Security Contracts

Product profile의 보안 계약은 `docs/core/PRODUCT_PROFILE_BASELINE.md`, `docs/core/SECURITY_BASELINE.md`, `docs/core/REFERENCE_STANDARDS.md`를 기준으로 작성한다.
KISA/SR 매핑은 선택 참고이지만, OWASP/CWE 기반의 제품 보안 판단은 비워두지 않는다.

| SEC ID | 보안 계약 | 적용 대상 | 기준/참조 | 관련 Scenario | 검증 |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | TBD | API-001 / DATA-001 / UI-001 | OWASP ASVS / OWASP Top 10 / CWE | SCN-001 | SEC-REG-001 |

## 6. Build / Deploy / Runtime Contracts

빌드와 배포는 `PRODUCT_ARCHITECTURE.md`의 Runtime And Deployment Assumptions와 연결한다.
Product에서는 감리 제출용 배포 아키텍처가 아니더라도, 사용자가 실행/검증할 수 있는 최소 명령과 환경 변수는 비워두지 않는다.
상세 개발/빌드/배포 기준이 필요하면 `docs/artifacts/02-design/development-standard/PRODUCT_ENGINEERING_GUIDE.md`로 분리한다.

| Contract ID | 항목 | 기준 | 검증/증적 |
| --- | --- | --- | --- |
| BUILD-001 | Build command | TBD | REG-001 |
| RUN-001 | Local run command | TBD | REG-001 |
| DEPLOY-001 | Deployment target / packaging | TBD | REG-001 |
| CONF-001 | Required env/config/secrets | TBD | SEC-REG-001 |

## 7. Security And Data Baseline

| 항목 | 기준 | 적용 위치 | 검증 |
| --- | --- | --- | --- |
| Security | docs/core/PRODUCT_PROFILE_BASELINE.md, docs/core/SECURITY_BASELINE.md | TBD | REG-001 |
| Data | docs/core/DATA_STANDARD_RULES.md | TBD | REG-001 |

## 8. Contract Gaps

| Gap ID | 내용 | 영향 | 후속 판단 |
| --- | --- | --- | --- |
| GAP-001 | TBD | TBD | TBD |
