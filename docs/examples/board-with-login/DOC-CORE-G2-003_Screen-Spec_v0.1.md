# 화면설계서

```yaml
---
document_id: DOC-CORE-G2-003
title: Screen Specification
title_ko: 화면설계서
project: Board With Login Sample
gate: G2
status: Draft
version: v0.1
owner_role: UX/UI Designer
author: Codex
reviewer: Requirements Lead
approver: Approver
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - SCR-001
  - SCR-002
  - SCR-003
  - SCR-004
  - SCR-005
  - SCR-006
change_reason: 로그인 게시판 샘플 최초 초안 작성
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플의 화면 구성, 주요 입력/출력 항목, 이벤트, 권한, 보안 고려사항을 정의한다.

## 2. 화면 목록

| SCR-ID | 화면명 | 유형 | 관련 FUNC | 관련 PGM | 관련 SEC | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| SCR-001 | 회원가입 화면 | Page | FUNC-001 | PGM-001 | SEC-001, SEC-004 | Draft |
| SCR-002 | 로그인 화면 | Page | FUNC-002 | PGM-002 | SEC-001 | Draft |
| SCR-003 | 게시글 목록 화면 | Page | FUNC-003 | PGM-003 |  | Draft |
| SCR-004 | 게시글 상세 화면 | Page | FUNC-004, FUNC-006 | PGM-004, PGM-006 | SEC-003 | Draft |
| SCR-005 | 게시글 작성 화면 | Page | FUNC-005 | PGM-005 | SEC-002, SEC-004 | Draft |
| SCR-006 | 게시글 수정 화면 | Page | FUNC-006 | PGM-006 | SEC-003, SEC-004 | Draft |

## 3. 화면 상세 요약

| SCR-ID | 화면명 | 접근 권한 | 주요 입력 | 주요 이벤트 | 관련 AC |
| --- | --- | --- | --- | --- | --- |
| SCR-001 | 회원가입 화면 | 비로그인 사용자 | 이메일, 비밀번호, 이름 | 가입 요청 | AC-001, AC-002 |
| SCR-002 | 로그인 화면 | 비로그인 사용자 | 이메일, 비밀번호 | 로그인 요청 | AC-003, AC-004 |
| SCR-003 | 게시글 목록 화면 | 전체 사용자 | 페이지 번호 | 목록 조회, 상세 이동 | AC-005 |
| SCR-004 | 게시글 상세 화면 | 전체 사용자 | 게시글 ID | 상세 조회, 삭제 요청 | AC-006, AC-010, AC-011 |
| SCR-005 | 게시글 작성 화면 | 로그인 사용자 | 제목, 본문 | 저장 요청 | AC-007, AC-008 |
| SCR-006 | 게시글 수정 화면 | 작성자 | 제목, 본문 | 수정 요청 | AC-009, AC-011 |

## 4. 입력 항목 표준

| SCR-ID | TERM-ID | 화면 항목명 | API 필드명 | 필수 | 형식/도메인 | 검증 기준 | 관련 SEC/SR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SCR-001 | TERM-002 | 이메일 | email | Y | DOMAIN-001 | 이메일 형식 | SEC-004 / KISA-SD-2021 SR1-1 |
| SCR-001 | TERM-003 | 비밀번호 | password | Y | DOMAIN-005 | 비밀번호 정책 | SEC-001 / KISA-SD-2021 SR2-3 |
| SCR-001 | TERM-004 | 이름 | userName | Y | DOMAIN-002 | 필수값, 길이 제한 | SEC-004 / KISA-SD-2021 SR1-9 |
| SCR-002 | TERM-002 | 이메일 | email | Y | DOMAIN-001 | 이메일 형식 | SEC-004 / KISA-SD-2021 SR1-1 |
| SCR-002 | TERM-003 | 비밀번호 | password | Y | DOMAIN-005 | 필수값 | SEC-001 / KISA-SD-2021 SR2-8 |
| SCR-005 | TERM-006 | 제목 | title | Y | DOMAIN-002 | 필수값, 길이 제한 | SEC-004 / KISA-SD-2021 SR1-5 |
| SCR-005 | TERM-007 | 본문 | content | Y | DOMAIN-003 | 필수값, 길이 제한 | SEC-004 / KISA-SD-2021 SR1-5 |
| SCR-006 | TERM-006 | 제목 | title | Y | DOMAIN-002 | 필수값, 길이 제한 | SEC-004 / KISA-SD-2021 SR1-5 |
| SCR-006 | TERM-007 | 본문 | content | Y | DOMAIN-003 | 필수값, 길이 제한 | SEC-004 / KISA-SD-2021 SR1-5 |

## 5. 화면 이벤트

| 이벤트 ID | 화면 | 이벤트 | 발생 조건 | 호출 프로그램 | 처리 결과 | 관련 AC/SEC |
| --- | --- | --- | --- | --- | --- | --- |
| EVT-001 | SCR-001 | 가입 요청 | 가입 버튼 클릭 | PGM-001 | 계정 생성 또는 오류 표시 | AC-001, AC-002, SEC-001 |
| EVT-002 | SCR-002 | 로그인 요청 | 로그인 버튼 클릭 | PGM-002 | 인증 상태 생성 또는 오류 표시 | AC-003, AC-004 |
| EVT-003 | SCR-003 | 목록 조회 | 화면 진입 | PGM-003 | 최신순 목록 표시 | AC-005 |
| EVT-004 | SCR-004 | 상세 조회 | 게시글 선택 | PGM-004 | 상세 정보 표시 | AC-006 |
| EVT-005 | SCR-005 | 게시글 저장 | 저장 버튼 클릭 | PGM-005 | 게시글 생성 또는 오류 표시 | AC-007, AC-008, SEC-002 |
| EVT-006 | SCR-006 | 게시글 수정 | 수정 버튼 클릭 | PGM-006 | 게시글 수정 또는 오류 표시 | AC-009, AC-011, SEC-003 |
| EVT-007 | SCR-004 | 게시글 삭제 | 삭제 버튼 클릭 | PGM-006 | 게시글 삭제 또는 오류 표시 | AC-010, AC-011, SEC-003 |

## 6. 권한 및 보안

| SEC-ID | 참조 표준 | 보안 고려사항 | 화면 적용 방식 | 검증 테스트 |
| --- | --- | --- | --- | --- |
| SEC-001 | KISA-SD-2021 SR2-3, SR2-8 | 비밀번호 입력/전송 보호 | 비밀번호 입력값 마스킹, HTTPS 전송 전제 | UT-003, IT-002 |
| SEC-002 | KISA-SD-2021 SR2-1, SR2-4 | 인증 사용자만 작성 | 비로그인 접근 시 로그인 필요 메시지 | UT-008, IT-004 |
| SEC-003 | KISA-SD-2021 SR1-9, SR2-4 | 작성자만 수정/삭제 | 작성자가 아니면 수정/삭제 버튼 숨김 및 서버 검증 | UT-011, IT-005 |
| SEC-004 | KISA-SD-2021 SR1-1, SR1-5, SR1-9 | 입력값 검증 | 클라이언트 안내와 서버 검증 병행 | UT-002, UT-007 |

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 화면설계 최초 작성 | Codex |  |  |

