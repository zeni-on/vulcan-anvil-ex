# 보안가이드

```yaml
---
document_id: DOC-SEC-G2-001
title: Security Guide
title_ko: 보안가이드
project: regression-simple-hello
gate: G2
status: Baseline Candidate
version: v0.1
owner_role: Security Reviewer
author: Codex Orchestrator
reviewer: Orchestrator
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - SEC-001
  - REQ-001-01
  - NREQ-001
  - API-001
  - PGM-001
change_reason: Gate 2 hello API 보안 기준 작성
---
```

## 1. 문서 목적

본 문서는 Python hello API 구현자가 따라야 할 프로젝트 보안 기준을 정의한다. 이번 범위는 인증/인가, DB, 개인정보 처리가 없으므로 보안 범위는 민감정보 미처리, 내부 오류정보 노출 방지, 안전한 로그 기준에 집중한다.

## 2. 적용 범위

| 구분 | 범위 | 관련 ID |
| --- | --- | --- |
| 인증 | 이번 범위 해당없음 | REQ-001-01 |
| 접근통제 | 이번 범위 해당없음 | REQ-001-01 |
| 입력값 검증 | 요청 본문, path, query 없음 | API-001 / PGM-001 |
| 중요정보 보호 | 개인정보, 인증정보, 영속 데이터 미처리 | SEC-001 |
| 오류/로그 | 내부 stack trace, 환경정보, 민감정보 응답/로그 노출 금지 | NREQ-001 / SEC-001 |

## 3. 보안가이드 목록

| SEC-ID | 보안가이드명 | 관련 REQ/NREQ | KISA 근거 | OWASP/CWE | 적용 대상 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | 민감정보 미처리 및 오류정보 노출 방지 | REQ-001-01 / NREQ-001 | KISA-SD-2021 SR3-1 | OWASP-T10-2021 A05 / CWE-209 / CWE-532 | API-001 / PGM-001 / CNT-001 | Baseline Candidate |

## 4. 기능 유형별 필수 후보 검토

| 기능 유형 | 필수 후보 `SEC-ID` | 필요 여부 | 사유 |
| --- | --- | --- | --- |
| 로그인/회원가입 | SEC-AUTH-PW, SEC-AUTH-LOGIN, SEC-SESSION | 해당없음 | 인증 기능 제외 |
| 사용자별 데이터 | SEC-ACCESS-OWNER | 해당없음 | 사용자별 데이터 없음 |
| 검색/목록/상세 API | SEC-INPUT, SEC-OUTPUT | 부분 해당 | 요청 입력 없음. 출력은 단순 문자열이며 내부 정보 미노출 기준 적용 |
| 게시글/댓글/HTML 출력 | SEC-XSS | 해당없음 | HTML 출력 없음 |
| 개인정보/민감정보 저장 | SEC-DATA-STORE | 해당없음 | 저장 데이터 없음 |
| 중요정보 전송 | SEC-DATA-TRANSFER | 해당없음 | 중요정보 전송 없음 |
| 오류 처리 | SEC-ERROR | 해당 | SEC-001로 반영 |
| 암호/토큰/난수 | SEC-CRYPTO | 해당없음 | 암호/토큰/난수 없음 |

## 5. 상세 보안가이드

### SEC-001 민감정보 미처리 및 오류정보 노출 방지

| 항목 | 내용 |
| --- | --- |
| 관련 요구사항 | REQ-001-01 / NREQ-001 |
| 관련 인수기준 | AC-001-01 / AC-001-02 / AC-002-01 |
| 관련 기능/화면/프로그램/DB | FUNC-001 / SCR 해당없음 / PGM-001 / DB 해당없음 |
| KISA 제안/근거 | KISA-SD-2021 SR3-1 오류 메시지를 통한 정보노출 방지 |
| OWASP/CWE 보조 분류 | OWASP-T10-2021 A05 Security Misconfiguration / CWE-209 / CWE-532 |
| 매핑 확실도/주의 | Medium. 단순 API이므로 주요 위험은 오류정보 노출과 로그 민감정보 노출이다. |
| 위협 또는 약점 | 내부 stack trace, 환경 경로, 라이브러리 버전, 비밀값이 응답이나 로그에 노출될 수 있다. |
| 구현 규격 | 정상 응답은 `hello`만 반환한다. 오류 응답은 내부 상세 stack trace를 노출하지 않는다. |
| 화면 규격 | 해당없음 |
| 데이터 규격 | 개인정보, 인증정보, 영속 데이터 없음 |
| 오류/메시지 규격 | 사용자 노출 오류는 일반 메시지로 제한한다. |
| 로그/증적 규격 | 테스트/QA 로그에는 명령, exit code, 상태만 남기고 비밀값은 기록하지 않는다. |
| 예외 또는 위험수용 | 없음 |

