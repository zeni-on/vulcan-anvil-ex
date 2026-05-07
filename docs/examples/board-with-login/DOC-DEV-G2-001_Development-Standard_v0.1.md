# 개발표준정의서

```yaml
---
document_id: DOC-DEV-G2-001
title: Development Standard
title_ko: 개발표준정의서
project: Board With Login Sample
gate: G2
status: Draft
version: v0.1
owner_role: Technical Architect
author: Codex
reviewer: Documentation Curator
approver: Approver
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - REQ-001
  - REQ-002
  - REQ-003
  - REQ-004
  - REQ-005
  - REQ-006
  - PGM-001
  - PGM-006
  - UT-001
  - IT-005
change_reason: 로그인 게시판 샘플 구현 전 개발 표준 초안 작성
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플을 구현할 때 사용할 개발 언어, 패키지 구조, 아키텍처 패턴, 코드 컨벤션, 주석 컨벤션, 빌드/실행/테스트 방법, 에이전트 작업 규칙을 정의한다.

본 문서는 샘플 구현의 제약 조건이다. 에이전트와 개발자는 구현 전에 요구사항정의서, 기능명세서, 프로그램명세서, DB명세서, 화면설계서, 테스트케이스 정의서와 함께 본 문서를 확인해야 한다.

## 2. 적용 범위

| 항목 | 내용 |
| --- | --- |
| 적용 시스템 | 로그인 게시판 샘플 |
| 적용 모듈 | 회원가입, 로그인/로그아웃, 게시글 목록/상세/작성/수정/삭제 |
| 적용 언어 | Python |
| 적용 프레임워크 | FastAPI |
| 적용 DB | SQLite |
| 적용 테스트 도구 | pytest, FastAPI TestClient |
| 제외 범위 | 실제 운영 배포, 외부 OAuth, 이메일 인증, 관리자 기능 |

## 3. 기술 스택

| 구분 | 표준 | 버전/범위 | 선정 사유 | 비고 |
| --- | --- | --- | --- | --- |
| Language | Python | 3.11 이상 권장 | 테스트 작성과 에이전트 구현 검증이 단순함 |  |
| Web Framework | FastAPI | 안정 버전 | API 문서화와 요청 검증이 쉬움 |  |
| Database | SQLite | 개발/테스트용 | 샘플 검증에 별도 DB 서버가 필요 없음 |  |
| ORM/Query | SQLAlchemy 또는 SQLModel | 구현 시 선택 | Repository 계층 검증 | 한 가지로 고정 후 변경 금지 |
| Password Hash | bcrypt 계열 | 구현 시 라이브러리 확정 | 비밀번호 평문 저장 금지 | SEC-001 |
| Test | pytest | 안정 버전 | UT/IT 연결이 명확함 |  |
| HTTP Test | FastAPI TestClient | 안정 버전 | API 통합 테스트 작성 |  |
| Lint/Format | ruff | 권장 | 빠른 정적 검사와 포맷 | 샘플에서는 필수 실패 조건은 아님 |

## 4. 아키텍처 및 패키지 구조

아키텍처 패턴:

```text
Router -> Service -> Repository -> Database
```

패키지 구조:

```text
sample-app/
  app/
    main.py
    api/
      auth.py
      posts.py
    services/
      auth_service.py
      post_service.py
    repositories/
      user_repository.py
      post_repository.py
    models/
      user.py
      post.py
    schemas/
      auth.py
      post.py
    core/
      config.py
      security.py
      errors.py
    resources/
      messages.ko.yml
    db/
      session.py
      init_db.py
  tests/
    unit/
      test_auth_service.py
      test_post_service.py
    integration/
      test_auth_api.py
      test_post_api.py
    conftest.py
```

| 계층 | 책임 | 허용 의존성 | 금지 사항 |
| --- | --- | --- | --- |
| Router | HTTP 요청/응답, 인증 의존성, 상태 코드 | Service, Schema | DB 직접 접근, 비밀번호 해시 직접 처리 |
| Service | 업무 규칙, 인증/권한 판단, 트랜잭션 흐름 | Repository, Security | HTTP 응답 객체 직접 생성 |
| Repository | 사용자/게시글 데이터 접근 | DB Session, Model | 권한 정책 판단 |
| Model | DB 테이블 구조 |  | 업무 로직 포함 |
| Schema | API 입출력 검증 |  | DB 접근 |
| Core | 보안, 오류, 설정 공통 기능 |  | 개별 업무 기능 포함 |

## 5. 코드 컨벤션

| 항목 | 규칙 | 예외 |
| --- | --- | --- |
| 네이밍 | Python 표준 `snake_case`를 사용한다. 클래스는 `PascalCase`를 사용한다. | 외부 라이브러리 규칙 |
| 함수 크기 | 한 함수는 하나의 책임을 가진다. 복잡한 흐름은 Service 메서드로 분리한다. | 단순 DTO 변환 |
| 모듈 분리 | 인증과 게시글 기능은 API/Service/Repository를 분리한다. | 공통 보안/오류는 `core`에 둔다. |
| 예외 처리 | 업무 오류는 공통 오류 코드로 변환한다. | 테스트 내부 예외 |
| 로그 | 비밀번호, 토큰, 해시값, 본문 원문 등 민감정보를 로그에 남기지 않는다. | 없음 |
| 설정값 | DB URL, 토큰 키 등은 `core/config.py`로 모은다. | 테스트 전용 fixture |
| 외부 의존성 | 새 라이브러리 추가 시 개발표준 또는 구현 메모에 사유를 남긴다. | 테스트 보조 라이브러리 |

## 6. 주석 컨벤션

기본 원칙:

- 코드가 그대로 설명하는 내용은 주석으로 반복하지 않는다.
- 요구사항, 보안 기준, 추적 ID, 복잡한 권한 판단은 주석 또는 docstring에 남길 수 있다.
- 임시 우회 처리는 `ISSUE-ID` 또는 `DEC-ID`와 함께 남긴다.

추적 ID 표기 예:

```python
def signup(...):
    """REQ-001 / PGM-001 / SEC-001: 회원가입 처리."""
