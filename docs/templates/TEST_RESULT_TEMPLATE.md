# Gate 4 QA 테스트 결과서

```yaml
---
document_id: DOC-QA-G4-002
title: QA Test Result
title_ko: QA 테스트 결과서
project:
gate: G4
status: Draft
version: v0.1
owner_role: QA Reviewer
author:
reviewer:
approver:
created_at:
updated_at:
related_ids:
  - REQ-
change_reason: 최초 초안 작성
---
```

## 1. QA 범위

| 구분 | 범위 |
| --- | --- |
| 대상 기능 |  |
| 대상 요구사항 | REQ- |
| 대상 화면 | SCR- |
| 기준 시안 | UIREF- |
| QA 방식 | 단위/통합 테스트, 추적성 검사, 브라우저 확인, 화면 캡처 증적 |

## 2. 요구사항 검증 요약

> 대시보드는 이 표의 헤더를 기준으로 테스트 결과를 렌더링한다. 헤더명은 유지한다.

| REQ-ID | 검증 항목 | 관련 테스트 | 결과 | 증적 |
| --- | --- | --- | --- | --- |
| REQ- |  | UT- / IT- / UI- | Pass / Fail / Not Run / Skipped | EV- / UI- / LOG- 또는 경로 |

## 3. 실행 검증

> 명령, 브라우저 수동 확인, Playwright, 보안 점검 등 실제 실행한 검증만 작성한다.

| 검증 ID | 명령/방법 | 결과 | 요약 |
| --- | --- | --- | --- |
| QA-CMD-001 |  | Pass / Fail / Not Run / Skipped |  |

## 4. 화면 증적

> 대시보드는 이 표의 헤더를 기준으로 이미지 썸네일과 미리보기를 렌더링한다. 파일은 프로젝트 기준 상대 경로를 쓴다.

| 증적 ID | 관련 UI | 파일 | 설명 |
| --- | --- | --- | --- |
| EV-UI-001 | UI- | docs/artifacts/04-review/evidence/ui/ |  |

## 5. QA 발견사항과 재귀 수정 방침

| 항목 | 내용 |
| --- | --- |
| 현재 Open FIND | 없음 / FIND- |
| QA 중 발견된 결함 처리 | 기존 설계 범위 안의 결함은 FIND 등록 후 G4 QA Fix Loop에서 수정, 테스트 재실행, 증적 갱신 |
| CR 승격 기준 | 요구사항, AC, 화면/프로그램/API/DB 설계, 보안 기준 변경이 필요한 경우 CR로 승격 |
| 이번 QA 판단 |  |

## 6. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 |  | 최초 작성 |  |  |  |
