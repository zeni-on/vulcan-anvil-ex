# 화면 테스트 결과서

```yaml
---
document_id: DOC-QA-G4-003
title: UI Test Result
title_ko: 화면 테스트 결과서
project: Board With Login Sample
gate: G4
status: Draft
version: v0.1
owner_role: QA Reviewer
author: Codex
reviewer: UX/UI Designer
approver: Approver
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - SCR-001
  - UI-001
change_reason: 로그인 게시판 샘플 화면 구현 및 캡처 증적 최초 작성
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플의 화면 구현 결과와 브라우저 캡처 증적을 정리한다.

화면 테스트는 화면설계서(`DOC-CORE-G2-003`)의 `SCR` 항목이 실제 화면으로 구현되었는지, 그리고 요구사항추적표(`DOC-CORE-G4-001`)에서 화면 증적까지 추적 가능한지 확인하기 위해 수행한다.

## 2. 테스트 환경

| 항목 | 내용 |
| --- | --- |
| 실행일 | 2026-05-07 |
| 실행 위치 | `docs/examples/board-with-login/sample-app` |
| 서버 | FastAPI / Uvicorn |
| 브라우저 | Codex in-app browser |
| 뷰포트 | Desktop 캡처 |
| 테스트 데이터 | `ui-final-*.example.com`, `UI evidence final post` |

## 3. 실행 결과

| 검증 항목 | 명령/방식 | 결과 | 비고 |
| --- | --- | --- | --- |
| 자동 테스트 | `python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-*` | Pass, 20 passed in 8.10s | API, 단위, 통합, 성능, UI 라우트 |
| 코드 규칙 | `python -m ruff check .` | Pass | 개발표준 적용 확인 |
| 브라우저 렌더링 | in-app browser 화면 캡처 | Pass | 콘솔 오류 없음 |

## 4. 화면별 증적

| UI-ID | SCR-ID | 화면명 | 검증 내용 | 증적 | 결과 |
| --- | --- | --- | --- | --- | --- |
| UI-001 | SCR-001 | 회원가입 | 화면 렌더링, 입력 폼 표시 | `evidence/ui/SCR-001_signup/desktop.png` | Pass |
| UI-002 | SCR-002 | 로그인 | 화면 렌더링, 입력 폼 표시 | `evidence/ui/SCR-002_login/desktop.png` | Pass |
| UI-003 | SCR-003 | 게시글 목록 | 로그인 상태 메뉴, 글쓰기 버튼, 최신 게시글 표시 | `evidence/ui/SCR-003_posts/desktop.png` | Pass |
| UI-004 | SCR-004 | 게시글 상세 | 제목, 본문, 작성자, 작성자 권한 버튼 표시 | `evidence/ui/SCR-004_detail/desktop.png` | Pass |
| UI-005 | SCR-005 | 게시글 작성 | 인증 사용자 작성 폼 표시 | `evidence/ui/SCR-005_new-post/desktop.png` | Pass |
| UI-006 | SCR-006 | 게시글 수정 | 작성자 수정 폼 표시 | `evidence/ui/SCR-006_edit-post/desktop.png` | Pass |

## 5. 발견 및 조치

| 이슈 ID | 내용 | 조치 | 상태 |
| --- | --- | --- | --- |
| ISSUE-002 | 화면 구현/캡처 증적이 추적표에 연결되지 않음 | 정적 UI 구현, UI 라우트 테스트 추가, 화면 캡처 저장, `DOC-QA-G4-003` 작성 | Closed |
| ISSUE-005 | CSS가 `hidden` 속성을 덮어 로그인 상태 메뉴가 함께 노출됨 | `[hidden] { display: none !important; }` 규칙 추가 | Closed |

## 6. 판정

로그인 게시판 샘플의 화면 구현은 `SCR-001`부터 `SCR-006`까지 렌더링 및 캡처 증적이 확보되었으므로 Gate 4 화면 검증 기준을 충족한 것으로 본다.

다만 모바일/반응형 캡처는 별도 뷰포트 기준이 정해진 후 `UI-007` 이후 항목으로 분리해 추가 검증한다.

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 화면 테스트 결과 및 캡처 증적 최초 작성 | Codex |  |  |
