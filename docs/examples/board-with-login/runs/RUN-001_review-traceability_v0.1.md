# RUN-001 추적성 리뷰

```yaml
---
run_id: RUN-001
title: Review Traceability
title_ko: 로그인 게시판 샘플 추적성 리뷰
adapter: codex-gpt
run_type: Review
gate: G4
status: CompletedWithIssues
version: v0.1
owner_role: QA Reviewer
author: Codex
created_at: 2026-05-07
updated_at: 2026-05-07
related_ids:
  - REQ-001
  - REQ-002
  - REQ-003
  - REQ-004
  - REQ-005
  - REQ-006
change_reason: Codex/GPT Adapter 입력/출력 계약 검증을 위한 첫 Review Run 작성
---
```

## 1. Run 목적

본 Run은 로그인 게시판 샘플의 요구사항, 설계, 구현, 테스트, 화면 증적이 `Codex/GPT Adapter` 입력/출력 계약 기준으로 실제 실행 가능한지 검증한다.

이번 Run은 코드를 수정하지 않는 Review Run이다.

검증 질문:

- 샘플 산출물만 보고 다음 에이전트가 유지보수 또는 추가 기능 개발을 이어받을 수 있는가?
- Run 입력 계약이 관련 문서, ID, 범위, 완료 조건을 충분히 전달하는가?
- Run 출력 계약이 검증 결과와 남은 이슈를 충분히 기록하는가?

## 2. Run 입력

```yaml
run_id: RUN-001
adapter: codex-gpt
agent_role: review-agent
run_type: Review
gate: G4
project:
  name: Board With Login Sample
  root: docs/examples/board-with-login
goal: "로그인 게시판 샘플의 요구사항-설계-구현-테스트-화면증적 연결이 Codex/GPT Adapter 계약 기준으로 충분한지 리뷰한다."

related_ids:
  req: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006]
  nreq: [NREQ-001, NREQ-002, NREQ-003]
  ac: [AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011]
  func: [FUNC-001, FUNC-002, FUNC-003, FUNC-004, FUNC-005, FUNC-006]
  scr: [SCR-001, SCR-002, SCR-003, SCR-004, SCR-005, SCR-006]
  pgm: [PGM-001, PGM-002, PGM-003, PGM-004, PGM-005, PGM-006]
  db: [DB-001, DB-002]
  sec: [SEC-001, SEC-002, SEC-003, SEC-004]
  test: [UT-001, UT-002, UT-003, UT-004, UT-005, UT-006, UT-007, UT-008, UT-009, UT-010, UT-011, IT-001, IT-002, IT-003, IT-004, IT-005, PT-001, UI-001, UI-002, UI-003, UI-004, UI-005, UI-006]

source_documents:
  required:
    - docs/core/ID_SYSTEM.md
    - docs/core/TRACEABILITY_RULES.md
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md
    - docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
    - docs/adapters/codex-gpt/GATE_PROMPTS.md
    - docs/examples/board-with-login/DOC-CORE-G1-001_Requirements-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G2-001_Function-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G2-002_Program-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G2-003_Screen-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/examples/board-with-login/DOC-DATA-G2-001_Project-Glossary_v0.1.md
    - docs/examples/board-with-login/DOC-DATA-G2-002_Database-Spec_v0.1.md
    - docs/examples/board-with-login/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/examples/board-with-login/DOC-QA-G3-001_Test-Cases_v0.1.md
    - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md
    - docs/examples/board-with-login/DOC-QA-G4-003_UI-Test-Result_v0.1.md

scope:
  writable:
    - docs/examples/board-with-login/runs/RUN-001_review-traceability_v0.1.md
  readonly:
    - docs/core/
    - docs/adapters/codex-gpt/
    - docs/examples/board-with-login/
  excluded:
    - docs/ref-docs/
    - "**/*.db"
    - "**/__pycache__/"
    - "**/.ruff_cache/"
    - "**/*.log"

completion_criteria:
  - "Run 입력 계약 필수 필드가 채워져 있다."
  - "관련 ID가 추적표와 산출물에서 확인된다."
  - "테스트 결과서와 실제 테스트 실행 결과가 일치한다."
  - "화면 증적 파일이 존재한다."
  - "남은 이슈가 Run 출력 계약 형식으로 기록된다."

verification:
  commands:
    - "python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-0youe_bo --ignore pytest-cache-files-3qbe63bz --ignore pytest-cache-files-b5l6_sjy --ignore pytest-cache-files-srgio6u0"
    - "python -m ruff check ."
    - "Test-Path evidence/ui/SCR-001_signup/desktop.png ... SCR-006_edit-post/desktop.png"
  evidence:
    required: true
    target_documents:
      - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md
      - docs/examples/board-with-login/DOC-QA-G4-003_UI-Test-Result_v0.1.md

output_requirements:
  format: docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
  include:
    - changed_files
    - related_ids
    - verification_results
    - evidence
    - open_issues
    - next_run_suggestion

question_policy:
  ask_when:
    - "추적표와 산출물의 관련 ID가 충돌한다."
    - "리뷰 범위를 넘어 코드 수정이 필요하다."
    - "G5 승인 여부 판단이 필요하다."

security_policy:
  forbidden_paths:
    - docs/ref-docs/
  forbidden_actions:
    - "민감 참조문서를 읽지 않는다."
    - "민감문서 내용을 출력에 인용하지 않는다."
    - "토큰, 비밀번호, 개인정보를 커밋하지 않는다."
```

