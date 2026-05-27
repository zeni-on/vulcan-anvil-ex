# 테스트케이스

```yaml
---
document_id: DOC-QA-G3-001
title: Test Case Specification
title_ko: 테스트케이스 정의서
project: regression-simple-hello
gate: G3
status: Baseline Candidate
version: v0.1
owner_role: Test Designer
author: Codex Orchestrator
reviewer: QA Reviewer
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - REQ-001-01
  - NREQ-001
  - AC-001-01
  - AC-001-02
  - AC-002-01
  - SEC-001
  - UT-001
  - IT-001
  - IT-002
change_reason: Gate 3 hello API 테스트 기준 작성
---
```

## 1. 문서 목적

본 문서는 Python hello API의 요구사항, 인수기준, 보안항목, 비기능 요구사항을 검증하기 위한 테스트 케이스와 명령 기반 검증 기준을 정의한다.

## 2. 테스트 범위

| 구분 | 포함 범위 | 제외 범위 | 비고 |
| --- | --- | --- | --- |
| 단위테스트 | `HelloService.get_hello()` public contract | DB, HTTP routing | UT-001 |
| 통합테스트 | FastAPI `GET /hello` route, status/body/content-type | 인증/DB/UI | IT-001 |
| 명령 기반 검증 | 로컬 서버 실행 후 HTTP 호출 재현성 | 배포 자동화 | IT-002 |
| 성능테스트 | 해당없음 | 부하/성능 목표 없음 | PT 해당없음 |
| 보안테스트 | 민감정보 미처리, 내부 오류정보 노출 방지 리뷰/검증 | 인증/인가/암호/세션 | SEC-001 |
| 화면/UI테스트 | 해당없음 | 프론트엔드 UI 없음 | UI 해당없음 |

## 3. 테스트 케이스 목록

| 테스트 ID | 유형 | 테스트명 | 대상 | 관련 REQ | 관련 AC | 관련 SEC/SR | 우선순위 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UT-001 | Unit | hello service 반환값 검증 | PGM-001 / MTH-001 | REQ-001-01 | AC-001-02 | SEC-001 / KISA-SD-2021 SR3-1 | Must | Pass |
| IT-001 | Integration | hello API 응답 계약 검증 | API-001 / PGM-001 / MTH-002 | REQ-001-01 | AC-001-01, AC-001-02 | SEC-001 / KISA-SD-2021 SR3-1 | Must | Pass |
| IT-002 | Integration/Command | 로컬 실행 및 HTTP 호출 재현성 검증 | CNT-001 / API-001 / PGM-001 | REQ-001-01 / NREQ-001 | AC-002-01 | SEC-001 / KISA-SD-2021 SR3-1 | Must | Pass |

### 3.1 상세 REQ별 테스트 매핑

| 상세 REQ-ID | 관련 AC-ID | UT-ID | IT-ID | UI-ID | PT-ID | 검증 방식 | 상태 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001-01 | AC-001-01 | 해당없음 | IT-001, IT-002 | 해당없음 | 해당없음 | FastAPI 통합 테스트 + 명령 기반 검증 | Pass | API 성공 상태 검증 Pass |
| REQ-001-01 | AC-001-02 | UT-001 | IT-001, IT-002 | 해당없음 | 해당없음 | service 단위 테스트 + API 응답 본문 검증 | Pass | `hello` 본문 검증 Pass |
| NREQ-001 | AC-002-01 | 해당없음 | IT-002 | 해당없음 | 해당없음 | 로컬 실행/검증 명령 재현성 | Pass | 명령 기반 smoke 통과 Pass |

## 4. 테스트 케이스 상세

### UT-001 hello service 반환값 검증

| 항목 | 내용 |
| --- | --- |
| 테스트 ID | UT-001 |
| 테스트 유형 | Unit |
| 테스트명 | hello service 반환값 검증 |
| 테스트 목적 | `HelloService.get_hello()` public contract가 단순 문자열 `hello`를 반환하는지 검증한다. |
| 테스트 대상 | PGM-001 / IF-001 / MTH-001 |
| 관련 요구사항 | REQ-001-01 |
| 관련 인수기준 | AC-001-02 |
| 관련 보안항목 | SEC-001 |
| 참조 표준 | KISA-SD-2021 SR3-1 |
| 관련 비기능 요구사항 | NREQ-001 |
| 우선순위 | Must |

#### 4.1 시나리오

