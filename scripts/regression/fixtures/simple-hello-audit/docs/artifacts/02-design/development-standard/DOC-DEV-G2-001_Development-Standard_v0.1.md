# 개발표준정의서

```yaml
---
document_id: DOC-DEV-G2-001
title: Development Standard
title_ko: 개발표준정의서
project: regression-simple-hello
gate: G2
status: Baseline Candidate
version: v0.1
owner_role: Technical Architect
author: Codex Orchestrator
reviewer: Orchestrator
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - REQ-001
  - FUNC-001
  - API-001
  - PGM-001
  - SEC-001
  - NREQ-001
change_reason: Gate 2 Python/FastAPI 개발표준 작성
---
```

## 1. 문서 목적

본 문서는 Python hello API 구현자가 따라야 할 언어, 패키지 구조, 코드 컨벤션, 보안/로그 기준, 실행/테스트 명령 기준을 정의한다. 구현 단계에서는 본 문서가 `docs/core/TECH_STACK_BASELINES.md`보다 우선한다.

## 2. 적용 범위

| 항목 | 내용 |
| --- | --- |
| 적용 시스템 | Python hello API |
| 적용 모듈 | `backend/` |
| 적용 언어 | Python |
| 적용 프레임워크 | FastAPI + Uvicorn |
| 적용 기술스택 베이스라인 | `TECH_STACK_BASELINES.md` §8 Python/FastAPI |
| 적용 테스트 도구 | pytest, FastAPI TestClient |
| 제외 범위 | DB, 프론트엔드, 인증/인가, 배포 자동화 |

## 3. 기술 스택

| 구분 | 표준 | 버전/범위 | 선정 사유 | 비고 |
| --- | --- | --- | --- | --- |
| Language | Python | 3.11+ 후보 | 로컬 API 구현과 테스트에 적합 | 실제 설치 버전은 Impl/QA에서 확인 |
| Runtime | CPython | 3.11+ | 일반 로컬 실행 기준 |  |
| Web Framework | FastAPI | 최신 호환 버전 | 작은 API, TestClient, 타입 힌트 활용 | ADR-001 |
| ASGI Server | Uvicorn | FastAPI 호환 | 로컬 개발 서버 |  |
| Database | 해당없음 | 해당없음 | 저장 데이터 없음 | ADR-002 |
| ORM/Query | 해당없음 | 해당없음 | DB 제외 |  |
| Test | pytest + FastAPI TestClient | 프로젝트 의존성에 고정 | unit/integration 검증 | Gate 3에서 테스트 ID 확정 |
| Build/Package | pip + requirements 또는 pyproject | Impl에서 확정 | 최소 의존성 관리 | lock 전략은 Impl 계획에서 보강 가능 |
| Lint/Format | ruff 후보 | 선택 | 작은 프로젝트라도 정적 검사 가능 | 설치 불가 시 Not Run 사유 기록 |
| DB Pool 기준 | 해당없음 | 해당없음 | DB를 사용하지 않음 | DB 추가 시 별도 설계 필요 |
| Lombok 기준 | 해당없음 | 해당없음 | Java/Spring 미사용 | Python 프로젝트라 적용 제외 |

적용 베이스라인:

| 영역 | 선택 | 참조 베이스라인 | 프로젝트 조정사항 |
| --- | --- | --- | --- |
| Backend | Python/FastAPI | `TECH_STACK_BASELINES.md` §8 | DB 없는 Router -> Service 구조 |
| Backend Security | FastAPI 기본 + 프로젝트 보안가이드 | `SECURITY_BASELINE.md`, `DOC-SEC-G2-001` | 인증/인가 제외, 오류정보 노출 방지 |
| Frontend | 해당없음 | 해당없음 | UI 제외 |
| Test/E2E | pytest/TestClient | `TECH_STACK_BASELINES.md` §8 | Playwright/UI 테스트 제외 |

## 4. 아키텍처 및 패키지 구조

아키텍처 패턴:

```text
FastAPI App -> Router -> Service
```

패키지 구조:

```text
regression-simple-hello/
  backend/
    app/
      __init__.py
      main.py
      api/
        __init__.py
        hello.py
      services/
        __init__.py
        hello_service.py
    tests/
      test_hello_service.py
      test_hello_api.py
    requirements.txt 또는 pyproject.toml
  docs/
```

