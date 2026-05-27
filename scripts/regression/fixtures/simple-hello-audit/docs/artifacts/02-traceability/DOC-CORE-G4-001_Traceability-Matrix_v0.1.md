# 요구사항추적표

```yaml
---
document_id: DOC-CORE-G4-001
title: Traceability Matrix
title_ko: 요구사항추적표
project: 프로젝트명
gate: G5
status: Approved
version: v0.1
owner_role: Documentation Curator
author: Codex Orchestrator
reviewer: Orchestrator
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - REQ-001-01
  - AC-001-01
  - AC-001-02
  - NREQ-001
  - AC-002-01
  - RUN-014
  - RUN-015
  - RUN-016
  - RUN-017
  - RUN-019
  - BL-001
change_reason: Gate 5 릴리즈 승인 및 ISSUE-QA-001 백로그 이월 반영
---
```

## 1. 문서 목적

본 문서는 요구사항이 기능, 화면, 프로그램, 데이터, 보안, 테스트, 증적까지 어떻게 연결되는지 추적한다.

요구사항추적표는 Gate 1부터 작성하기 시작하고, Gate 2, Gate 3, Gate 4, Gate 5를 지나며 계속 갱신한다.

## 2. 작성 기준

- 요구사항추적표는 “요구사항 하나가 어디에 설계되고 어떻게 검증되었는가”를 보여주는 중심 산출물이다.
- 모든 상세 `REQ-NNN-NN`은 하나 이상의 `AC-NNN-NN`와 연결하는 것을 원칙으로 한다.
- 모든 핵심 `AC`는 하나 이상의 테스트 또는 검증 증적과 연결해야 한다.
- 모든 테스트는 `REQ`, `NREQ`, `AC`, `SEC`, `CR` 중 하나 이상과 연결되어야 한다.
- Gate 3 완료 시점에는 `UT-ID`, `IT-ID`, `PT-ID`에 `미정` 또는 `확인필요`가 남아 있으면 안 된다. 필요 없는 테스트 유형은 `해당없음`으로 쓰고, 통합/UI 테스트로 대체 검증하는 경우 해당 `IT-ID` 또는 `UI-ID`를 명시한다.
- 화면 퍼블리싱 산출물 또는 외부 시안이 구현 기준이면 `UIREF-ID`와 `UICON-ID`를 함께 연결한다.
- 보안 관련 항목은 가능한 경우 `SR-ID` 또는 외부 보안 기준을 함께 기록한다.
- 데이터 항목 관련 요구사항은 공공데이터 표준 검토 결과를 연결한다.
- 비어 있는 연결은 숨기지 말고 `미정`, `해당없음`, `확인필요` 중 하나로 표시한다.

## 3. 상태값

| 상태 | 의미 |
| --- | --- |
| `Draft` | 초안 |
| `Defined` | 요구사항/기준 정의 완료 |
| `Designed` | 설계 산출물 연결 완료 |
| `Planned` | 테스트 계획 연결 완료 |
| `Implemented` | 구현 완료 |
| `Verified` | 검증 완료 |
| `Changed` | 변경 발생 |
| `Deferred` | 후속 범위로 이관 |
| `Rejected` | 제외 또는 반려 |

## 4. 요구사항 추적 매트릭스

| REQ-ID | NREQ-ID | AC-ID | FUNC-ID | SCR-ID | UIREF-ID | UICON-ID | PGM-ID | DB-ID | IF-ID | SEC-ID | 참조 표준 | UT-ID | IT-ID | UI-ID | PT-ID | 상태 | 증적 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001-01 |  | AC-001-01 | FUNC-001 | 해당없음 | 해당없음 | 해당없음 | PGM-001 / API-001 | 해당없음 | 해당없음 | SEC-001 | KISA-SD-2021 SR3-1 / OWASP A05 / CWE-209 | 해당없음 | IT-001 / IT-002 | 해당없음 | 해당없음 | Verified | DOC-CORE-G1-001, DOC-ARCH-G2-001, DOC-API-G2-001, DOC-CORE-G2-002, DOC-QA-G3-001, backend/app/api/hello.py, backend/tests/test_hello_api.py, docs/runs/RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md, DOC-QA-G4-002, docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-001.log, docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-002.log, DOC-PM-G5-001 | 필수 Gate 4 QA Pass, Gate 5 사용자 승인 대기 |
| REQ-001-01 |  | AC-001-02 | FUNC-001 | 해당없음 | 해당없음 | 해당없음 | PGM-001 / API-001 | 해당없음 | 해당없음 | SEC-001 | KISA-SD-2021 SR3-1 / OWASP A05 / CWE-209 | UT-001 | IT-001 / IT-002 | 해당없음 | 해당없음 | Verified | DOC-CORE-G1-001, DOC-CORE-G2-001, DOC-API-G2-001, DOC-CORE-G2-002, DOC-QA-G3-001, backend/app/services/hello_service.py, backend/app/api/hello.py, backend/tests/test_hello_service.py, backend/tests/test_hello_api.py, docs/runs/RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md, DOC-QA-G4-002, docs/artifacts/04-review/evidence/qa-001/QA-CMD-UT-001.log, docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-001.log, docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-002.log, DOC-PM-G5-001 | `hello` 본문 검증 Pass, Gate 5 사용자 승인 대기 |
|  | NREQ-001 | AC-002-01 | FUNC-001 | 해당없음 | 해당없음 | 해당없음 | PGM-001 / API-001 | 해당없음 | 해당없음 | SEC-001 | TECH_STACK_BASELINES §8 / SEC-001 | 해당없음 | IT-002 | 해당없음 | 해당없음 | Verified | DOC-DEV-G2-001, DOC-ARCH-G2-001, DOC-QA-G3-001, backend/app/main.py, backend/app/api/hello.py, docs/runs/RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md, DOC-QA-G4-002, docs/artifacts/04-review/evidence/qa-000/, docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-002.log, DOC-PM-G5-001 | 로컬 실행 재현성 필수 QA Pass, Gate 5 사용자 승인 대기 |