| 항목 | 내용 |
| --- | --- |
| Given | hello service 구현체가 준비되어 있다. |
| When | `get_hello()`를 호출한다. |
| Then | 반환값은 정확히 `hello`다. |

#### 4.2 사전 조건

| 번호 | 조건 |
| ---: | --- |
| 1 | `backend/app/services/hello_service.py`에 `get_hello() -> str` contract가 구현되어 있다. |

#### 4.3 테스트 데이터

| TERM-ID | 항목명 | 값 | 설명 | 보안 분류 |
| --- | --- | --- | --- | --- |
| TERM-001 | hello 응답 | `hello` | expected response literal | 일반 |

#### 4.4 테스트 절차

| 순서 | 수행 내용 | 기대 결과 |
| ---: | --- | --- |
| 1 | service의 `get_hello()`를 호출한다. | 반환값이 `hello`다. |
| 2 | 반환값에 개인정보, 인증정보, 추가 JSON 필드가 없는지 확인한다. | 반환값은 단순 문자열이다. |

#### 4.5 판정 기준

| 판정 | 기준 | 필수 증적 |
| --- | --- | --- |
| PASS | 테스트 함수가 통과하고 반환값이 `hello`와 일치한다. | pytest 실행 로그 |
| FAIL | 반환값 불일치, 예외 발생, 테스트 실패 중 하나 이상이 있다. | 실패 로그 |
| Not Run | 구현 또는 의존성 미준비로 실행하지 못했다. | 미실행 사유, 영향 범위, 후속 조치 |
| Skipped | 승인된 사유로 제외했다. | 승인 근거 |

#### 4.6 자동화 정보

| 항목 | 내용 |
| --- | --- |
| 테스트 파일 | `backend/tests/test_hello_service.py` |
| 테스트 함수/케이스명 | `test_UT_001_hello_service_returns_hello` |
| 실행 위치(cwd) | `backend/` |
| Windows 명령 | `python -m pytest tests/test_hello_service.py` |
| POSIX 명령 | `python -m pytest tests/test_hello_service.py` |
| 성공 기준 | exit code 0, 실패 0건 |
| 결과/증적 경로 | Gate 4 `docs/artifacts/04-review/evidence/QA-CMD-UT-001.log` 후보 |
| 실패/미실행 기록 | Fail / Not Run / Skipped 사유 |
| CI Job | 현재 없음 |

### IT-001 hello API 응답 계약 검증

| 항목 | 내용 |
| --- | --- |
| 테스트 ID | IT-001 |
| 테스트 유형 | Integration |
| 테스트명 | hello API 응답 계약 검증 |
| 테스트 목적 | `GET /hello`가 HTTP 200, `text/plain`, 본문 `hello`를 반환하는지 검증한다. |
| 테스트 대상 | API-001 / PGM-001 / MTH-002 |
| 관련 요구사항 | REQ-001-01 |
| 관련 인수기준 | AC-001-01 / AC-001-02 |
| 관련 보안항목 | SEC-001 |
| 참조 표준 | KISA-SD-2021 SR3-1 |
| 관련 비기능 요구사항 | NREQ-001 |
| 우선순위 | Must |

#### 4.7 시나리오

| 항목 | 내용 |
| --- | --- |
| Given | FastAPI app과 hello router가 준비되어 있다. |
| When | TestClient 또는 equivalent client로 `GET /hello`를 호출한다. |
| Then | 상태코드는 200이고 응답 본문은 `hello`다. |

#### 4.8 사전 조건

| 번호 | 조건 |
| ---: | --- |
| 1 | `backend/app/main.py`가 FastAPI app을 생성하고 hello router를 등록한다. |
| 2 | `backend/app/api/hello.py`가 `GET /hello` route를 제공한다. |

#### 4.9 테스트 데이터

| TERM-ID | 항목명 | 값 | 설명 | 보안 분류 |
| --- | --- | --- | --- | --- |
| TERM-001 | hello 응답 | `hello` | expected API response body | 일반 |

#### 4.10 테스트 절차

| 순서 | 수행 내용 | 기대 결과 |
| ---: | --- | --- |
| 1 | TestClient로 `GET /hello`를 호출한다. | HTTP status 200 |
| 2 | 응답 본문을 확인한다. | 본문이 `hello` |
| 3 | 응답 Content-Type을 확인한다. | `text/plain` 포함 |
| 4 | 불필요한 개인정보/인증정보/JSON 필드가 없는지 확인한다. | 응답은 단순 문자열 |

