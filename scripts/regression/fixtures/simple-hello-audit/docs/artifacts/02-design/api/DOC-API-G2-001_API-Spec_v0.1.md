# API 정의서

```yaml
---
document_id: DOC-API-G2-001
title: API Specification
title_ko: API 정의서
project: regression-simple-hello
gate: G2
status: Baseline Candidate
version: v0.1
owner_role: API Designer
author: Codex Orchestrator
reviewer: Technical Architect
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - API-001
  - REQ-001-01
  - FUNC-001
  - PGM-001
  - SEC-001
change_reason: Gate 2 hello API 계약 작성
---
```

## 1. 문서 목적

본 문서는 hello API의 HTTP 요청/응답 계약을 정의한다. 본 문서에 없는 API, 필드, 상태코드를 구현 단계에서 임의로 추가하지 않는다.

## 2. API 목록

| API-ID | API명 | Method | Path | 관련 PGM | 관련 SCR | 인증 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| API-001 | hello 응답 조회 API | GET | `/hello` | PGM-001 | 해당없음 | N | Baseline Candidate |

## 3. 공통 계약

| 항목 | 기준 |
| --- | --- |
| Base URL | 로컬 실행 기준 `http://127.0.0.1:8000` 후보 |
| 요청 Content-Type | 요청 본문 없음 |
| 응답 Content-Type | `text/plain; charset=utf-8` |
| 인증 방식 | 해당없음 |
| 권한 실패 | 해당없음 |
| 공통 오류 응답 | 내부 오류 발생 시 stack trace를 응답에 노출하지 않음. 상세 포맷은 구현 스택 기본값 또는 프로그램 설계의 오류 계약을 따른다. |
| 날짜/시간 형식 | 해당없음 |
| 필드명 규칙 | 해당없음 |

## 4. API 상세

### API-001 hello 응답 조회 API

| 항목 | 내용 |
| --- | --- |
| API-ID | API-001 |
| Method | GET |
| Path | `/hello` |
| 설명 | 호출자에게 단순 문자열 `hello`를 반환한다. |
| 관련 요구사항 | REQ-001-01 |
| 관련 인수기준 | AC-001-01 / AC-001-02 |
| 관련 기능 | FUNC-001 |
| 관련 프로그램 | PGM-001 |
| 관련 화면 | 해당없음 |
| 관련 보안가이드 | SEC-001 |
| 인증 필요 | N |
| 권한 조건 | 없음 |

#### 4.1 Request

| 위치 | TERM-ID | 필드명 | 타입 | 필수 | 검증 기준 | 예시 | 관련 SEC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 해당없음 | 해당없음 | 해당없음 | N | 요청 본문, query, path parameter 없음 | 해당없음 | SEC-001 |

요청 예시:

```http
GET /hello HTTP/1.1
Host: 127.0.0.1:8000
```

#### 4.2 Response

| 상태코드 | TERM-ID | 필드명 | 타입 | 필수 | 설명 | 예시 | 보안 분류 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 200 | 해당없음 | response body | string | Y | hello 응답 본문 | `hello` | 일반 |

응답 예시:

```text
hello
```

#### 4.3 Error

| 오류 ID | HTTP Status | error.code | 사용자 메시지 | 발생 조건 | 처리 기준 | 관련 AC/SEC |
| --- | ---: | --- | --- | --- | --- | --- |
| ERR-API-001 | 500 | INTERNAL_ERROR | 요청을 처리할 수 없습니다. | 예상하지 못한 서버 오류 | 내부 stack trace 및 환경정보를 응답에 노출하지 않는다. | AC-002-01 / SEC-001 |

오류 응답 예시는 구현 스택의 공통 오류 처리 또는 프로그램 설계의 오류 계약을 따른다. Gate 3에서 오류 응답 검증이 필요하면 별도 IT로 전개한다.

#### 4.4 처리 및 보안 기준

| 순서 | 처리 내용 | 관련 PGM | 관련 SEC/SR | 실패 처리 |
| ---: | --- | --- | --- | --- |
| 1 | Router가 `GET /hello` 요청을 수신한다. | PGM-001 | SEC-001 / KISA-SD-2021 SR3-1 | 라우팅 실패 시 404 |
| 2 | Service가 `hello` 문자열을 반환한다. | PGM-001 | SEC-001 | 내부 오류 시 ERR-API-001 |
| 3 | Router가 `text/plain` 응답으로 반환한다. | PGM-001 | SEC-001 | 내부 상세 미노출 |

#### 4.5 테스트 연결

| 테스트 ID | 테스트 유형 | 검증 내용 | 관련 AC/SEC |
| --- | --- | --- | --- |
| UT-001 후보 | Unit | HelloService가 `hello`를 반환한다. | AC-001-02 |
| IT-001 후보 | Integration | `GET /hello`가 200과 `hello` 본문을 반환한다. | AC-001-01 / AC-001-02 |
| IT-002 후보 | Integration/Command | 로컬 실행 후 명령 기반 호출이 재현된다. | AC-002-01 / SEC-001 |

## 5. 화면/API/DB 매핑

| API-ID | 화면 항목명 | API 필드명 | DB 컬럼명 | TERM-ID | 비고 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 해당없음 | response body | 해당없음 | 해당없음 | 화면/DB 제외 |

## 6. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 API에 `API-ID`가 부여되었는가 | 예 |
| API가 `REQ`, `AC`, `FUNC`, `PGM`, `SCR`과 연결되었는가 | 예 - SCR은 해당없음 |
| 요청/응답 필드와 검증 기준이 작성되었는가 | 예 |
| 오류 응답과 상태코드가 작성되었는가 | 예 |
| 인증/권한/보안 기준이 `SEC-ID`와 연결되었는가 | 예 |
| 요청/응답 예시가 작성되었는가 | 예 |
| 테스트 ID가 연결되었는가 | Gate 3 후보로 연결 |

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | Gate 2 hello API 계약 작성 | Codex Orchestrator | Orchestrator | 사용자 |
