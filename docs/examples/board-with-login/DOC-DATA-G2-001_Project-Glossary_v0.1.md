# 프로젝트 단어사전

```yaml
---
document_id: DOC-DATA-G2-001
title: Project Glossary
title_ko: 프로젝트 단어사전
project: Board With Login Sample
gate: G2
status: Draft
version: v0.2
owner_role: Data Architect
author: Codex
reviewer: Documentation Curator
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

본 문서는 로그인 게시판 샘플에서 사용하는 주요 용어, 단어, 도메인, 화면/API/DB 항목명 매핑을 정의한다.

본 문서는 공공데이터 공통표준(2025.11월)과 대조한 결과를 반영한다. 표준에 동일하거나 직접 적용 가능한 용어가 있는 항목은 `준용`으로 표시하고, 샘플 업무 특화 항목은 `프로젝트신규`로 남기되 대조 근거와 등록 사유를 기록한다.

## 2. 참조 표준

| 참조 코드 | 문서명 | 적용 범위 |
| --- | --- | --- |
| PUBLIC-DATA-STD-2025-11 | 공공데이터 공통표준(2025.11월) | 용어, 단어, 도메인 검토 |

## 3. 프로젝트 용어 목록

| TERM-ID | 한글명 | 영문명 | 영문 약어 | 정의 | 도메인 | 출처 | 표준 준용 상태 | 등록 사유 | 관련 ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-001 | 사용자 | User | USER | 게시판 서비스를 이용하는 계정 주체 | DOMAIN-002 | 프로젝트 | 프로젝트신규 | 공통표준에는 사용자명/사용자아이디 등 파생 용어가 존재하나 계정 주체 자체는 샘플 엔티티명으로 등록 | DB-001, REQ-001, REQ-002 |
| TERM-002 | 이메일주소 | Email Address | EML_ADDR | 사용자 계정 식별과 로그인에 사용하는 이메일 주소 | DOMAIN-001 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 이메일주소 계열 용어와 주소 도메인 준용 | DB-001, REQ-001, REQ-002 |
| TERM-003 | 사용자암호화비밀번호 | Encrypted Password | USER_ENPSWD | 원문 비밀번호를 안전한 방식으로 해시한 저장 값 | DOMAIN-005 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 사용자암호화비밀번호를 준용하되 구현 컬럼은 password_hash로 유지 | DB-001, SEC-001 |
| TERM-004 | 사용자명 | User Name | USER_NM | 게시글 작성자 표시 등에 사용하는 사용자 이름 | DOMAIN-002 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 사용자명(USER_NM), 명V100 준용 | DB-001, REQ-001 |
| TERM-005 | 게시물 | Post | PST | 사용자가 게시판에 작성한 제목과 본문 콘텐츠 | DOMAIN-003 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 게시물 계열 용어를 게시판 샘플의 게시글 개념에 적용 | DB-002, REQ-003, REQ-004, REQ-005, REQ-006 |
| TERM-006 | 게시물제목 | Post Title | PST_TTL | 게시물의 제목 | DOMAIN-007 | PUBLIC-DATA-STD-2025-11 | 변형 | 공통표준 게시물제목(PST_TTL), 명V256을 확인했으나 샘플 구현은 200자 제한 | DB-002, REQ-003, REQ-004, REQ-005, REQ-006 |
| TERM-007 | 게시물내용 | Post Content | PST_CN | 게시물의 본문 내용 | DOMAIN-003 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 게시물내용(PST_CN), 내용V4000 준용 | DB-002, REQ-004, REQ-005, REQ-006 |
| TERM-008 | 작성자아이디 | Writer ID | WRTR_ID | 게시물을 작성한 사용자의 내부 식별자 | DOMAIN-006 | 프로젝트 | 프로젝트신규 | 공통표준 작성자명/사용자아이디는 존재하나 샘플 FK 컬럼은 작성자 내부 ID이므로 프로젝트 용어로 등록 | DB-002, SEC-003 |
| TERM-009 | 작성일시 | Created Date Time | WRT_DT | 데이터가 최초 작성된 일시 | DOMAIN-004 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 작성일시(WRT_DT), 연월일시분초D 준용 | DB-001, DB-002 |
| TERM-010 | 수정일시 | Updated Date Time | MDFCN_DT | 데이터가 마지막으로 수정된 일시 | DOMAIN-004 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 수정일시(MDFCN_DT), 연월일시분초D 준용 | DB-001, DB-002 |

## 4. 프로젝트 단어 목록

| WORD-ID | 한글 단어 | 영문명 | 영문 약어 | 정의 | 출처 | 표준 준용 상태 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WORD-001 | 사용자 | User | USER | 서비스를 이용하는 주체 | PUBLIC-DATA-STD-2025-11 | 준용 |  |
| WORD-002 | 이메일 | Email | EML | 이메일 주소 | PUBLIC-DATA-STD-2025-11 | 준용 | 이메일주소 계열 용어 구성 단어 |
| WORD-003 | 비밀번호 | Password | PSWD | 인증에 사용하는 비밀 문자열 | PUBLIC-DATA-STD-2025-11 | 준용 | 원문 저장 금지 |
| WORD-004 | 해시값 | Hash Value | HASH_VAL | 해시 연산 결과값 | 프로젝트 | 프로젝트신규 |  |
| WORD-005 | 게시글 | Post | POST | 게시판 콘텐츠 | 프로젝트 | 프로젝트신규 |  |
| WORD-006 | 제목 | Title | TTL | 제목 | PUBLIC-DATA-STD-2025-11 | 준용 |  |
| WORD-007 | 내용 | Content | CN | 본문 내용 | PUBLIC-DATA-STD-2025-11 | 준용 |  |
| WORD-008 | 작성자 | Writer | WRTR | 작성 주체 | PUBLIC-DATA-STD-2025-11 | 준용 | 작성자명 계열 용어 구성 단어 |
| WORD-009 | 작성일시 | Created Date Time | WRT_DT | 최초 작성 일시 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 작성일시 준용 |
| WORD-010 | 수정일시 | Modified Date Time | MDFCN_DT | 마지막 수정 일시 | PUBLIC-DATA-STD-2025-11 | 준용 | 공통표준 수정일시 준용 |

## 5. 도메인 목록

| DOMAIN-ID | 도메인명 | 데이터 타입 | 길이 | 소수점 | 저장 형식 | 표현 형식 | 출처 | 표준 준용 상태 |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| DOMAIN-001 | 이메일V254 | VARCHAR | 254 |  | 254자리 이내 문자 | 이메일 주소 | 프로젝트 | 변형 |
| DOMAIN-002 | 명V100 | VARCHAR | 100 |  | 100자리 이내 문자 | 문자열 | PUBLIC-DATA-STD-2025-11 | 준용 |
| DOMAIN-003 | 내용V4000 | VARCHAR | 4000 |  | 4000자리 이내 문자 | 문자열 | PUBLIC-DATA-STD-2025-11 | 준용 |
| DOMAIN-004 | 일시DT | DATETIME |  |  | YYYY-MM-DD HH:MM:SS | YYYY-MM-DD HH:MM:SS | PUBLIC-DATA-STD-2025-11 | 변형 |
| DOMAIN-005 | 해시값V255 | VARCHAR | 255 |  | 255자리 이내 문자 | 해시 문자열 | 프로젝트 | 프로젝트신규 |
| DOMAIN-006 | 식별자N | INTEGER |  |  | 정수 | 내부 식별자 | 프로젝트 | 프로젝트신규 |
| DOMAIN-007 | 제목V200 | VARCHAR | 200 |  | 200자리 이내 문자 | 제목 | 프로젝트 | 변형 |

## 6. 화면/API/DB 항목 매핑

| TERM-ID | 한글명 | 화면 항목명 | API 필드명 | DB 컬럼명 | 도메인 | 보안 분류 | 관련 SEC | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-002 | 이메일주소 | 이메일 | email | email | DOMAIN-001 | 식별정보 | SEC-004 | 화면 표시명은 이메일, 표준 용어는 이메일주소 |
| TERM-003 | 사용자암호화비밀번호 | 비밀번호 | password / passwordHash | password_hash | DOMAIN-005 | 인증정보 | SEC-001 | 화면/API 입력은 원문, DB 저장은 해시값 |
| TERM-004 | 사용자명 | 이름 | userName | user_nm | DOMAIN-002 | 개인정보 |  | 표시명 |
| TERM-006 | 게시물제목 | 제목 | title | post_ttl | DOMAIN-007 | 일반 | SEC-004 | 입력값 검증 필요 |
| TERM-007 | 게시물내용 | 본문 | content | post_cn | DOMAIN-003 | 일반 | SEC-004 | XSS 방지 필요 |
| TERM-008 | 작성자아이디 | 작성자 | authorId | author_id | DOMAIN-006 | 식별정보 | SEC-003 | 권한 검증 기준 |
| TERM-009 | 작성일시 | 작성일 | createdAt | created_at | DOMAIN-004 | 일반 |  |  |
| TERM-010 | 수정일시 | 수정일 | updatedAt | updated_at | DOMAIN-004 | 일반 |  |  |

## 7. 보안/개인정보 분류

| TERM-ID | 한글명 | 보안 분류 | 저장 보호 | 전송 보호 | 로그 출력 | 관련 SEC | 검증 방향 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-002 | 이메일 | 식별정보 | DB 접근통제 | HTTPS | 마스킹 권장 | SEC-004 | UT-002 |
| TERM-003 | 비밀번호해시값 | 인증정보 | 해시+솔트 저장 | HTTPS | 출력 금지 | SEC-001 | UT-001, UT-003 |
| TERM-004 | 사용자명 | 개인정보 | 접근통제 | HTTPS | 필요 최소 출력 |  | 리뷰 |
| TERM-008 | 작성자 | 식별정보 | 접근통제 | HTTPS | 필요 최소 출력 | SEC-003 | UT-009, UT-010, UT-011 |

## 8. 미정/확인 필요 사항

| ID | 내용 | 관련 항목 | 확인 주체 | 상태 |
| --- | --- | --- | --- | --- |
| ISSUE-007 | 공공데이터 공통표준 대조 완료. TERM-002, TERM-004, TERM-009, TERM-010은 준용, TERM-008은 프로젝트신규로 등록 | TERM-002, TERM-004, TERM-008, TERM-009, TERM-010 | Data Architect | Closed |
| ISSUE-008 | API 필드명과 DB 컬럼명 명명 규칙 확정 필요 | 전체 항목 | Technical Architect | Draft |

## 9. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-07 | 로그인 게시판 샘플 프로젝트 단어사전 최초 작성 | Codex |  |  |
| v0.2 | 2026-05-07 | RUN-002 기준 공공데이터 공통표준 대조 결과 반영 | Codex |  |  |
