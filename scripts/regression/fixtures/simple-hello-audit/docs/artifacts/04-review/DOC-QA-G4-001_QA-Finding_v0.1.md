# QA 발견사항

```yaml
---
document_id: DOC-QA-G4-001
title: QA Finding
title_ko: QA 발견사항
project: regression-simple-hello
gate: G4
status: Draft
version: v0.1
owner_role: QA Reviewer
author: Codex QA Worker
reviewer: Orchestrator
approver: 사용자
created_at: 2026-05-24
updated_at: 2026-05-24
related_ids:
  - RUN-014
  - RUN-015
  - RUN-016
  - RUN-017
  - REQ-001-01
  - AC-001-01
  - AC-001-02
  - AC-002-01
  - FUNC-001
  - PGM-001
  - API-001
  - SEC-001
  - UT-001
  - IT-001
  - IT-002
change_reason: Gate 4 QA-000 환경 준비/스모크, QA-001 명령 기반 검증, QA-002 UI/E2E 적용 제외, QA-003 결과 정리 반영
---
```

## 1. 발견사항 개요

| 항목 | 내용 |
| --- | --- |
| 현재 Open FIND | 없음 |
| 현재 Open ISSUE | ISSUE-QA-001 - 선택 ruff 정적 검사 E402 4건 |
| 대상 Run | RUN-014 QA-000, RUN-015 QA-001, RUN-016 QA-002, RUN-017 QA-003 |
| 발견 출처 | QA-001 command validation, QA-002 UI/E2E applicability, QA-003 consolidation |
| 발견일 | 2026-05-24 |
| 상태 | Open FIND 없음, ISSUE-QA-001 Orchestrator 판단 필요 |
| CR 필요 여부 | No |

## 2. 관련 추적 ID

| 구분 | 관련 ID |
| --- | --- |
| 요구사항 | REQ-001-01 |
| 인수조건 | AC-001-01, AC-001-02, AC-002-01 |
| 기능 | FUNC-001 |
| 화면 | 해당없음 |
| 프로그램 | PGM-001, API-001 |
| 데이터 | 해당없음 |
| 보안 | SEC-001 |
| 테스트 | UT-001, IT-001, IT-002 |
| 증적 | docs/artifacts/04-review/evidence/qa-000/, docs/artifacts/04-review/evidence/qa-001/, docs/artifacts/04-review/evidence/qa-002/ |

## 2.1 증적 매칭

| FIND/ISSUE ID | 관련 테스트/화면 ID | 증적 ID | 증적 성격 | 상태 | 설명 |
| --- | --- | --- | --- | --- | --- |
| 해당없음 | UT-001 / IT-001 / IT-002 | QA-000-* | 환경 준비/스모크 증적 | Pass | QA-000 범위에서 후속 QA를 차단하는 결함은 발견되지 않았다. |
| ISSUE-QA-001 | IT-001 | QA-CMD-RUFF | 선택 정적 검사 증적 | Open | `backend/tests/test_hello_api.py`에서 `pytest.importorskip("fastapi")` 이후 import가 있어 ruff E402 4건이 발생했다. |
| 해당없음 | UI 해당없음 | QA-UI-APPLICABILITY | UI/E2E 적용 여부 증적 | Skipped | API-only 범위이며 UI-ID/SCR/UIREF가 없어 화면 검증은 적용 제외했다. |

## 3. 현상

| 항목 | 내용 |
| --- | --- |
| 재현 조건 | QA-001 명령 기반 검증 중 `python -m ruff check .` 실행 |
| 실제 결과 | 필수 pytest/API/trace 검증은 통과했으나 선택 ruff 정적 검사에서 E402 4건 발생. QA-001 Run 문서는 현재 worktree에 없음 |
| 기대 결과 | 필수 명령 검증은 exit code 0으로 완료되고, 선택 정적 검사 실패는 숨기지 않고 Orchestrator 판단 항목으로 기록 |
| 첨부 증적 | docs/artifacts/04-review/evidence/qa-001/QA-CMD-RUFF.log, docs/artifacts/04-review/evidence/qa-003/QA-003-CONSOLIDATION.log |

## 4. 분류 판단

| 질문 | 답변 | 근거 |
| --- | --- | --- |
| 기존 요구사항 의미가 바뀌는가 | No | ruff E402는 hello API 요구사항 의미 변경 없음 |
| AC 추가/삭제/변경이 필요한가 | No | 테스트 명령 결과상 AC 변경 필요 없음 |
| 설계 변경이 필요한가 | No | API-only 설계와 기능 계약은 pytest/API smoke/check-trace에서 통과 |
| 보안 기준 완화가 필요한가 | No | SEC-001 기준 완화 없음 |
| 기존 설계를 만족시키기 위한 수정인가 | No | 소스 수정 없음 |

