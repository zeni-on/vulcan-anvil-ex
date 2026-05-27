# DB명세서

```yaml
---
document_id: DOC-DATA-G2-002
title: Database Specification
title_ko: DB명세서
project: regression-simple-hello
gate: G2
status: N/A
version: v0.1
owner_role: Data Architect
author: Codex Orchestrator
reviewer: Technical Architect
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - REQ-001-01
  - ADR-002
change_reason: hello API 범위에서 DB 제외 결정 기록
---
```

## 1. 문서 목적

본 문서는 이번 Gate 2 범위에서 데이터베이스가 제외되었음을 명확히 기록한다. hello API는 저장 데이터, 테이블, 컬럼, ERD가 필요 없는 단순 응답 API다.

## 2. DB 적용 여부

| 항목 | 내용 |
| --- | --- |
| DB 사용 여부 | 사용하지 않음 |
| 제외 사유 | `REQ-001-01`은 API 호출 시 단순 문자열 `hello`를 반환하는 요구사항이며 영속 데이터가 필요 없다. |
| 관련 ADR | ADR-002 DB 제외 |
| 후속 처리 | 저장 데이터가 필요한 기능이 추가되면 별도 CR 또는 백로그로 Gate 1/2 영향도 분석 후 DB명세를 작성한다. |

## 3. 데이터 객체 목록

| DB-ID | 논리명 | 물리명 | 유형 | 관련 REQ | 관련 FUNC | 관련 PGM | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 저장 데이터 없음 | 해당없음 | 해당없음 | REQ-001-01 | FUNC-001 | PGM-001 | N/A |

## 4. ERD 산출물

| 구분 | 원본 DBML | 보기용 Export | 기준 | 상태 |
| --- | --- | --- | --- | --- |
| 논리 ERD | docs/artifacts/02-design/data/erd/logical/logical-erd.dbml | 해당없음 | DB 제외 사유 기록 | N/A |
| 물리 ERD | docs/artifacts/02-design/data/erd/physical/physical-erd.dbml | 해당없음 | DB 제외 사유 기록 | N/A |

## 5. 데이터 보안

| 항목 | 내용 | 관련 SEC |
| --- | --- | --- |
| 개인정보 | 처리하지 않음 | SEC-001 |
| 인증정보 | 처리하지 않음 | SEC-001 |
| 영속 데이터 | 저장하지 않음 | SEC-001 |
| 로그 출력 | 요청/응답에 민감정보가 없도록 유지 | SEC-001 |

## 6. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | hello API 범위에서 DB 제외 결정 기록 | Codex Orchestrator | Orchestrator | 사용자 |

## 7. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 데이터 객체에 `DB-ID`가 부여되었는가 | 해당없음 |
| 주요 컬럼이 프로젝트 단어사전의 `TERM`과 연결되었는가 | 해당없음 |
| 공공데이터 공통표준 검토 결과가 기록되었는가 | 해당없음 |
| 개인정보/인증정보/민감정보가 분류되었는가 | 예 - 처리하지 않음 |
| 보호 대상 컬럼이 `SEC`와 연결되었는가 | 해당없음 |
| 프로그램 설계서에서 참조 가능한 수준으로 키/제약조건이 정의되었는가 | 해당없음 |
| 논리/물리 ERD DBML 원본이 작성되었는가 | 해당없음 사유 기록 |
| ERD export 이미지 또는 PDF가 사람이 검토 가능한 형태로 생성되었는가 | 해당없음 |
| DB명세서의 테이블/컬럼/관계가 DBML과 일치하는가 | 해당없음 |