## 5. 요구사항별 검증 요약

| REQ-ID | 요구사항명 | 인수기준 수 | 설계 연결 | 테스트 연결 | 검증 상태 | 미해결 사항 |
| --- | --- | ---: | --- | --- | --- | --- |
| REQ-001-01 | hello 응답 반환 | 2 | FUNC-001 / API-001 / PGM-001 / SEC-001 | UT-001 / IT-001 / IT-002 | Verified | Gate 5 승인 완료, ISSUE-QA-001은 BL-001로 이월 |
| NREQ-001 | 로컬 재현성 | 1 | CNT-001 / PGM-001 / Development Standard | IT-002 | Verified | Gate 5 승인 완료 |

## 6. 보안항목 추적

| SEC-ID | 보안항목 | 관련 REQ/NREQ | 참조 표준 | 적용 대상 | 검증 테스트 | 증적 | 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | 민감정보 미처리 및 오류정보 노출 방지 | REQ-001-01 / NREQ-001 | KISA-SD-2021 SR3-1 / OWASP A05 / CWE-209 / CWE-532 | API-001 / PGM-001 / CNT-001 | IT-001 / IT-002 / 리뷰 | DOC-SEC-G2-001; DOC-QA-G3-001; backend/app/api/hello.py; docs/runs/RUN-012_build-wave-BW-001_python-hello-api-feature-implementation_v0.1.md; DOC-QA-G4-002; docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-001.log; docs/artifacts/04-review/evidence/qa-001/QA-CMD-IT-002.log; DOC-PM-G5-001 | Verified |

## 7. 데이터 표준 추적

| DB-ID | 데이터 항목 | 관련 REQ/NREQ | 공공데이터 표준 용어 | 영문 약어 | 도메인 | 표준 준용 여부 | 비고 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 저장 데이터 없음 | REQ-001-01 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | DB 범위 제외 |

## 8. 변경요청 영향 추적

| CR-ID | 변경요청명 | 영향받는 REQ | 영향받는 설계 | 영향받는 테스트 | 승인 여부 | 반영 버전 |
| --- | --- | --- | --- | --- | --- | --- |
| 해당없음 | 현재 변경요청 없음 | 해당없음 | 해당없음 | 해당없음 | 해당없음 | 해당없음 |

## 9. 추적성 결함 목록

| 결함 ID | 결함 유형 | 관련 ID | 설명 | 조치 담당 | 상태 |
| --- | --- | --- | --- | --- | --- |
| ISSUE-001 | 정식 QA 증적 미생성 | UT-001 / IT-001 / IT-002 | Gate 4에서 QA-CMD 로그와 Test Result로 정식 증적화했다. | Orchestrator | Closed |
| ISSUE-QA-001 / BL-001 | 선택 정적 검사 실패 | IT-001 | 필수 QA는 통과했지만 선택 ruff 검사에서 `backend/tests/test_hello_api.py` E402 4건이 발생했다. Gate 5 승인 조건으로 백로그 이월한다. | Orchestrator / 사용자 | Backlogged |

결함 유형 예시:

- 인수기준 누락
- 설계 연결 누락
- 테스트 계획 누락
- 보안항목 검증 누락
- 보안항목 참조 표준 누락
- 데이터 표준 검토 누락
- 증적 누락
- 변경요청 영향 분석 누락

## 10. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | Gate 1 요구사항/인수기준 초기 추적성 작성, Gate 2 설계 연결, Gate 3 테스트 계획 반영, Impl 구현 파일 및 Wave 검증 결과 반영 | Codex Orchestrator | Orchestrator | 사용자 |
| v0.1 | 2026-05-24 | Gate 4 QA 증적, Gate 5 릴리즈 승인서, ISSUE-QA-001 잔여 위험을 반영 | Codex Release Worker | Orchestrator | 사용자 |
| v0.1 | 2026-05-24 | Gate 5 승인 및 `BL-001` 백로그 이월 반영 | Codex Orchestrator | Orchestrator | 사용자 |

## 11. 검토 체크리스트

| 항목 | 확인 |
| --- | --- |
| 모든 `REQ`가 추적표에 포함되었는가 | 예 |
| 모든 핵심 `AC`가 테스트 또는 검증 증적과 연결되었는가 | 예 - Gate 4 QA-CMD 증적 연결 완료 |
| 모든 `PGM`이 관련 `FUNC` 또는 `REQ`와 연결되었는가 | 예 |
| 모든 `SEC`가 적용 대상과 검증 테스트를 가지는가 | 예 |
| 보안 관련 `SEC`에 적용 가능한 `SR-ID`가 기록되었는가 | 예 |
| 데이터 항목의 공공데이터 표준 검토 여부가 기록되었는가 | 예 - 저장 데이터 없음 |
| 테스트 목적이 요구사항/인수기준/보안항목과 연결되는가 | 예 |
| 변경요청의 영향받는 ID가 기록되었는가 | 해당없음 |
| 검증 완료 항목에 증적이 존재하는가 | 예 - QA-000~QA-003 로그, Test Result, Release Approval 연결 완료 |