판정:

```text
Open FIND 없음. ISSUE-QA-001은 선택 정적 검사 실패로, Orchestrator가 비차단 ISSUE 유지 또는 QA Fix Loop/FIND 승격 여부를 결정한다.
Orchestrator 재검증 결과 RUN-015는 dev 통합 브랜치에 존재한다. QA worker의 누락 보고는 stale QA worktree 기준이므로 별도 ISSUE로 유지하지 않는다.
```

## 5. 조치 내용

| 항목 | 내용 |
| --- | --- |
| 원인 | 해당없음 |
| 수정 파일 | 해당없음 |
| 수정 요약 | 소스 수정 없음 |
| 문서 갱신 | RUN-017, DOC-QA-G4-001, DOC-QA-G4-002에 QA-003 결과 정리 기록 |
| 테스트 갱신 | 없음 |
| 증적 갱신 | docs/artifacts/04-review/evidence/qa-001/ |

## 6. 검증 결과

| 검증 | 명령/방법 | 결과 | 근거 |
| --- | --- | --- | --- |
| 환경 준비 | Python/pip/requirements/port 확인 | Passed | QA-000-python-version.log, QA-000-pip-check.log, QA-000-pip-install.log, QA-000-port-8000.log |
| 테스트 discovery | `python -m pytest --collect-only -q` | Passed | QA-000-pytest-collect.log |
| API startup smoke | in-process Uvicorn `/hello` 호출 | Passed | QA-000-uvicorn-startup-smoke.log |
| 단위 테스트 | `python -m pytest tests/test_hello_service.py` | Passed | QA-CMD-UT-001.log |
| 통합 테스트 | `python -m pytest tests/test_hello_api.py` | Passed | QA-CMD-IT-001.log |
| 전체 pytest | `python -m pytest` | Passed | QA-CMD-PYTEST-ALL.log |
| 명령 기반 API smoke | in-process Uvicorn `/hello` 호출 | Passed | QA-CMD-IT-002.log |
| 계약 검사 | `python vulcan.py check-contract` | Pass with Warning | QA-CMD-CHECK-CONTRACT.log |
| 추적성 검사 | `python vulcan.py check-trace` | Passed | QA-CMD-CHECK-TRACE.log |
| Run 결과 문서 검사 | `python vulcan.py run-check docs/runs/RUN-015_qa-001-gate-4-command-validation-for-python-hello-api_v0.1.md` | Passed | QA-CMD-RUN-CHECK.log |
| 선택 정적 검사 | `python -m ruff check .` | Failed | QA-CMD-RUFF.log |
| 화면 테스트 | API-only 범위로 적용 제외 | Skipped | QA-000-frontend-playwright-applicability.log |
| UI/E2E 적용 여부 | UI-ID/SCR/UIREF 및 frontend/Playwright 설정 없음 확인 | Skipped | QA-UI-APPLICABILITY.log |
| DB 검증 | DB 제외 범위로 적용 제외 | Skipped | QA-000-db-applicability.log |
| QA-003 증적 정리 | QA-000/001/002 증적 존재 여부와 dev 통합 브랜치 RUN-015 파일 존재 여부 확인 | CompletedWithIssues | QA-003-CONSOLIDATION.log |

## 7. 종료 판단

| 항목 | 확인 |
| --- | --- |
| 기존 설계 범위 내 수정임을 확인했는가 | 소스 수정 없음 |
| 관련 테스트가 통과했는가 | 필수 QA-001 테스트와 추적성 검사는 통과. 선택 ruff 실패는 ISSUE-QA-001로 기록 |
| 증적이 갱신되었는가 | 예 |
| 추적표 또는 Run 기록에 반영했는가 | Run 기록 반영. 추적표 최종 반영은 Orchestrator 판단 대상 |
| CR 승격이 불필요한 사유를 기록했는가 | 요구사항/AC/API/보안 기준 변경 없이 테스트 파일 정적 검사 이슈로 분류 가능 |

## 8. 변경이력

| 버전 | 일자 | 변경내용 | 작성자 | 검토자 | 승인자 |
| --- | --- | --- | --- | --- | --- |
| v0.1 | 2026-05-24 | QA-000 환경 준비/스모크 결과 기록 | Codex QA Worker | Orchestrator | 사용자 |
| v0.1 | 2026-05-24 | QA-001 명령 기반 검증과 ISSUE-QA-001 기록 | Codex QA Worker | Orchestrator | 사용자 |
| v0.1 | 2026-05-24 | QA-002 UI/E2E 적용 제외 판단 기록 | Codex QA Worker | Orchestrator | 사용자 |
| v0.1 | 2026-05-24 | QA-003 결과 정리와 Orchestrator 재검증 반영 | Codex QA Worker | Orchestrator | 사용자 |
