# 테스트 결과서

```yaml
---
document_id: DOC-QA-G4-002
title: Test Result
title_ko: 테스트 결과서
project: Board With Login Sample
gate: G4
status: Draft
version: v0.1
owner_role: QA Reviewer
author: Codex
reviewer: Documentation Curator
approver: Approver
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - UT-001
  - UT-011
  - IT-001
  - IT-005
  - PT-001
change_reason: 로그인 게시판 샘플 앱 구현 후 테스트 실행 결과 기록
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플 앱의 구현 결과가 요구사항, 인수기준, 보안항목, 테스트케이스와 연결되어 검증되었는지 기록한다.

## 2. 실행 환경

| 항목 | 내용 |
| --- | --- |
| 앱 위치 | `docs/examples/board-with-login/sample-app` |
| 실행 런타임 | Codex bundled Python 3.12.13 |
| 주요 라이브러리 | FastAPI, SQLAlchemy, bcrypt, pytest |
| DB | 테스트 실행 시 SQLite in-memory DB |

## 3. 실행 명령

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-0youe_bo --ignore pytest-cache-files-3qbe63bz --ignore pytest-cache-files-b5l6_sjy --ignore pytest-cache-files-srgio6u0
python -m ruff check .
```

비고:

- 기본 `python`/`py` 실행기는 WindowsApps 접근 문제로 사용할 수 없어 Codex bundled Python 경로로 실행했다.
- 이전 실패 실행에서 생성된 `pytest-cache-files-*` 임시 디렉터리는 권한 문제로 삭제되지 않았으나 `.gitignore`로 제외했다.

## 4. 결과 요약

| 검증 항목 | 결과 | 비고 |
| --- | --- | --- |
| 단위 테스트 | Passed | `UT-001` ~ `UT-011` |
| 통합 테스트 | Passed | `IT-001` ~ `IT-005` |
| 성능 테스트 | Passed | `PT-001` |
| UI 라우트 테스트 | Passed | `UI-001` ~ `UI-007` |
| 정적 검사 | Passed | `ruff check .` |

테스트 실행 결과:

```text
20 passed in 8.10s
All checks passed!
```

## 5. 테스트케이스별 결과

| Test ID | 검증 내용 | 결과 | 관련 REQ/AC/SEC |
| --- | --- | --- | --- |
| UT-001 | 정상 회원가입 및 비밀번호 해시 저장 | Passed | REQ-001, AC-001, SEC-001 |
| UT-002 | 중복 이메일 차단 | Passed | REQ-001, AC-002, SEC-004 |
| UT-003 | 정상 로그인 | Passed | REQ-002, AC-003, SEC-001 |
| UT-004 | 로그인 실패 | Passed | REQ-002, AC-004 |
| UT-005 | 게시글 목록 최신순 정렬 | Passed | REQ-003, AC-005 |
| UT-006 | 게시글 상세 필드 확인 | Passed | REQ-004, AC-006 |
| UT-007 | 인증 사용자 게시글 작성 | Passed | REQ-005, AC-007, SEC-002 |
| UT-008 | 비로그인 게시글 작성 차단 | Passed | REQ-005, AC-008, SEC-002 |
| UT-009 | 작성자 게시글 수정 | Passed | REQ-006, AC-009, SEC-003 |
| UT-010 | 작성자 게시글 삭제 | Passed | REQ-006, AC-010, SEC-003 |
| UT-011 | 타인 글 수정/삭제 차단 | Passed | REQ-006, AC-011, SEC-003 |
| IT-001 | 회원가입 후 로그인 | Passed | REQ-001, REQ-002 |
| IT-002 | 인증 필요 기능 접근 제어 | Passed | REQ-002, REQ-005, SEC-002 |
| IT-003 | 목록에서 상세 조회 | Passed | REQ-003, REQ-004 |
| IT-004 | 로그인 후 게시글 작성 | Passed | REQ-005 |
| IT-005 | 작성자 권한 검증 흐름 | Passed | REQ-006, SEC-003 |
| PT-001 | 게시글 목록 응답시간 | Passed | NREQ-002 |

## 6. 발견 사항

| ISSUE ID | 내용 | 조치 |
| --- | --- | --- |
| ISSUE-005 | `passlib[bcrypt]`와 최신 `bcrypt 5.x` 조합에서 호환성 문제가 발생했다. | `bcrypt` 라이브러리를 직접 사용하도록 구현 변경 |
| ISSUE-006 | pytest 기본 임시 디렉터리와 캐시 디렉터리 접근 권한 문제가 발생했다. | 테스트 fixture에서 `tmp_path` 제거, 캐시 플러그인 비활성화 명령 사용 |

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 앱 구현 후 테스트 결과 기록 | Codex |  |  |