## 3. 실행 프롬프트

```text
너는 Vulcan-Anvil Ex Codex/GPT Adapter를 통해 실행되는 에이전트다.
아래 Run 입력 계약을 기준으로만 작업한다.

이번 Run은 Review Run이다.

작업:
1. 관련 산출물과 코드/증적 연결을 검토한다.
2. 버그, 추적성 누락, 보안 누락, 테스트 누락을 우선 찾는다.
3. 발견사항은 심각도와 관련 파일/ID를 포함해 작성한다.
4. 코드는 수정하지 않고 Run 결과만 기록한다.

출력은 RUN_OUTPUT_CONTRACT.md 형식을 따른다.
```

## 4. Run 입력 검증

| 체크 | 결과 | 근거 |
| --- | --- | --- |
| 필수 필드 존재 | Pass | `run_id`, `adapter`, `run_type`, `gate`, `goal`, `related_ids`, `source_documents`, `scope`, `completion_criteria`, `verification`, `output_requirements`, `question_policy`, `security_policy` 작성 |
| 관련 ID 존재 | Pass | `DOC-CORE-G4-001` 추적표에 REQ/AC/FUNC/SCR/PGM/DB/SEC/UT/IT/PT/UI 연결 존재 |
| 기준 문서 존재 | Pass | Core, Adapter, 샘플 산출물 문서 경로 확인 |
| 수정 범위 명확 | Pass | writable은 본 Run 기록 문서로 제한 |
| 제외 경로 포함 | Pass | `docs/ref-docs/`, DB, 캐시, 로그 제외 |
| 완료 조건 명확 | Pass | 테스트 실행, 화면 증적 파일, 미해결 이슈 기록 기준 포함 |

## 5. 검증 실행 결과

| 검증 | 명령/방식 | 결과 | 요약 |
| --- | --- | --- | --- |
| 자동 테스트 | `python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-*` | Passed | `20 passed in 8.10s` |
| 정적 검사 | `python -m ruff check .` | Passed | `All checks passed!` |
| 화면 증적 파일 | `Test-Path evidence/ui/SCR-001~SCR-006/desktop.png` | Passed | 6개 캡처 파일 모두 존재 |

## 6. Review 결과

### 6.1 추적성

| 항목 | 결과 | 설명 |
| --- | --- | --- |
| 요구사항 -> 인수기준 | Pass | `REQ-001`~`REQ-006`이 `AC-001`~`AC-011`과 연결됨 |
| 인수기준 -> 기능/화면/프로그램 | Pass | 추적표에서 `FUNC`, `SCR`, `PGM` 연결 확인 |
| 프로그램 -> 테스트 | Pass | `UT-001`~`UT-011`, `IT-001`~`IT-005`, `PT-001` 연결 확인 |
| 화면 -> UI 증적 | Pass | `UI-001`~`UI-006`과 캡처 경로 연결 확인 |
| 보안항목 -> 검증 | Pass | `SEC-001`~`SEC-004`가 테스트 및 결과서와 연결됨 |
| 데이터 표준 | Open Issue | `ISSUE-004`가 Open 상태로 남아 있음 |

### 6.2 Adapter 계약 검증

| 계약 항목 | 결과 | 설명 |
| --- | --- | --- |
| Run Input Contract 적용성 | Pass | 샘플 산출물에서 관련 ID와 문서를 채워 넣을 수 있음 |
| Run Output Contract 적용성 | Pass | 검증 결과와 남은 이슈를 YAML 형식으로 정리 가능 |
| Gate Prompt 적용성 | Pass | Review Run 프롬프트로 코드 수정 없이 검증 가능 |
| Scope 통제 | Pass | writable을 Run 기록 문서로 제한해 리뷰만 수행 가능 |
| 민감문서 제외 | Pass | `docs/ref-docs/` 제외 조건 명시 |

