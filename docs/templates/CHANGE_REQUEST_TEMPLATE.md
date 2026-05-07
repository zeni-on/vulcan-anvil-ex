# 변경요청서 템플릿

```yaml
---
document_id: DOC-PM-G1-001
title: Change Request
title_ko: 변경요청서
project:
gate: G1
status: Draft
version: v0.1
owner_role: Project Manager
author:
reviewer:
approver:
created_at:
updated_at:
related_ids:
  - CR-001
change_reason: 최초 초안 작성
---
```

## 1. 변경요청 개요

| 항목 | 내용 |
| --- | --- |
| CR-ID | CR-001 |
| 제목 |  |
| 요청 출처 | 고객 / 감리 / QA / 개발 / 운영 / 내부 검토 |
| 요청자 |  |
| 요청일 |  |
| 우선순위 | P0 / P1 / P2 / P3 |
| 긴급도 | 긴급 / 일반 / 보류 가능 |
| 상태 | Draft / Reviewing / Approved / Rejected / Deferred / Done |

## 2. 요청 내용

| 항목 | 내용 |
| --- | --- |
| 현재 기준 |  |
| 변경 요청 |  |
| 변경 사유 |  |
| 기대 효과 |  |
| 미반영 시 영향 |  |

## 3. 영향도 분석

| 구분 | 영향받는 ID | 영향 내용 | 재진입 Gate |
| --- | --- | --- | --- |
| 요구사항 | REQ- / NREQ- / AC- |  | G1 |
| 기능 | FUNC- |  | G2 |
| 화면 | SCR- |  | G2 |
| 프로그램 | PGM- |  | G2 |
| 데이터 | DB- / TERM- |  | G2 |
| 보안 | SEC- / KISA-SD-2021 SR- |  | G1/G2/G3 |
| 테스트 | UT- / IT- / PT- / UI- |  | G3 |
| 증적 |  |  | G4 |
| 승인/릴리즈 |  |  | G5 |

## 4. 분류

| 항목 | 선택 |
| --- | --- |
| 변경 유형 | Patch / Minor CR / Major CR / Baseline CR |
| 처리 방식 | 즉시 Run / Backlog 등록 / 반려 / 보류 |
| 최소 재진입 Gate | G1 / G2 / G3 / G4 / G5 |
| Scope | REQ-, AC-, FUNC-, SCR-, PGM-, DB-, SEC-, UT- |

## 5. 승인 판단

| 항목 | 내용 |
| --- | --- |
| 승인 여부 | Approved / Rejected / Deferred |
| 승인자 |  |
| 승인일 |  |
| 판단 근거 |  |
| 조건부 승인 조건 |  |

## 6. 반영 계획

| 작업 | 대상 | 담당 | 예정 Run | 상태 |
| --- | --- | --- | --- | --- |
| 요구사항 갱신 |  |  | RUN- | Pending |
| 설계 갱신 |  |  | RUN- | Pending |
| 테스트 갱신 |  |  | RUN- | Pending |
| 구현/수정 |  |  | RUN- | Pending |
| 검증/증적 |  |  | RUN- | Pending |

## 7. 완료 확인

| 항목 | 확인 |
| --- | --- |
| 영향받는 요구사항이 갱신되었는가 |  |
| 설계 산출물이 갱신되었는가 |  |
| 테스트케이스가 갱신되었는가 |  |
| 구현과 테스트가 완료되었는가 |  |
| 증적이 갱신되었는가 |  |
| 요구사항추적표에 CR이 반영되었는가 |  |
| 변경이력이 기록되었는가 |  |

## 8. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 |  | 최초 작성 |  |  |  |