#### 4.11 판정 기준

| 판정 | 기준 | 필수 증적 |
| --- | --- | --- |
| PASS | status/body/content-type이 모두 기대값과 일치한다. | pytest 실행 로그 |
| FAIL | HTTP 상태, 본문, content-type 불일치 또는 테스트 실패 | 실패 로그 |
| Not Run | 구현 또는 의존성 미준비 | 미실행 사유 |
| Skipped | 승인된 제외 사유 | 승인 근거 |

#### 4.12 자동화 정보

| 항목 | 내용 |
| --- | --- |
| 테스트 파일 | `backend/tests/test_hello_api.py` |
| 테스트 함수/케이스명 | `test_IT_001_get_hello_returns_200_text_plain_and_hello` |
| 실행 위치(cwd) | `backend/` |
| Windows 명령 | `python -m pytest tests/test_hello_api.py` |
| POSIX 명령 | `python -m pytest tests/test_hello_api.py` |
| 성공 기준 | exit code 0, 실패 0건 |
| 결과/증적 경로 | Gate 4 `docs/artifacts/04-review/evidence/QA-CMD-IT-001.log` 후보 |
| 실패/미실행 기록 | Fail / Not Run / Skipped 사유 |
| CI Job | 현재 없음 |

### IT-002 로컬 실행 및 HTTP 호출 재현성 검증

| 항목 | 내용 |
| --- | --- |
| 테스트 ID | IT-002 |
| 테스트 유형 | Integration/Command |
| 테스트명 | 로컬 실행 및 HTTP 호출 재현성 검증 |
| 테스트 목적 | 개발표준의 명령으로 로컬 서버를 실행하고 HTTP 명령으로 `hello` 응답을 재현할 수 있는지 검증한다. |
| 테스트 대상 | CNT-001 / API-001 / PGM-001 |
| 관련 요구사항 | REQ-001-01 |
| 관련 인수기준 | AC-001-01 / AC-001-02 / AC-002-01 |
| 관련 보안항목 | SEC-001 |
| 참조 표준 | KISA-SD-2021 SR3-1 |
| 관련 비기능 요구사항 | NREQ-001 |
| 우선순위 | Must |

#### 4.13 시나리오

| 항목 | 내용 |
| --- | --- |
| Given | 의존성이 설치되어 있고 `backend/`에서 FastAPI app을 실행할 수 있다. |
| When | Uvicorn으로 서버를 실행한 뒤 HTTP 명령으로 `/hello`를 호출한다. |
| Then | HTTP 상태는 200이고 본문은 `hello`다. |

#### 4.14 사전 조건

| 번호 | 조건 |
| ---: | --- |
| 1 | `backend/requirements.txt` 또는 동등한 의존성 파일이 존재한다. |
| 2 | `python -m pip install -r requirements.txt`가 성공한다. |
| 3 | `127.0.0.1:8000` 포트가 사용 가능하거나 대체 포트를 기록한다. |

#### 4.15 테스트 데이터

| TERM-ID | 항목명 | 값 | 설명 | 보안 분류 |
| --- | --- | --- | --- | --- |
| TERM-001 | hello 응답 | `hello` | expected command response body | 일반 |

#### 4.16 테스트 절차

| 순서 | 수행 내용 | 기대 결과 |
| ---: | --- | --- |
| 1 | `backend/`에서 의존성을 설치한다. | 설치 명령 exit code 0 |
| 2 | Uvicorn으로 app을 실행한다. | 서버가 기동하고 `/hello` 요청을 받을 수 있다. |
| 3 | Windows 또는 POSIX HTTP 명령으로 `/hello`를 호출한다. | 상태 200, 본문 `hello` |
| 4 | 로그에 민감정보나 내부 오류 상세가 없는지 확인한다. | SEC-001 위반 없음 |

#### 4.17 판정 기준

| 판정 | 기준 | 필수 증적 |
| --- | --- | --- |
| PASS | 설치, 서버 실행, HTTP 호출, 응답 검증이 모두 성공한다. | 명령 로그, 서버 로그 요약 |
| FAIL | 명령 실패, 서버 기동 실패, 응답 불일치, SEC-001 위반 중 하나 이상이 있다. | 실패 로그 |
| Not Run | 의존성/포트/환경 문제로 실행하지 못했다. | 미실행 사유, 영향 범위, 후속 조치 |
| Skipped | 승인된 제외 사유 | 승인 근거 |