## 7. Run 출력

```yaml
run_id: RUN-001
adapter: codex-gpt
status: CompletedWithIssues
summary:
  ko: "로그인 게시판 샘플의 요구사항-설계-구현-테스트-화면증적 연결을 Codex/GPT Adapter 계약 기준으로 리뷰했다. G4 검증 흐름은 재현 가능하지만 데이터 표준 검토 이슈가 남아 있어 G5 승인 후보로는 아직 완료 상태가 아니다."
  changed_behavior: []

changed_files:
  - path: docs/examples/board-with-login/runs/RUN-001_review-traceability_v0.1.md
    change_type: added
    related_ids: [RUN-001]

related_ids:
  req: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006]
  ac: [AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011]
  func: [FUNC-001, FUNC-002, FUNC-003, FUNC-004, FUNC-005, FUNC-006]
  scr: [SCR-001, SCR-002, SCR-003, SCR-004, SCR-005, SCR-006]
  pgm: [PGM-001, PGM-002, PGM-003, PGM-004, PGM-005, PGM-006]
  db: [DB-001, DB-002]
  sec: [SEC-001, SEC-002, SEC-003, SEC-004]
  test: [UT-001, UT-002, UT-003, UT-004, UT-005, UT-006, UT-007, UT-008, UT-009, UT-010, UT-011, IT-001, IT-002, IT-003, IT-004, IT-005, PT-001, UI-001, UI-002, UI-003, UI-004, UI-005, UI-006]

verification_results:
  - type: test
    command: "python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-*"
    result: passed
    summary: "20 passed in 8.10s"
  - type: lint
    command: "python -m ruff check ."
    result: passed
    summary: "All checks passed!"
  - type: evidence_check
    command: "Test-Path evidence/ui/SCR-001~SCR-006/desktop.png"
    result: passed
    summary: "6 UI evidence screenshots exist"

evidence:
  documents:
    - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md
    - docs/examples/board-with-login/DOC-QA-G4-003_UI-Test-Result_v0.1.md
    - docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  files:
    - docs/examples/board-with-login/evidence/ui/SCR-001_signup/desktop.png
    - docs/examples/board-with-login/evidence/ui/SCR-002_login/desktop.png
    - docs/examples/board-with-login/evidence/ui/SCR-003_posts/desktop.png
    - docs/examples/board-with-login/evidence/ui/SCR-004_detail/desktop.png
    - docs/examples/board-with-login/evidence/ui/SCR-005_new-post/desktop.png
    - docs/examples/board-with-login/evidence/ui/SCR-006_edit-post/desktop.png
  commit: null

traceability_updates:
  - document: docs/examples/board-with-login/runs/RUN-001_review-traceability_v0.1.md
    update: "Codex/GPT Adapter 입력/출력 계약 검증 결과 기록"

open_issues:
  - issue_id: ISSUE-004
    severity: Medium
    related_ids: [DB-001, DB-002]
    description: "공공데이터 공통표준 용어/단어/도메인 확인 및 프로젝트 신규어 승인 여부 결정이 남아 있다."
    impact: "G4 구현 검증은 가능하지만 G5 승인 또는 감리 제출 전 데이터 표준 검토 Run이 필요하다."

next_run_suggestion:
  run_id: RUN-002
  run_type: Review
  goal: "DB-001, DB-002 데이터 항목을 공공데이터 공통표준 및 프로젝트 단어사전 기준으로 검토하고 ISSUE-004를 닫을 수 있는지 판단한다."
  related_ids: [DB-001, DB-002, ISSUE-004]
```

## 8. 판정

`RUN-001` 테스트 결과, Codex/GPT Adapter의 입력/출력 계약은 로그인 게시판 샘플에 적용 가능하다.

다음 에이전트는 이 Run 문서와 관련 산출물만 보고 샘플의 상태를 이어받을 수 있다.

다만 `ISSUE-004`가 남아 있으므로 현재 샘플은 G4 검증 완료에 가깝지만 G5 승인 후보로는 아직 `CompletedWithIssues` 상태로 보는 것이 적절하다.

## 9. 다음 Run 후보

```yaml
run_id: RUN-002
adapter: codex-gpt
agent_role: review-agent
run_type: Review
gate: G4
goal: "프로젝트 단어사전과 DB명세의 데이터 표준 검토 상태를 확인하고 ISSUE-004 해소 방안을 정리한다."
related_ids:
  db: [DB-001, DB-002]
  issue: [ISSUE-004]
```
