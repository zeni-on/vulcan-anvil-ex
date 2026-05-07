# DB명세서

```yaml
---
document_id: DOC-DATA-G2-002
title: Database Specification
title_ko: DB명세서
project: Board With Login Sample
gate: G2
status: Draft
version: v0.2
owner_role: Data Architect
author: Codex
reviewer: Technical Architect
approver: Approver
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - DB-001
  - DB-002
change_reason: RUN-002 데이터 표준 검토 결과 반영
---
```

## 1. 문서 목적

본 문서는 로그인 게시판 샘플의 사용자와 게시글 데이터 구조를 정의한다.

DB명세서는 프로젝트 단어사전의 `TERM`, `DOMAIN`을 기준으로 작성하며, 프로그램명세서와 테스트케이스가 참조하는 데이터 기준이 된다.

## 2. 데이터 객체 목록

| DB-ID | 논리명 | 물리명 | 유형 | 관련 REQ | 관련 FUNC | 관련 PGM | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DB-001 | 사용자 | users | Table | REQ-001, REQ-002 | FUNC-001, FUNC-002 | PGM-001, PGM-002 | Draft |
| DB-002 | 게시글 | posts | Table | REQ-003, REQ-004, REQ-005, REQ-006 | FUNC-003, FUNC-004, FUNC-005, FUNC-006 | PGM-003, PGM-004, PGM-005, PGM-006 | Draft |

## 3. 테이블 상세

### DB-001 사용자

| 항목 | 내용 |
| --- | --- |
| DB-ID | DB-001 |
| 논리명 | 사용자 |
| 물리명 | users |
| 설명 | 로그인 게시판의 사용자 계정 정보 |
| 관련 요구사항 | REQ-001, REQ-002 |
| 관련 기능 | FUNC-001, FUNC-002 |
| 관련 프로그램 | PGM-001, PGM-002 |
| 보안 분류 | 식별정보 및 인증정보 포함 |
| 관련 보안항목 | SEC-001, SEC-004 |

#### 3.1.1 컬럼 정의

| 순번 | TERM-ID | 논리명 | 물리명 | 도메인 | 데이터 타입 | 길이 | PK | FK | NN | 기본값 | 보안 분류 | 관련 SEC | 설명 |
| ---: | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | TERM-001 | 사용자ID | id | DOMAIN-006 | INTEGER |  | Y | N | Y |  | 식별정보 | SEC-004 | 사용자 내부 식별자 |
| 2 | TERM-002 | 이메일주소 | email | DOMAIN-001 | VARCHAR | 254 | N | N | Y |  | 식별정보 | SEC-004 | 로그인 식별자, Unique |
| 3 | TERM-003 | 사용자암호화비밀번호 | password_hash | DOMAIN-005 | VARCHAR | 255 | N | N | Y |  | 인증정보 | SEC-001 | 원문 비밀번호 저장 금지 |
| 4 | TERM-004 | 사용자명 | user_nm | DOMAIN-002 | VARCHAR | 100 | N | N | Y |  | 개인정보 |  | 화면 표시명 |
| 5 | TERM-009 | 작성일시 | created_at | DOMAIN-004 | DATETIME |  | N | N | Y | CURRENT_TIMESTAMP | 일반 |  | 계정 생성 시각 |
| 6 | TERM-010 | 수정일시 | updated_at | DOMAIN-004 | DATETIME |  | N | N | Y | CURRENT_TIMESTAMP | 일반 |  | 계정 수정 시각 |

#### 3.1.2 키 및 제약조건

| 구분 | 이름 | 대상 컬럼 | 설명 | 비고 |
| --- | --- | --- | --- | --- |
| PK | pk_users | id | 사용자 기본키 |  |
| UK | uk_users_email | email | 이메일 중복 가입 방지 | AC-002 |
| CHECK | ck_users_email_not_empty | email | 이메일 필수값 | NREQ-003 |
| CHECK | ck_users_name_not_empty | user_nm | 사용자명 필수값 | NREQ-003 |

#### 3.1.3 데이터 보안

| 컬럼 | 보안 분류 | 저장 보호 | 전송 보호 | 로그 출력 | 참조 표준 | 관련 SEC | 검증 방향 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| email | 식별정보 | DB 접근통제 | HTTPS | 마스킹 권장 | KISA-SD-2021 SR1-9 | SEC-004 | UT-002 |
| password_hash | 인증정보 | 해시+솔트 저장 | HTTPS | 출력 금지 | KISA-SD-2021 SR2-3, SR2-6, SR2-7 | SEC-001 | UT-001, UT-003 |
| user_nm | 개인정보 | DB 접근통제 | HTTPS | 필요 최소 출력 |  |  | 리뷰 |

### DB-002 게시글

| 항목 | 내용 |
| --- | --- |
| DB-ID | DB-002 |
| 논리명 | 게시글 |
| 물리명 | posts |
| 설명 | 사용자가 작성한 게시글 정보 |
| 관련 요구사항 | REQ-003, REQ-004, REQ-005, REQ-006 |
| 관련 기능 | FUNC-003, FUNC-004, FUNC-005, FUNC-006 |
| 관련 프로그램 | PGM-003, PGM-004, PGM-005, PGM-006 |
| 보안 분류 | 식별정보 연결 |
| 관련 보안항목 | SEC-002, SEC-003, SEC-004 |

#### 3.2.1 컬럼 정의

