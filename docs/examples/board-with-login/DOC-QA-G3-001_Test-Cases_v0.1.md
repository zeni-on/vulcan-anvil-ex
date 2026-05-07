# 테스트케이스 정의서

```yaml
---
document_id: DOC-QA-G3-001
title: Test Case Specification
title_ko: 테스트케이스 정의서
project: Board With Login Sample
gate: G3
status: Draft
version: v0.1
owner_role: Test Designer
author: Codex
reviewer: QA Reviewer
approver: Approver
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - UT-001
  - IT-001
change_reason: 로그인 게시판 샘플 최초 초안 작성
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플의 요구사항, 인수기준, 보안항목, 비기능 요구사항을 검증하기 위한 테스트 케이스를 정의한다.

## 2. 테스트 케이스 목록

| 테스트 ID | 유형 | 테스트명 | 대상 | 관련 REQ | 관련 AC | 관련 SEC/SR | 우선순위 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UT-001 | Unit | 정상 회원가입 | PGM-001 | REQ-001 | AC-001 | SEC-001 / SR2-3, SR2-6, SR2-7 | Must | Draft |
| UT-002 | Unit | 중복 이메일 차단 | PGM-001 | REQ-001 | AC-002 | SEC-004 / SR1-1 | Must | Draft |
| UT-003 | Unit | 정상 로그인 | PGM-002 | REQ-002 | AC-003 | SEC-001 / SR2-3, SR2-8 | Must | Draft |
| UT-004 | Unit | 잘못된 비밀번호 로그인 실패 | PGM-002 | REQ-002 | AC-004 | SR3-1 | Must | Draft |
| UT-005 | Unit | 게시글 목록 최신순 정렬 | PGM-003 | REQ-003 | AC-005 |  | Must | Draft |
| UT-006 | Unit | 게시글 상세 필드 확인 | PGM-004 | REQ-004 | AC-006 |  | Must | Draft |
| UT-007 | Unit | 로그인 사용자 게시글 작성 성공 | PGM-005 | REQ-005 | AC-007 | SEC-002, SEC-004 / SR1-5, SR2-4 | Must | Draft |
| UT-008 | Unit | 비로그인 게시글 작성 차단 | PGM-005 | REQ-005 | AC-008 | SEC-002 / SR2-1 | Must | Draft |
| UT-009 | Unit | 본인 글 수정 성공 | PGM-006 | REQ-006 | AC-009 | SEC-003 / SR2-4 | Must | Draft |
| UT-010 | Unit | 본인 글 삭제 성공 | PGM-006 | REQ-006 | AC-010 | SEC-003 / SR2-4 | Must | Draft |
| UT-011 | Unit | 타인 글 수정/삭제 차단 | PGM-006 | REQ-006 | AC-011 | SEC-003 / SR1-9, SR2-4 | Must | Draft |
| IT-001 | Integration | 회원가입 후 로그인 가능 | SCR-001, SCR-002, PGM-001, PGM-002 | REQ-001, REQ-002 | AC-001, AC-003 | SEC-001 | Must | Draft |
| IT-002 | Integration | 로그인 후 인증 필요 기능 접근 | SCR-002, SCR-005, PGM-002, PGM-005 | REQ-002, REQ-005 | AC-003, AC-007 | SEC-002 | Must | Draft |
| IT-003 | Integration | 목록에서 상세 조회 | SCR-003, SCR-004, PGM-003, PGM-004 | REQ-003, REQ-004 | AC-005, AC-006 |  | Must | Draft |
| IT-004 | Integration | 로그인 후 게시글 작성 | SCR-002, SCR-005, PGM-002, PGM-005 | REQ-005 | AC-007, AC-008 | SEC-002, SEC-004 | Must | Draft |
| IT-005 | Integration | 작성자 권한 검증 흐름 | SCR-004, SCR-006, PGM-006 | REQ-006 | AC-009, AC-010, AC-011 | SEC-003 | Must | Draft |
| PT-001 | Performance | 게시글 목록 조회 응답시간 | PGM-003, SCR-003 | REQ-003 | AC-005 |  | Should | Draft |
| UI-001 | UI | 회원가입 화면 렌더링 | SCR-001 | REQ-001 | AC-001, AC-002 | SEC-001, SEC-004 | Must | Draft |
| UI-002 | UI | 로그인 화면 렌더링 | SCR-002 | REQ-002 | AC-003, AC-004 | SEC-001 | Must | Draft |
| UI-003 | UI | 게시글 목록 화면 렌더링 | SCR-003 | REQ-003 | AC-005 |  | Must | Draft |
| UI-004 | UI | 게시글 상세 화면 렌더링 | SCR-004 | REQ-004, REQ-006 | AC-006, AC-010, AC-011 | SEC-003 | Must | Draft |
| UI-005 | UI | 게시글 작성 화면 렌더링 | SCR-005 | REQ-005 | AC-007, AC-008 | SEC-002, SEC-004 | Must | Draft |
| UI-006 | UI | 게시글 수정 화면 렌더링 | SCR-006 | REQ-006 | AC-009 | SEC-003 | Must | Draft |

## 3. 대표 테스트 상세

### UT-001 정상 회원가입

| 항목 | 내용 |
| --- | --- |
| 테스트 ID | UT-001 |
| 테스트 유형 | Unit |
| 테스트명 | 정상 회원가입 |
| 테스트 목적 | 정상 입력 시 사용자 계정이 생성되고 비밀번호 원문이 저장되지 않는지 검증한다 |
| 테스트 대상 | PGM-001 |
| 관련 요구사항 | REQ-001 |
| 관련 인수기준 | AC-001 |
| 관련 보안항목 | SEC-001 |
| 참조 표준 | KISA-SD-2021 SR2-3, SR2-6, SR2-7 |

#### 테스트 데이터

| TERM-ID | 항목명 | 값 | 설명 | 보안 분류 |
| --- | --- | --- | --- | --- |
| TERM-002 | 이메일 | user@example.com | 신규 이메일 | 식별정보 |
| TERM-003 | 비밀번호 | Password!123 | 원문 입력값 | 인증정보 |
| TERM-004 | 사용자명 | 홍길동 | 표시명 | 개인정보 |

#### 테스트 절차

| 순서 | 수행 내용 | 기대 결과 |
| ---: | --- | --- |
| 1 | 회원가입 API에 정상 입력값을 전달한다 | 성공 응답을 반환한다 |
| 2 | users 저장값을 확인한다 | email, user_nm이 저장된다 |
| 3 | password_hash를 확인한다 | 원문 비밀번호와 다르고 해시값이 저장된다 |

#### 판정 기준

| 판정 | 기준 |
| --- | --- |
| PASS | 계정이 생성되고 비밀번호 원문이 저장되지 않는다 |
| FAIL | 계정 생성 실패 또는 비밀번호 원문 저장 |

### UT-011 타인 글 수정/삭제 차단

| 항목 | 내용 |
| --- | --- |
| 테스트 ID | UT-011 |
| 테스트 유형 | Unit |
| 테스트명 | 타인 글 수정/삭제 차단 |
| 테스트 목적 | 게시글 작성자가 아닌 사용자의 수정/삭제 요청을 차단하는지 검증한다 |
| 테스트 대상 | PGM-006 |
| 관련 요구사항 | REQ-006 |
| 관련 인수기준 | AC-011 |
| 관련 보안항목 | SEC-003 |
| 참조 표준 | KISA-SD-2021 SR1-9, SR2-4 |

| 순서 | 수행 내용 | 기대 결과 |
| ---: | --- | --- |
| 1 | 사용자 A가 게시글을 작성한다 | 게시글 작성자가 A로 저장된다 |
| 2 | 사용자 B가 해당 게시글 수정을 요청한다 | 403 권한 오류를 반환한다 |
| 3 | 사용자 B가 해당 게시글 삭제를 요청한다 | 403 권한 오류를 반환한다 |

## 4. 성능 테스트 기준

| PT-ID | 관련 NREQ | 대상 | 지표 | 기준값 | 측정 방법 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| PT-001 | NREQ-002 | PGM-003, SCR-003 | 응답시간 | 샘플 환경 2초 이내 | 게시글 100건 기준 목록 조회 시간 측정 | Draft |

## 5. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 테스트케이스 최초 작성 | Codex |  |  |
