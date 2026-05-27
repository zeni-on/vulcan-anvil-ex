# 프로젝트 단어사전

```yaml
---
document_id: DOC-DATA-G2-001
title: Project Glossary
title_ko: 프로젝트 단어사전
project: regression-simple-hello
gate: G2
status: Baseline Candidate
version: v0.1
owner_role: Data Architect
author: Codex Orchestrator
reviewer: Documentation Curator
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - TERM-001
  - WORD-001
  - DOMAIN-001
  - REQ-001-01
  - API-001
change_reason: hello API 응답 용어 기준 작성
---
```

## 1. 문서 목적

본 문서는 이번 범위에서 사용하는 최소 용어를 기록한다. DB 컬럼이나 화면 항목은 없지만, API 응답 literal을 추적하기 위해 `TERM-001`, `WORD-001`, `DOMAIN-001`을 둔다.

## 2. 프로젝트 용어 목록

| TERM-ID | 한글명 | 영문명 | 영문 약어 | 정의 | 도메인 | 출처 | 표준 준용 상태 | 등록 사유 | 관련 ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-001 | hello 응답 | hello response | HELLO_RESP | hello API가 반환하는 단순 문자열 응답 | DOMAIN-001 | 프로젝트 | 프로젝트 용어 | 공공데이터 표준 대상 업무 데이터가 아닌 API 응답 literal | API-001 / REQ-001-01 |

## 3. 프로젝트 단어 목록

| WORD-ID | 한글 단어 | 영문명 | 영문 약어 | 정의 | 출처 | 표준 준용 상태 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WORD-001 | hello | hello | HELLO | API 성공 응답 본문으로 사용하는 고정 문자열 | 프로젝트 | 프로젝트 단어 | 국제화 대상 메시지가 아니라 검증 literal |

## 4. 도메인 목록

| DOMAIN-ID | 도메인명 | 데이터 타입 | 길이 | 소수점 | 저장 형식 | 표현 형식 | 출처 | 표준 준용 상태 |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| DOMAIN-001 | PlainTextResponse | string | 5 | 0 | 저장 안 함 | `hello` | 프로젝트 | 프로젝트 도메인 |

## 5. 화면/API/DB 항목 매핑

| TERM-ID | 한글명 | 화면 항목명 | API 필드명 | DB 컬럼명 | 도메인 | 보안 분류 | 관련 SEC | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-001 | hello 응답 | 해당없음 | response body | 해당없음 | DOMAIN-001 | 일반 | SEC-001 | 단순 문자열 응답 |

## 6. 보안/개인정보 분류

| TERM-ID | 한글명 | 보안 분류 | 저장 보호 | 전송 보호 | 로그 출력 | 관련 SEC | 검증 방향 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TERM-001 | hello 응답 | 일반 | 저장 없음 | 일반 로컬 HTTP 응답 | 민감정보 없음 | SEC-001 | IT 후보 |

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | hello API 응답 용어 기준 작성 | Codex Orchestrator | Orchestrator | 사용자 |

## 8. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 주요 데이터 항목이 용어 목록에 등록되었는가 | 예 - TERM-001 |
| 공공데이터 공통표준 검토 결과가 기록되었는가 | 예 - 프로젝트 용어 |
| 표준 미존재 용어의 등록 사유가 작성되었는가 | 예 |
| 화면/API/DB 항목 매핑이 작성되었는가 | 예 |
| 개인정보/인증정보/민감정보가 분류되었는가 | 예 - 없음 |
| 보호 대상 데이터가 `SEC` 항목과 연결되었는가 | 예 - SEC-001 일반 기준 |
