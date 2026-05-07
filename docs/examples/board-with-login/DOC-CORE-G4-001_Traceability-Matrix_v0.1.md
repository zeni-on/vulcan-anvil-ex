# 요구사항추적표

```yaml
---
document_id: DOC-CORE-G4-001
title: Traceability Matrix
title_ko: 요구사항추적표
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
  - REQ-001
  - AC-001
change_reason: 로그인 게시판 샘플 최초 초안 작성
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플의 요구사항, 인수기준, 기능, 화면, 프로그램, DB, 보안항목, 테스트 간 연결을 추적한다.

## 2. 요구사항 추적 매트릭스

| REQ-ID | NREQ-ID | AC-ID | FUNC-ID | SCR-ID | PGM-ID | DB-ID | IF-ID | SEC-ID | 참조 표준 | UT-ID | IT-ID | PT-ID | 상태 | 증적 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | NREQ-001 | AC-001 | FUNC-001 | SCR-001 | PGM-001 | DB-001 |  | SEC-001 | KISA-SD-2021 SR2-3, SR2-6, SR2-7 | UT-001 | IT-001 |  | Verified | sample-app, DOC-QA-G4-002 | 정상 회원가입 |
| REQ-001 | NREQ-003 | AC-002 | FUNC-001 | SCR-001 | PGM-001 | DB-001 |  | SEC-004 | KISA-SD-2021 SR1-1, SR1-9 | UT-002 | IT-001 |  | Verified | sample-app, DOC-QA-G4-002 | 중복 이메일 차단 |
| REQ-002 | NREQ-001 | AC-003 | FUNC-002 | SCR-002 | PGM-002 | DB-001 |  | SEC-001 | KISA-SD-2021 SR2-1, SR2-3, SR2-8 | UT-003 | IT-002 |  | Verified | sample-app, DOC-QA-G4-002 | 정상 로그인 |
| REQ-002 | NREQ-001 | AC-004 | FUNC-002 | SCR-002 | PGM-002 | DB-001 |  | SEC-001 | KISA-SD-2021 SR2-2, SR3-1 | UT-004 | IT-002 |  | Verified | sample-app, DOC-QA-G4-002 | 로그인 실패 |
| REQ-003 | NREQ-002 | AC-005 | FUNC-003 | SCR-003 | PGM-003 | DB-002 |  |  |  | UT-005 | IT-003 | PT-001 | Verified | sample-app, DOC-QA-G4-002 | 목록 최신순 |
| REQ-004 |  | AC-006 | FUNC-004 | SCR-004 | PGM-004 | DB-002 |  |  |  | UT-006 | IT-003 |  | Verified | sample-app, DOC-QA-G4-002 | 상세 조회 |
| REQ-005 | NREQ-001 | AC-007 | FUNC-005 | SCR-005 | PGM-005 | DB-002 |  | SEC-002 | KISA-SD-2021 SR2-1, SR2-4 | UT-007 | IT-004 |  | Verified | sample-app, DOC-QA-G4-002 | 로그인 작성 |
| REQ-005 | NREQ-001 | AC-008 | FUNC-005 | SCR-005 | PGM-005 | DB-002 |  | SEC-002 | KISA-SD-2021 SR2-1, SR2-4 | UT-008 | IT-004 |  | Verified | sample-app, DOC-QA-G4-002 | 비로그인 작성 차단 |
| REQ-006 | NREQ-001 | AC-009 | FUNC-006 | SCR-006 | PGM-006 | DB-002 |  | SEC-003 | KISA-SD-2021 SR1-9, SR2-4 | UT-009 | IT-005 |  | Verified | sample-app, DOC-QA-G4-002 | 본인 글 수정 |
| REQ-006 | NREQ-001 | AC-010 | FUNC-006 | SCR-004 | PGM-006 | DB-002 |  | SEC-003 | KISA-SD-2021 SR1-9, SR2-4 | UT-010 | IT-005 |  | Verified | sample-app, DOC-QA-G4-002 | 본인 글 삭제 |
| REQ-006 | NREQ-001 | AC-011 | FUNC-006 | SCR-004 | PGM-006 | DB-002 |  | SEC-003 | KISA-SD-2021 SR1-9, SR2-4 | UT-011 | IT-005 |  | Verified | sample-app, DOC-QA-G4-002 | 타인 글 수정/삭제 차단 |

## 3. 요구사항별 검증 요약

| REQ-ID | 요구사항명 | 인수기준 수 | 설계 연결 | 테스트 연결 | 검증 상태 | 미해결 사항 |
| --- | --- | ---: | --- | --- | --- | --- |
| REQ-001 | 회원가입 | 2 | FUNC-001, SCR-001, PGM-001, DB-001 | UT-001, UT-002, IT-001 | Verified | 이메일 인증 여부 |
| REQ-002 | 로그인/로그아웃 | 2 | FUNC-002, SCR-002, PGM-002, DB-001 | UT-003, UT-004, IT-002 | Verified | 세션/토큰 방식 |
| REQ-003 | 게시글 목록 조회 | 1 | FUNC-003, SCR-003, PGM-003, DB-002 | UT-005, IT-003, PT-001 | Verified | 페이지네이션 방식 |
| REQ-004 | 게시글 상세 조회 | 1 | FUNC-004, SCR-004, PGM-004, DB-002 | UT-006, IT-003 | Verified | 삭제 글 접근 처리 |
| REQ-005 | 게시글 작성 | 2 | FUNC-005, SCR-005, PGM-005, DB-002 | UT-007, UT-008, IT-004 | Verified | 제목/본문 길이 |
| REQ-006 | 게시글 수정/삭제 | 3 | FUNC-006, SCR-004, SCR-006, PGM-006, DB-002 | UT-009, UT-010, UT-011, IT-005 | Verified | 삭제 방식 |

## 4. 보안항목 추적

| SEC-ID | 보안항목 | 관련 REQ/NREQ | 참조 표준 | 적용 대상 | 검증 테스트 | 증적 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | 비밀번호는 평문으로 저장하지 않는다 | REQ-001, REQ-002, NREQ-001 | KISA-SD-2021 SR2-3, SR2-6, SR2-7 | PGM-001, PGM-002, DB-001 | UT-001, UT-003 | DOC-QA-G4-002 | Verified |
| SEC-002 | 인증된 사용자만 게시글을 작성할 수 있다 | REQ-005, NREQ-001 | KISA-SD-2021 SR2-1, SR2-4 | SCR-005, PGM-005 | UT-007, UT-008, IT-004 | DOC-QA-G4-002 | Verified |
| SEC-003 | 작성자만 본인 게시글을 수정/삭제할 수 있다 | REQ-006, NREQ-001 | KISA-SD-2021 SR1-9, SR2-4 | SCR-004, SCR-006, PGM-006 | UT-009, UT-010, UT-011, IT-005 | DOC-QA-G4-002 | Verified |
| SEC-004 | 사용자 입력값은 서버에서 검증한다 | REQ-001, REQ-005, REQ-006, NREQ-003 | KISA-SD-2021 SR1-1, SR1-5, SR1-9 | PGM-001, PGM-005, PGM-006 | UT-002, UT-007 | DOC-QA-G4-002 | Verified |

## 5. 개발표준 추적

| 문서 ID | 표준 영역 | 관련 설계 | 관련 테스트 | 상태 | 비고 |
| --- | --- | --- | --- | --- | --- |
| DOC-DEV-G2-001 | Python/FastAPI, Router-Service-Repository, 코드/주석/테스트 컨벤션 | PGM-001~PGM-006, SCR-001~SCR-006, DB-001~DB-002 | UT-001~UT-011, IT-001~IT-005, PT-001 | Applied | 샘플 앱 구현 및 테스트에 적용 |

## 6. 화면 테스트 증적 추적

| UI-ID | SCR-ID | 관련 REQ | 관련 AC/SEC | 검증 내용 | 증적 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| UI-001 | SCR-001 | REQ-001 | AC-001, AC-002, SEC-001, SEC-004 | 회원가입 화면 렌더링 및 입력 폼 확인 | DOC-QA-G4-003, `evidence/ui/SCR-001_signup/desktop.png` | Verified |
| UI-002 | SCR-002 | REQ-002 | AC-003, AC-004, SEC-001 | 로그인 화면 렌더링 및 입력 폼 확인 | DOC-QA-G4-003, `evidence/ui/SCR-002_login/desktop.png` | Verified |
| UI-003 | SCR-003 | REQ-003 | AC-005 | 게시글 목록, 글쓰기 버튼, 최신 게시글 표시 확인 | DOC-QA-G4-003, `evidence/ui/SCR-003_posts/desktop.png` | Verified |
| UI-004 | SCR-004 | REQ-004, REQ-006 | AC-006, AC-010, AC-011, SEC-003 | 상세 조회 및 작성자 권한 버튼 확인 | DOC-QA-G4-003, `evidence/ui/SCR-004_detail/desktop.png` | Verified |
| UI-005 | SCR-005 | REQ-005 | AC-007, AC-008, SEC-002, SEC-004 | 인증 사용자 작성 화면 확인 | DOC-QA-G4-003, `evidence/ui/SCR-005_new-post/desktop.png` | Verified |
| UI-006 | SCR-006 | REQ-006 | AC-009, SEC-003 | 작성자 수정 화면 확인 | DOC-QA-G4-003, `evidence/ui/SCR-006_edit-post/desktop.png` | Verified |

## 7. 데이터 표준 추적

| DB-ID | 데이터 항목 | 관련 REQ/NREQ | 공공데이터 표준 용어 | 영문 약어 | 도메인 | 표준 준용 여부 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DB-001 | 이메일 | REQ-001, REQ-002 | 확인필요 | 확인필요 | 확인필요 | 확인필요 | 공공데이터 공통표준 확인 필요 |
| DB-001 | 비밀번호해시 | REQ-001, REQ-002, NREQ-001 | 확인필요 | 확인필요 | 확인필요 | 확인필요 | 원문 비밀번호 저장 금지 |
| DB-001 | 사용자명 | REQ-001 | 확인필요 | 확인필요 | 확인필요 | 확인필요 | 화면 표시명/DB 컬럼명 매핑 필요 |
| DB-002 | 게시글제목 | REQ-003, REQ-004, REQ-005, REQ-006 | 확인필요 | 확인필요 | 확인필요 | 확인필요 | 제목 길이 제한 필요 |
| DB-002 | 게시글내용 | REQ-004, REQ-005, REQ-006 | 확인필요 | 확인필요 | 확인필요 | 확인필요 | 본문 길이 제한 필요 |

## 8. 추적성 점검 목록

| 점검 ID | 점검 유형 | 관련 ID | 설명 | 조치 담당 | 상태 |
| --- | --- | --- | --- | --- | --- |
| ISSUE-001 | 구현 증적 미연결 | PGM-001~PGM-006 | 프로그램명세서 기준으로 `sample-app` 구현이 작성되었다. | Technical Architect | Closed |
| ISSUE-002 | 화면 증적 미연결 | SCR-001~SCR-006 | 화면 구현, UI 라우트 테스트, 브라우저 캡처, `DOC-QA-G4-003` 결과서가 연결되었다. | UX/UI Designer | Closed |
| ISSUE-003 | 테스트 실행 증적 미연결 | UT-001~UT-011, IT-001~IT-005, PT-001 | 자동화 테스트 코드와 실행 결과가 `DOC-QA-G4-002`에 연결되었다. | Test Designer | Closed |
| ISSUE-004 | 데이터 표준 검토 미완료 | DB-001, DB-002 | 공공데이터 공통표준 용어/단어/도메인 확인 및 프로젝트 신규어 승인 여부 결정이 필요하다. | Data Architect | Open |

## 9. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 추적표 최초 작성 | Codex |  |  |