| 순번 | TERM-ID | 논리명 | 물리명 | 도메인 | 데이터 타입 | 길이 | PK | FK | NN | 기본값 | 보안 분류 | 관련 SEC | 설명 |
| ---: | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | TERM-005 | 게시물ID | id | DOMAIN-006 | INTEGER |  | Y | N | Y |  | 일반 |  | 게시물 내부 식별자 |
| 2 | TERM-006 | 게시물제목 | post_ttl | DOMAIN-007 | VARCHAR | 200 | N | N | Y |  | 일반 | SEC-004 | 제목 입력값 검증 |
| 3 | TERM-007 | 게시물내용 | post_cn | DOMAIN-003 | TEXT |  | N | N | Y |  | 일반 | SEC-004 | 본문 입력값 검증 및 XSS 방지 |
| 4 | TERM-008 | 작성자아이디 | author_id | DOMAIN-006 | INTEGER |  | N | Y | Y |  | 식별정보 | SEC-003 | users.id 참조 |
| 5 | TERM-009 | 작성일시 | created_at | DOMAIN-004 | DATETIME |  | N | N | Y | CURRENT_TIMESTAMP | 일반 |  | 게시글 생성 시각 |
| 6 | TERM-010 | 수정일시 | updated_at | DOMAIN-004 | DATETIME |  | N | N | Y | CURRENT_TIMESTAMP | 일반 |  | 게시글 수정 시각 |

#### 3.2.2 키 및 제약조건

| 구분 | 이름 | 대상 컬럼 | 설명 | 비고 |
| --- | --- | --- | --- | --- |
| PK | pk_posts | id | 게시글 기본키 |  |
| FK | fk_posts_author | author_id | 작성자 사용자 참조 | SEC-003 |
| CHECK | ck_posts_title_not_empty | post_ttl | 제목 필수값 | AC-007 |
| CHECK | ck_posts_content_not_empty | post_cn | 본문 필수값 | AC-007 |

#### 3.2.3 인덱스

| 인덱스명 | 컬럼 | 유형 | 목적 | 관련 NREQ/PT |
| --- | --- | --- | --- | --- |
| ix_posts_created_at | created_at | Normal | 최신순 목록 조회 | NREQ-002, PT-001 |
| ix_posts_author_id | author_id | Normal | 작성자 권한 확인 및 사용자별 조회 | SEC-003 |

#### 3.2.4 데이터 보안

| 컬럼 | 보안 분류 | 저장 보호 | 전송 보호 | 로그 출력 | 참조 표준 | 관련 SEC | 검증 방향 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| post_ttl | 일반 | 입력값 검증 | HTTPS | 가능 | KISA-SD-2021 SR1-5 | SEC-004 | UT-007 |
| post_cn | 일반 | 입력값 검증/XSS 방지 | HTTPS | 필요 최소 출력 | KISA-SD-2021 SR1-5 | SEC-004 | UT-007 |
| author_id | 식별정보 | 접근통제 | HTTPS | 필요 최소 출력 | KISA-SD-2021 SR2-4 | SEC-003 | UT-009, UT-010, UT-011 |

## 4. 테이블 관계

| 출발 DB-ID | 관계 | 대상 DB-ID | 관계 설명 | 비고 |
| --- | --- | --- | --- | --- |
| DB-001 | 1:N | DB-002 | 한 사용자는 여러 게시글을 작성할 수 있다 | posts.author_id -> users.id |

## 5. 데이터 표준 검토

| TERM-ID | 논리명 | 공공데이터 표준 용어 | 영문 약어 | 도메인 | 표준 준용 상태 | 등록/변형 사유 |
| --- | --- | --- | --- | --- | --- | --- |
| TERM-002 | 이메일주소 | 이메일주소 계열 용어 | EML_ADDR | 주소V320 / DOMAIN-001 | 준용 | 물리 컬럼 email은 구현 관례로 유지 |
| TERM-003 | 사용자암호화비밀번호 | 사용자암호화비밀번호 | USER_ENPSWD | 암호화번호V256 / DOMAIN-005 | 준용 | 구현 컬럼 password_hash는 해시 저장 의미를 명확히 하기 위해 유지 |
| TERM-004 | 사용자명 | 사용자명 | USER_NM | 명V100 / DOMAIN-002 | 준용 | 공통표준 용어와 약어 일치 |
| TERM-006 | 게시물제목 | 게시물제목 | PST_TTL | 명V256 / DOMAIN-007 | 변형 | 구현 컬럼 post_ttl은 표준 약어를 따르되 샘플 구현은 200자 제한 |
| TERM-007 | 게시물내용 | 게시물내용 | PST_CN | 내용V4000 / DOMAIN-003 | 준용 | 구현 컬럼 post_cn은 표준 약어 기반 |
| TERM-008 | 작성자아이디 | 사용자아이디/작성자명 대조 | WRTR_ID | DOMAIN-006 | 프로젝트신규 | FK 컬럼 성격상 작성자명 대신 내부 ID를 저장하므로 프로젝트 용어로 등록 |
| TERM-009 | 작성일시 | 작성일시 | WRT_DT | 연월일시분초D / DOMAIN-004 | 준용 | 구현 컬럼 created_at은 개발 표준 네이밍으로 유지 |
| TERM-010 | 수정일시 | 수정일시 | MDFCN_DT | 연월일시분초D / DOMAIN-004 | 준용 | 구현 컬럼 updated_at은 개발 표준 네이밍으로 유지 |

## 6. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 DB명세 최초 작성 | Codex |  |  |
| v0.2 | 2026-05-07 | RUN-002 기준 공공데이터 공통표준 대조 결과 반영 | Codex |  |  |