#### 5.1 KISA 근거와 프로젝트 상세스펙

| 구분 | 내용 | 출처 또는 결정 근거 |
| --- | --- | --- |
| KISA 제안/근거 | 오류 메시지를 통해 시스템 내부 정보가 노출되지 않도록 한다. | KISA-SD-2021 SR3-1 |
| OWASP/CWE 보조 분류 | A05, CWE-209, CWE-532 | 위험/약점 분류용 |
| 프로젝트 상세스펙 | 정상 응답은 `hello`; 오류 시 내부 stack trace, 파일 경로, 환경변수, 의존성 상세를 응답에 포함하지 않는다. | API-001 / PGM-001 |
| 프로젝트 추가 정책 | 운영 코드에서 secret, token, password, authorization header를 로그에 남기지 않는다. 현재 범위에는 해당 값이 없어야 한다. | 개발표준 |

#### 5.2 구현 규격 상세

| 규격 ID | 항목 | KISA 제안/근거 | 프로젝트 상세스펙 | 적용 위치 | 필수 여부 | 검증 ID |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-001-R01 | 정상 응답 최소화 | 정보 노출 최소화 | 정상 응답 본문은 `hello`만 포함 | API-001 / PGM-001 | Must | IT-001 후보 |
| SEC-001-R02 | 내부 오류정보 노출 방지 | KISA-SD-2021 SR3-1 | stack trace, 파일 경로, 환경변수, 내부 설정을 응답에 포함하지 않음 | PGM-001 | Must | IT-002 후보 / 리뷰 |
| SEC-001-R03 | 민감정보 로그 금지 | CWE-532 | 비밀번호, 토큰, 인증 헤더, secret이 생기면 로그 출력 금지. 현재 범위에서는 생성/처리하지 않음 | PGM-001 / QA 로그 | Must | 리뷰 |

#### 5.3 테스트 기준

| 테스트 ID | 테스트 유형 | 검증할 보안가이드 | 입력/조건 | 기대 결과 | 증적 |
| --- | --- | --- | --- | --- | --- |
| IT-001 후보 | Integration | SEC-001-R01 | `GET /hello` | 200, `hello`, 불필요한 데이터 없음 | Gate 4 QA-CMD 로그 |
| IT-002 후보 | Integration/Review | SEC-001-R02/R03 | 로컬 실행 및 오류/로그 검토 | 내부 상세와 민감정보 노출 없음 | Gate 4 QA-CMD 로그 또는 리뷰 결과 |

#### 5.4 OWASP/CWE 매핑 메모

| 분류 | 값 | 확실도 | 주의점 |
| --- | --- | --- | --- |
| OWASP | OWASP-T10-2021 A05 | Medium | 오류/디버그 노출 방지 관점 |
| CWE | CWE-209 | Medium | 오류 메시지 정보 노출 |
| CWE | CWE-532 | Medium | 로그 민감정보 출력 |

## 6. 화면/프로그램/테스트 반영 체크

| 확인 항목 | 연결 문서 | 확인 |
| --- | --- | --- |
| 화면설계서의 입력항목/오류메시지가 본 보안가이드 값을 따른다. | Screen Spec | 해당없음 - UI 제외 |
| 프로그램 설계서의 검증 로직과 예외 처리가 본 보안가이드 값을 따른다. | Program Design | 예 |
| DB명세서의 저장/마스킹/출력 금지 항목이 본 보안가이드 값을 따른다. | Database Spec | 해당없음 - DB 제외 |
| 테스트케이스가 각 `SEC-ID`의 규격 ID를 검증한다. | Test Case | Gate 3에서 작성 |
| 요구사항추적표가 `SEC-ID`, 테스트 ID, 증적을 연결한다. | Traceability Matrix | Gate 3/4에서 보강 |

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | Gate 2 hello API 보안 기준 작성 | Codex Orchestrator | Orchestrator | 사용자 |
