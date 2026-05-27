# 화면설계서

```yaml
---
document_id: DOC-CORE-G2-003
title: Screen Specification
title_ko: 화면설계서
project: regression-simple-hello
gate: G2
status: N/A
version: v0.1
owner_role: UX/UI Designer
author: Codex Orchestrator
reviewer: Requirements Lead
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - REQ-001-01
  - FUNC-001
  - API-001
change_reason: hello API 범위에서 화면 제외 결정 기록
---
```

## 1. 문서 목적

본 문서는 이번 Gate 2 범위에서 프론트엔드 화면이 제외되었음을 명확히 기록한다. 이번 기능은 API 호출 검증이 목적이며 화면, 시안, UI Implementation Contract, Playwright 화면 증적은 필요하지 않다.

## 2. 화면 적용 여부

| 항목 | 내용 |
| --- | --- |
| 화면 사용 여부 | 사용하지 않음 |
| 제외 사유 | `REQ-001-01`은 HTTP API 호출 결과를 검증하는 요구사항이며 UI 표시가 필요 없다. |
| 관련 API | API-001 |
| 후속 처리 | 화면에서 hello 응답을 표시하는 기능이 필요하면 별도 백로그/CR로 분리한다. |

## 3. 화면 목록

| SCR-ID | 화면명 | 유형 | 관련 FUNC | 관련 PGM | 관련 SEC | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 화면 없음 | 해당없음 | FUNC-001 | PGM-001 | SEC-001 | N/A |

## 4. 화면 시안 및 기준 증적

| SCR-ID | 시안/와이어프레임 ID | 출처 | 파일/URL | 기준 Viewport | 비교 기준 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | API 명령 검증으로 대체 | N/A |

## 5. UI Implementation Contract

| Contract-ID | 관련 SCR | 기준 UIREF | 기준 파일 | 기준 CSS/토큰 | 구현 기준 유형 | 상태 |
| --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | N/A |

## 6. UI 테스트 및 증적 기준

| UI-ID | 대상 SCR | 사용자 흐름 | 기준 시안 | 관련 Contract | Viewport | 캡처 경로 | 비교 기준 | 관련 AC/SEC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 해당없음 | API 호출 검증 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | 명령 기반 HTTP 검증으로 대체 | AC-001-01 / AC-001-02 |

## 7. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | hello API 범위에서 화면 제외 결정 기록 | Codex Orchestrator | Orchestrator | 사용자 |

## 8. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 화면에 `SCR-ID`가 부여되었는가 | 해당없음 |
| 화면이 `REQ`, `AC`, `FUNC`와 연결되었는가 | 해당없음 |
| 화면 이벤트가 관련 `PGM`과 연결되었는가 | 해당없음 |
| 입력/출력 항목이 프로젝트 단어사전과 연결되었는가 | 해당없음 |
| 입력값 검증과 오류 메시지가 작성되었는가 | 해당없음 |
| 보안 고려사항에 `SEC-ID`와 `SR-ID`가 연결되었는가 | 해당없음 |
| 외부/생성 시안이 `SCR-ID`, 출처, 파일/URL, viewport와 연결되었는가 | 해당없음 |
| 기준 시안이 구현 계약인지 참고자료인지 명시되었는가 | 해당없음 |
| 구현 계약이면 필수 유지, 변경 허용, 변경 금지, 비교 방식이 작성되었는가 | 해당없음 |
| 기본/오류/빈/권한 제한 상태가 필요한 경우 작성되었는가 | 해당없음 |
| UI 테스트와 캡처 증적 기준이 작성되었는가 | 해당없음 |
| 테스트 연결이 작성되었는가 | API 통합테스트로 대체 |