| 계층 | 책임 | 허용 의존성 | 금지 사항 |
| --- | --- | --- | --- |
| App Entry | FastAPI app 생성, router 등록 | Router | 업무 로직 직접 작성 |
| API/Router | 요청/응답, HTTP 상태, Content-Type | Service | DB 직접 접근, 응답값 임의 변경 |
| Service | `hello` 응답 규칙 | 없음 | HTTP 객체 직접 의존 |
| Schema/DTO | 이번 범위 해당없음 | 해당없음 | 불필요한 JSON DTO 추가 |
| Test | public contract 검증 | app/service | 문서에 없는 기능 검증 |

## 5. 코드 컨벤션

| 항목 | 규칙 | 예외 |
| --- | --- | --- |
| 네이밍 | 모듈/함수/변수는 `snake_case`, 클래스는 `PascalCase` | 없음 |
| 함수 크기 | 단일 책임 유지. Router는 HTTP 변환, Service는 응답 값 제공 | 없음 |
| 모듈 분리 | `api`와 `services` 분리 | 단일 파일 임시 구현은 scaffold에서만 허용 가능 |
| 예외 처리 | 내부 오류 상세를 응답에 노출하지 않음 | 개발 중 stack trace는 로컬 콘솔에 한정 |
| 로그 | 민감정보, 환경변수, stack trace 응답 노출 금지 | 현재 범위 민감정보 없음 |
| 설정값 | host/port는 실행 명령 또는 환경으로 조정 가능 | 개발 기본값 허용 |
| 외부 의존성 | FastAPI, Uvicorn, pytest, httpx/TestClient 계열로 최소화 | 추가 의존성은 Run에 사유 기록 |

언어/프레임워크별 상세 기준:

| 스택 | 적용 규칙 | 예외/조정 사유 |
| --- | --- | --- |
| Python/FastAPI | Router -> Service, Pydantic은 입력/JSON 계약이 생길 때만 사용, pytest/TestClient 사용 | 이번 API는 요청/JSON DTO 없음 |

Java/Spring 전용 기준 적용 여부:

| 항목 | 프로젝트 기준 |
| --- | --- |
| DB Pool 기준 | 해당없음. Python/FastAPI hello API는 DB를 사용하지 않는다. |
| Lombok 기준 | 해당없음. Java/Spring을 사용하지 않는다. |

## 6. 주석 컨벤션

- 코드가 그대로 설명하는 내용은 주석으로 반복하지 않는다.
- public service/route에는 docstring 또는 짧은 주석으로 `REQ/AC/PGM/API`를 남길 수 있다.
- 보안 판단이나 예외 처리에는 `SEC-ID`를 남길 수 있다.
- 임시 TODO는 관련 `ISSUE` 또는 Run ID와 함께 남긴다.

추적 ID 표기 예:

```text
REQ: REQ-001-01
PGM: PGM-001
API: API-001
SEC: SEC-001
TEST: UT-001 / IT-001
```

## 7. 로깅 컨벤션

| 항목 | 규칙 |
| --- | --- |
| 로깅 API | Python 표준 `logging` 또는 Uvicorn/FastAPI 기본 로깅 |
| 금지 API | 운영/검증 코드에서 불필요한 `print` 남용 금지 |
| 로그 레벨 | 정상 시작/요청은 INFO, 내부 오류는 ERROR, 디버그는 로컬 개발에 한정 |
| 민감정보 | 비밀번호, 토큰, 인증 헤더, secret, 환경변수 로그 출력 금지 |
| 예외 로그 | 사용자 응답과 내부 원인을 분리하고 응답에 stack trace를 포함하지 않음 |

## 8. API 및 오류 응답 규칙

성공 응답 표준:

```text
hello
```

| 항목 | 기준 |
| --- | --- |
| HTTP Status | 200 |
| Content-Type | `text/plain; charset=utf-8` |
| Body | `hello` |

오류 응답 기준:

| 오류 코드 | 의미 | HTTP 상태 | 관련 보안 기준 |
| --- | --- | ---: | --- |
| INTERNAL_ERROR | 예상하지 못한 서버 오류 | 500 | SEC-001 |

## 9. 메시지 관리 규칙

이번 범위의 정상 응답 `hello`는 요구사항의 핵심 응답 값이므로 상수 또는 service 반환값으로 관리할 수 있다. 사용자 오류 메시지는 이번 범위에 없으며, 오류 응답이 추가되면 메시지 상수 또는 리소스로 분리한다.

## 10. DB 접근 및 데이터 표준 규칙