```

테스트 ID 표기 예:

```python
def test_UT_001_signup_success(...):
    """UT-001 / AC-001: 정상 회원가입."""
```

## 7. API 및 오류 응답 규칙

성공 응답 표준:

```json
{
  "data": {},
  "message": "OK"
}
```

오류 응답 표준:

```json
{
  "error": {
    "code": "ERR-001",
    "message": "요청을 처리할 수 없습니다."
  }
}
```

| 오류 코드 | 의미 | HTTP 상태 | 관련 보안 기준 |
| --- | --- | ---: | --- |
| ERR-001 | 이메일 중복 | 409 | KISA-SD-2021 SR1-1, SR1-9 |
| ERR-002 | 인증 실패 | 401 | KISA-SD-2021 SR2-1, SR2-2 |
| ERR-003 | 인증 필요 | 401 | KISA-SD-2021 SR2-1 |
| ERR-004 | 권한 없음 | 403 | KISA-SD-2021 SR2-4 |
| ERR-005 | 게시글 없음 | 404 | KISA-SD-2021 SR3-1 |
| ERR-006 | 입력값 오류 | 422 | KISA-SD-2021 SR1-1, SR1-9 |
| ERR-007 | 서버 오류 | 500 | KISA-SD-2021 SR3-1 |

## 8. 메시지 관리 규칙

기본 원칙:

- 사용자에게 노출되는 메시지는 코드에 직접 하드코딩하지 않는다.
- 사용자 노출 메시지는 `app/resources/messages.ko.yml`에서 관리한다.
- API 응답은 메시지 코드와 메시지 본문을 함께 반환한다.
- 테스트는 원칙적으로 메시지 본문보다 `ERR-001`, `MSG-001` 같은 메시지 코드를 검증한다.
- 인증/권한/보안 오류 메시지는 계정 존재 여부, 내부 구조, 권한 판단 상세를 노출하지 않는다.
- 문구 변경은 코드 변경 없이 메시지 리소스 수정으로 처리할 수 있어야 한다.

메시지 리소스:

```text
app/resources/messages.ko.yml
```

메시지 코드 예:

```yaml
MSG-001: 정상 처리되었습니다.
ERR-001: 이미 사용 중인 이메일입니다.
ERR-002: 이메일 또는 비밀번호가 올바르지 않습니다.
ERR-003: 로그인이 필요합니다.
ERR-004: 접근 권한이 없습니다.
ERR-005: 게시글을 찾을 수 없습니다.
ERR-006: 입력값을 확인해 주세요.
ERR-007: 요청을 처리하는 중 오류가 발생했습니다.
```

| 구분 | 하드코딩 허용 여부 | 관리 방식 | 비고 |
| --- | --- | --- | --- |
| 사용자 오류 메시지 | 금지 | `messages.ko.yml` | API `error.message` |
| 사용자 성공/안내 메시지 | 금지 | `messages.ko.yml` | API `message` |
| 입력값 검증 메시지 | 금지 | `messages.ko.yml` | Validation 응답 |
| 보안 관련 메시지 | 금지 | `messages.ko.yml` | 노출 정보 최소화 |
| 로그 내부 메시지 | 허용 | 코드 또는 상수 | 민감정보 출력 금지 |
| 테스트 설명 문자열 | 허용 | 테스트 코드 | 메시지 본문 검증 지양 |
| 개발자 전용 assertion | 허용 | 코드 | 사용자 노출 금지 |

구현 예:

```python
raise AppError("ERR-001")
```

응답 예:

```json
{
  "error": {
    "code": "ERR-001",
    "message": "이미 사용 중인 이메일입니다."
  }
}
```

## 9. DB 접근 및 데이터 표준 규칙

- DB 객체는 DB명세서의 `DB-001 users`, `DB-002 posts`를 따른다.
- DB 컬럼명은 DB명세서의 물리명과 일치시킨다.
- API 필드명은 개발자 사용성과 일관성을 위해 영어 `snake_case`를 사용한다.
- 프로젝트 단어사전에서 `확인필요` 상태인 용어는 실제 프로젝트 적용 시 공공데이터 공통표준 확인 후 상태를 갱신한다.
- 비밀번호 원문은 저장하지 않고 `password_hash`만 저장한다.

## 10. 보안 구현 규칙

| 보안 영역 | 구현 규칙 | 참조 기준 | 검증 테스트 |
| --- | --- | --- | --- |
| 입력값 검증 | 이메일 형식, 필수값, 길이 제한은 서버에서 검증한다. | KISA-SD-2021 SR1-1, SR1-9 | UT-002, UT-007 |
| 인증 | 로그인 성공 시 인증 토큰 또는 세션을 발급한다. | KISA-SD-2021 SR2-1 | UT-003, IT-002 |
| 인증 실패 | 로그인 실패 메시지는 계정 존재 여부를 과도하게 노출하지 않는다. | KISA-SD-2021 SR2-2, SR3-1 | UT-004 |
| 권한 | 게시글 작성/수정/삭제는 인증 사용자를 확인한다. | KISA-SD-2021 SR2-4 | UT-008, UT-011 |
| 비밀번호 | 비밀번호는 평문 저장 금지, bcrypt 계열 해시를 사용한다. | KISA-SD-2021 SR2-3, SR2-6, SR2-7 | UT-001, UT-003 |
| 중요정보 전송 | 실제 운영 전환 시 HTTPS 전송을 전제로 한다. | KISA-SD-2021 SR2-8 | IT-002 |
| 예외처리 | 내부 예외 상세를 사용자 응답에 노출하지 않는다. | KISA-SD-2021 SR3-1 | UT-004, UT-011 |

## 11. 테스트 컨벤션

| 항목 | 규칙 |
| --- | --- |
| 테스트 파일명 | 기능별로 `test_auth_service.py`, `test_post_api.py`처럼 작성한다. |
| 테스트 함수명 | `test_{ID}_{summary}` 형식을 사용한다. 예: `test_UT_001_signup_success`. |
| 단위테스트 기준 | Service 또는 Repository 단위의 업무 규칙과 보안 규칙을 검증한다. |
| 통합테스트 기준 | API 요청부터 DB 반영까지의 흐름을 검증한다. |
| 성능테스트 기준 | `PT-001`은 샘플 규모에서 목록 API 응답시간 기준을 확인한다. |
| 테스트 데이터 | 테스트마다 독립 데이터를 사용하고 테스트 간 상태 공유를 피한다. |
| 테스트 증적 | 테스트 실행 명령, 결과 요약, 실패 로그를 Gate 4 산출물에 연결할 수 있게 보관한다. |

대표 테스트 함수명:

```text
test_UT_001_signup_success
test_UT_011_other_user_cannot_modify_or_delete
test_IT_001_signup_then_login
test_PT_001_post_list_response_time
```

## 12. 빌드, 실행, 테스트 명령

초기 샘플 구현 시 다음 명령을 기준으로 한다. 실제 의존성 파일명이 확정되면 본 표를 갱신한다.

| 목적 | 명령 | 비고 |
| --- | --- | --- |
| 가상환경 생성 | `python -m venv .venv` | Windows/WSL 환경별 활성화 명령은 README에 보완 |
| 의존성 설치 | `python -m pip install -r requirements.txt` | 샘플 앱 루트 기준 |
| 개발 서버 실행 | `uvicorn app.main:app --reload` | 샘플 앱 루트 기준 |
| 단위 테스트 | `pytest tests/unit` | UT 증적 |
| 통합 테스트 | `pytest tests/integration` | IT 증적 |
| 전체 테스트 | `pytest` | Gate 4 증적 |
| 정적 검사 | `ruff check .` | 도입 시 |
| 포맷 | `ruff format .` | 도입 시 |

## 13. 에이전트 작업 규칙

에이전트는 다음 순서를 따른다.

1. 관련 요구사항정의서, 기능명세서, 프로그램명세서, 화면설계서, DB명세서, 테스트케이스 정의서를 확인한다.
2. 구현 대상의 `REQ/FUNC/PGM/SCR/DB/SEC/UT/IT/PT` ID를 확인한다.
3. 본 문서의 패키지 구조와 계층 의존성 규칙을 따른다.
4. Router에서 DB를 직접 호출하지 않는다.
5. 문서에 없는 API, DB 컬럼, 테스트를 임의로 추가하지 않는다.
6. 필요한 변경이 있으면 먼저 `ISSUE` 또는 `CR` 후보로 기록한다.
7. 사용자 노출 메시지를 코드에 직접 하드코딩하지 않고 `messages.ko.yml`의 메시지 코드를 사용한다.
8. 구현 후 테스트 결과와 증적을 추적표에 연결할 수 있게 남긴다.

## 14. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 구현 전 개발 표준 초안 작성 | Codex |  |  |