#### 4.18 자동화 정보

| 항목 | 내용 |
| --- | --- |
| 테스트 파일 | 명령 기반 검증. 보조 자동화 파일은 Gate 4 QA Run에서 정할 수 있다. |
| 테스트 함수/케이스명 | `IT-002_command_get_hello_returns_hello` |
| 실행 위치(cwd) | `backend/` |
| Windows 명령 | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`; 별도 터미널에서 `Invoke-WebRequest http://127.0.0.1:8000/hello` |
| POSIX 명령 | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`; 별도 터미널에서 `curl -i http://127.0.0.1:8000/hello` |
| 성공 기준 | 서버 기동 성공, HTTP 200, 본문 `hello` |
| 결과/증적 경로 | Gate 4 `docs/artifacts/04-review/evidence/QA-CMD-IT-002.log` 후보 |
| 실패/미실행 기록 | Fail / Not Run / Skipped 사유 |
| CI Job | 현재 없음 |

## 5. 성능 테스트 기준

| PT-ID | 관련 NREQ | 대상 | 지표 | 기준값 | 측정 방법 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | NREQ-001 | PGM-001 | 해당없음 | 별도 성능 목표 없음 | 해당없음 | Skipped |

## 6. 보안 테스트 기준

| 테스트 ID | 관련 SEC | 참조 표준 | 테스트 내용 | 증적 |
| --- | --- | --- | --- | --- |
| IT-001 | SEC-001 | KISA-SD-2021 SR3-1 | 정상 응답이 `hello`만 포함하고 불필요한 정보가 없는지 확인 | pytest 로그 |
| IT-002 | SEC-001 | KISA-SD-2021 SR3-1 | 명령 실행/서버 로그에서 민감정보와 내부 오류 상세 노출이 없는지 확인 | QA-CMD 로그 |

## 7. 화면/UI 테스트 기준

| UI-ID | 관련 SCR | 기준 시안 | 관련 Contract | Viewport | 상태/시나리오 | 입력값 | 기대 화면 | 캡처 경로 | 비교 방식 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | API-only 기능 | 해당없음 | 해당없음 | 해당없음 | 명령 기반 HTTP 검증으로 대체 | Skipped |

## 8. Gate 4 증적 계획

| 증적 ID 후보 | 관련 테스트 | 경로 후보 | 내용 |
| --- | --- | --- | --- |
| QA-CMD-UT-001 | UT-001 | `docs/artifacts/04-review/evidence/QA-CMD-UT-001.log` | service 단위 테스트 실행 로그 |
| QA-CMD-IT-001 | IT-001 | `docs/artifacts/04-review/evidence/QA-CMD-IT-001.log` | FastAPI TestClient 통합 테스트 실행 로그 |
| QA-CMD-IT-002 | IT-002 | `docs/artifacts/04-review/evidence/QA-CMD-IT-002.log` | Uvicorn 서버 실행 및 HTTP 호출 로그 |

## 9. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | Gate 3 hello API 테스트 기준 작성 | Codex Orchestrator | Orchestrator | 사용자 |

## 10. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 테스트에 `UT`, `IT`, `PT` ID가 부여되었는가 | 예 - PT는 해당없음 |
| 요구사항정의서의 모든 상세 `REQ-NNN-NN`이 3.1 상세 REQ별 테스트 매핑 표에 포함되었는가 | 예 |
| 모든 테스트가 상세 `REQ-NNN-NN`, `AC-NNN-NN`, `NREQ`, `SEC`, `CR` 중 하나 이상과 연결되었는가 | 예 |
| 보안 테스트에 `SEC-ID`와 `SR-ID`가 연결되었는가 | 예 |
| 화면 테스트에 `UI-ID`, `SCR-ID`, 기준 시안, viewport, 캡처 경로가 연결되었는가 | 해당없음 |
| 기준 시안의 UI Implementation Contract가 테스트 기대결과와 비교 방식에 반영되었는가 | 해당없음 |
| 테스트 데이터가 프로젝트 단어사전과 연결되었는가 | 예 - TERM-001 |
| PASS/FAIL 판정 기준이 명확한가 | 예 |
| 자동화 가능한 테스트에 파일/명령 정보가 작성되었는가 | 예 |
| 명령 기반 테스트에 실행 위치(cwd), OS별 명령, 성공 기준, 로그/증적 경로가 작성되었는가 | 예 |