DB 접근은 이번 범위에서 금지한다. 저장 데이터, Entity, Repository, migration을 구현하지 않는다.

## 11. 보안 구현 규칙

| 보안 영역 | 구현 규칙 | 참조 기준 | 검증 테스트 |
| --- | --- | --- | --- |
| 입력값 검증 | 요청 본문/path/query가 없으므로 해당없음 | SEC-001 | IT-001 후보 |
| 인증 | 해당없음 | SEC-001 | 리뷰 |
| 권한 | 해당없음 | SEC-001 | 리뷰 |
| 비밀번호/암호 | 해당없음 | SEC-001 | 리뷰 |
| 중요정보 전송 | 중요정보 없음 | SEC-001 | 리뷰 |
| 예외처리 | 내부 stack trace와 환경정보를 응답에 노출하지 않음 | KISA-SD-2021 SR3-1 / SEC-001 | IT-002 후보 |
| 세션통제 | 해당없음 | SEC-001 | 리뷰 |

## 12. 테스트 컨벤션

| 항목 | 규칙 |
| --- | --- |
| 테스트 파일명 | `backend/tests/test_hello_service.py`, `backend/tests/test_hello_api.py` |
| 테스트 함수명 | `test_UT_001_hello_service_returns_hello`, `test_IT_001_get_hello_returns_200_and_hello` 후보 |
| 단위테스트 기준 | Service public contract 검증 |
| 통합테스트 기준 | FastAPI TestClient 또는 로컬 서버 HTTP 호출 검증 |
| 성능테스트 기준 | 해당없음 |
| 테스트 데이터 | 없음 |
| 테스트 증적 | Gate 4에서 QA-CMD 로그와 Test Result에 기록 |

## 13. 빌드, 실행, 테스트 명령

| 목적 | 실행 위치(cwd) | Windows 명령 | POSIX 명령 | 필수 여부 | 실행 시점 | 성공 기준 | 결과 기록 위치 | 로그/증적 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 의존성 설치 | `backend/` | `python -m pip install -r requirements.txt` | `python -m pip install -r requirements.txt` | 필수 | Impl/QA 환경 준비 | exit code 0 | Run | QA-CMD 후보 | requirements 방식 기준 |
| 개발 서버 실행 | `backend/` | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | 동일 | 선택 | 수동/API 호출 검증 | 서버 기동 성공 | Run/Test Result | 서버 로그 | Gate 4 QA-000 후보 |
| 단위/통합 테스트 | `backend/` | `python -m pytest` | `python -m pytest` | 필수 | Build Wave 완료, Gate 4 | exit code 0, 실패 0건 | Run/Test Result | QA-CMD 후보 | Gate 3에서 UT/IT 확정 |
| 정적 검사 | `backend/` | `python -m ruff check .` | `python -m ruff check .` | 선택 | Build Wave 완료, Gate 4 | exit code 0 | Run | QA-CMD 후보 | ruff 미설치 시 Not Run 사유 기록 |
| API 명령 검증 | repository root 또는 `backend/` | `Invoke-WebRequest http://127.0.0.1:8000/hello` | `curl -i http://127.0.0.1:8000/hello` | 필수 | Gate 4 | status 200, body `hello` | Test Result | QA-CMD 후보 | 서버 실행 필요 |

명령 실행 기록 기준:

- 실행한 필수 명령은 cwd, 실제 명령, OS, exit code, 결과, 로그/증적 경로를 기록한다.
- `Pass`는 exit code와 성공 기준이 모두 충족될 때만 기록한다.
- 실행하지 못한 필수 명령은 `Not Run`으로 기록하고 사유와 후속 조치를 남긴다.

## 14. 에이전트 작업 규칙

1. 구현 worker는 Program Design의 `PGM-001`, `IF-001`, `MTH-001~002`, `SKEL-001`을 먼저 확인한다.
2. 문서에 없는 JSON 응답, DB, UI, 인증 기능을 추가하지 않는다.
3. 구현 파일과 테스트에는 관련 `REQ/API/PGM/SEC/UT/IT` ID를 주석 또는 docstring으로 남길 수 있다.
4. worker self-check는 `python -m pytest`를 우선 실행하고 결과를 Run에 남긴다.
5. Orchestrator가 최종 추적표와 Gate 4 테스트결과서 반영을 재검증한다.

## 15. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | Gate 2 Python/FastAPI 개발표준 작성 | Codex Orchestrator | Orchestrator | 사용자 |
