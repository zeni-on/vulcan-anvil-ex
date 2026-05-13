# 프로그램명세서

```yaml
---
document_id: DOC-CORE-G2-002
title: Program Specification
title_ko: 프로그램명세서
project: 프로젝트명
gate: G2
status: Draft
version: v0.1
owner_role: Technical Architect
author: 작성자 또는 에이전트
reviewer: Security Reviewer
approver: Approver
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
related_ids:
  - PGM-001
change_reason: 최초 초안 작성
---
```

## 1. 문서 목적

본 문서는 기능을 구현하는 프로그램, API, 배치, 모듈, 서비스의 처리 기준을 정의한다.

프로그램명세서는 “어떤 프로그램이 어떤 입력을 받아 어떤 로직으로 처리하고 어떤 결과를 반환하는가”를 설명한다.

API가 있는 경우 프로그램명세서는 API 목록과 처리 모듈의 책임을 요약하고, 요청/응답/상태코드/오류/인증/예시는 별도 API 정의서(`docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md`)에서 상세화한다.

## 2. 작성 기준

- 프로그램은 `PGM-001` 형식으로 부여한다.
- 프로그램은 하나 이상의 `REQ`, `AC`, `FUNC`와 연결한다.
- 프로그램의 입력/출력 항목은 프로젝트 단어사전 `TERM`과 연결한다.
- 보안 민감 프로그램은 `SEC`와 외부 보안 기준 `SR`을 함께 기록한다.
- 단위테스트는 프로그램 로직을 검증하되, 검증 이유는 `AC`, `SEC`, `NREQ` 중 하나에서 나와야 한다.
- REST, GraphQL, 내부 HTTP API가 있으면 API 정의서의 `API-ID`와 연결한다.
- API가 없으면 API 관련 칸은 `해당없음`으로 쓰고, 프로그램 유형은 `Module`, `Service`, `Batch`, `Component`, `CLI`처럼 실제 유형으로 작성한다.

## 3. 프로그램 목록

| PGM-ID | 프로그램명 | 유형 | 관련 FUNC | 관련 SCR | 관련 DB | 관련 SEC | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PGM-001 |  | Module | FUNC- | SCR- | DB- | SEC- | Draft |

## 4. 프로그램 상세

### PGM-001 프로그램명

| 항목 | 내용 |
| --- | --- |
| PGM-ID | PGM-001 |
| 프로그램명 |  |
| 유형 | Module |
| 설명 |  |
| 관련 요구사항 | REQ- |
| 관련 인수기준 | AC- |
| 관련 기능 | FUNC- |
| 관련 화면 | SCR- |
| 관련 데이터 | DB- |
| 관련 보안항목 | SEC- |
| 관련 API | 해당없음 |

#### 4.1 인터페이스

| 항목 | 내용 |
| --- | --- |
| 호출 방식 | Internal Call |
| 엔드포인트/함수명 |  |
| Method | 해당없음 |
| 인증 필요 | 해당없음 |
| 권한 조건 |  |
| 요청 Content-Type | 해당없음 |
| 응답 Content-Type | 해당없음 |
| API 정의서 | 해당없음 |

#### 4.2 입력 파라미터

| 순번 | TERM-ID | 파라미터명 | 위치 | 필수 | 타입/도메인 | 검증 기준 | 관련 SEC/SR |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | TERM-001 |  | Body / Query / Path / Header | Y/N | DOMAIN- |  | SEC- / KISA-SD-2021 SR- |

#### 4.3 출력 항목

| 순번 | TERM-ID | 필드명 | 타입/도메인 | 설명 | 보안 분류 | 비고 |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | TERM-001 |  | DOMAIN- |  | 일반 |  |

#### 4.4 처리 흐름

| 순서 | 처리 내용 | 관련 AC | 관련 SEC/SR | 예외 |
| ---: | --- | --- | --- | --- |
| 1 |  | AC- | SEC- / KISA-SD-2021 SR- |  |

#### 4.5 예외 및 오류 처리

| 오류 ID | 발생 조건 | 응답 코드/메시지 | 처리 방식 | 관련 AC/SEC |
| --- | --- | --- | --- | --- |
| ERR-001 |  |  |  | AC-/SEC- |

#### 4.6 데이터 접근

| DB-ID | 대상 | 동작 | 조건 | 트랜잭션 | 비고 |
| --- | --- | --- | --- | --- | --- |
| DB-001 |  | Create / Read / Update / Delete |  | Y/N |  |

#### 4.7 보안 설계

| SEC-ID | 참조 표준 | 보안 설계 내용 | 적용 위치 | 검증 테스트 |
| --- | --- | --- | --- | --- |
| SEC-001 | KISA-SD-2021 SR- |  | 입력검증 / 인증 / 인가 / 암호화 / 예외처리 / 세션 | UT-/IT- |

#### 4.8 단위테스트 연결

| UT-ID | 테스트명 | 검증 대상 | 관련 AC/SEC/NREQ | 비고 |
| --- | --- | --- | --- | --- |
| UT-001 |  | PGM-001 | AC- / SEC- / NREQ- |  |

## 5. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | YYYY-MM-DD | 최초 초안 작성 |  |  |  |

## 6. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 프로그램에 `PGM-ID`가 부여되었는가 |  |
| 프로그램이 `REQ`, `AC`, `FUNC`와 연결되었는가 |  |
| 입력/출력 항목이 프로젝트 단어사전과 연결되었는가 |  |
| 보안 설계에 `SEC-ID`와 `SR-ID`가 연결되었는가 |  |
| 예외/오류 처리 기준이 작성되었는가 |  |
| 단위테스트가 `AC`, `SEC`, `NREQ`와 연결되었는가 |  |
