# RUN-002 데이터 표준 검토

```yaml
---
run_id: RUN-002
title: Review Data Standard
title_ko: 로그인 게시판 샘플 데이터 표준 검토
project: Board With Login Sample
adapter: codex-gpt
agent_adapter: codex-gpt
persona: review
skill: data-standard-review
agent_role: review-agent
gate: G4
status: Completed
created_at: 2026-05-07
updated_at: 2026-05-07
input_contract: docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md
output_contract: docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
related_ids:
  db: [DB-001, DB-002]
  data: [TERM-002, TERM-003, TERM-004, TERM-006, TERM-007, TERM-008, TERM-009, TERM-010]
  issue: [ISSUE-004, ISSUE-007]
verification_results:
  - command: "python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-*"
    result: passed
  - command: "python -m ruff check ."
    result: passed
evidence:
  - docs/examples/board-with-login/DOC-DATA-G2-001_Project-Glossary_v0.1.md
  - docs/examples/board-with-login/DOC-DATA-G2-002_Database-Spec_v0.1.md
traceability_updates:
  - docs/examples/board-with-login/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
open_issues:
  - ISSUE-008
---
```

## 1. Run 목적

`RUN-001`에서 남긴 `ISSUE-004`를 해소하기 위해 로그인 게시판 샘플의 프로젝트 단어사전과 DB명세를 공공데이터 공통표준(2025.11월) 기준으로 검토한다.

검토 대상은 다음이다.

| 대상 | 문서 |
| --- | --- |
| 프로젝트 단어사전 | `DOC-DATA-G2-001_Project-Glossary_v0.1.md` |
| DB명세서 | `DOC-DATA-G2-002_Database-Spec_v0.1.md` |
| 공통 규칙 | `docs/core/DATA_STANDARD_RULES.md`, `docs/core/REFERENCE_STANDARDS.md` |
| 참조 표준 | `docs/seed-docs/reference-standards/공공데이터 공통표준(2025.11월).xlsx` |

## 2. Run 입력

```yaml
run:
  run_id: RUN-002
  adapter: codex-gpt
  persona: review
  skill: data-standard-review
  role: review-agent
  gate: G4
  objective: "DB-001, DB-002 데이터 항목을 공공데이터 공통표준과 대조하고 ISSUE-004를 해소할 수 있는지 판단한다."
  scope:
    writable:
      - docs/examples/board-with-login/DOC-DATA-G2-001_Project-Glossary_v0.1.md
      - docs/examples/board-with-login/DOC-DATA-G2-002_Database-Spec_v0.1.md
      - docs/examples/board-with-login/runs/RUN-002_review-data-standard_v0.1.md
    readonly:
      - docs/core/DATA_STANDARD_RULES.md
      - docs/core/REFERENCE_STANDARDS.md
      - docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md
      - docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
      - docs/seed-docs/reference-standards/공공데이터 공통표준(2025.11월).xlsx
  prohibited:
    - 표준 원문 내용을 산출물에 과도하게 복사하지 않는다.
    - 민감 참조 문서를 Git 추적 대상에 포함하지 않는다.
```

## 3. 검토 기준

| 기준 | 확인 내용 |
| --- | --- |
| 표준 용어 대조 | 동일하거나 직접 적용 가능한 공통표준 용어가 있는지 확인 |
| 표준 약어 대조 | DB 컬럼 약어가 표준 약어와 일치하거나 의도적으로 변형되었는지 확인 |
| 도메인 대조 | 데이터 타입, 길이, 표현 형식이 표준 도메인 또는 프로젝트 도메인으로 설명되는지 확인 |
| 프로젝트신규 사유 | 표준에 직접 맞추기 어려운 항목의 등록 사유가 남아 있는지 확인 |
| 구현 정합성 | DB명세의 타입/길이가 샘플 앱 모델과 충돌하지 않는지 확인 |

## 4. 공공데이터 공통표준 대조 결과

| TERM-ID | 기존 항목 | 검토 결과 | 적용 판단 |
| --- | --- | --- | --- |
| TERM-002 | 이메일 | 공통표준 이메일주소 계열 용어가 존재한다. | `이메일주소`, `EML_ADDR` 기준으로 준용하고 물리 컬럼 `email`은 구현 관례로 유지 |
| TERM-003 | 비밀번호해시값 | 공통표준 사용자암호화비밀번호 계열 용어가 존재한다. | `사용자암호화비밀번호`, `USER_ENPSWD`를 준용하되 구현 컬럼 `password_hash`는 해시 저장 의미를 위해 유지 |
| TERM-004 | 사용자명 | 공통표준 `사용자명`, `USER_NM`, `명V100`이 존재한다. | 준용 |
| TERM-006 | 게시글제목 | 공통표준 `게시물제목`, `PST_TTL`, `명V256`이 존재한다. | 용어/약어는 준용, 샘플 구현 길이 200자는 변형으로 기록 |
| TERM-007 | 게시글내용 | 공통표준 `게시물내용`, `PST_CN`, `내용V4000`이 존재한다. | 준용 |
| TERM-008 | 작성자 | 공통표준 작성자명/사용자아이디 계열은 존재하나 샘플 컬럼은 FK 내부 ID이다. | `작성자아이디`를 프로젝트신규로 등록 |
| TERM-009 | 작성일시 | 공통표준 `작성일시`, `WRT_DT`, `연월일시분초D`가 존재한다. | 준용, 구현 컬럼 `created_at`은 개발 표준 네이밍으로 유지 |
| TERM-010 | 수정일시 | 공통표준 `수정일시`, `MDFCN_DT`, `연월일시분초D`가 존재한다. | 준용, 구현 컬럼 `updated_at`은 개발 표준 네이밍으로 유지 |

## 5. 반영 내용

| 문서 | 반영 내용 |
| --- | --- |
| `DOC-DATA-G2-001_Project-Glossary_v0.1.md` | 버전 `v0.2`로 갱신, 표준 준용/변형/프로젝트신규 상태 반영, `ISSUE-007` Closed 처리 |
| `DOC-DATA-G2-002_Database-Spec_v0.1.md` | 버전 `v0.2`로 갱신, DB 컬럼 논리명/도메인/데이터 표준 검토표 갱신 |

## 6. 검증 결과

| 검증 | 명령/방법 | 결과 | 근거 |
| --- | --- | --- | --- |
| 표준 엑셀 구조 확인 | `openpyxl`로 시트 확인 | Passed | `공통표준용어`, `공통표준단어`, `공통표준도메인` 시트 확인 |
| 표준 용어 검색 | `openpyxl`로 대상 용어 검색 | Passed | 이메일주소, 사용자명, 게시물제목, 게시물내용, 작성일시, 수정일시 등 대조 |
| 미확정 상태 제거 | `rg -n "확인필요" ...` | Passed | 데이터 문서 내 `확인필요` 없음 |
| 자동 테스트 | `python -m pytest tests -p no:cacheprovider --ignore pytest-cache-files-*` | Passed | `20 passed in 8.71s` |
| 정적 검사 | `python -m ruff check .` | Passed | `All checks passed!` |

## 7. Run 출력

```yaml
run_output:
  run_id: RUN-002
  status: Completed
  changed_files:
    - docs/examples/board-with-login/DOC-DATA-G2-001_Project-Glossary_v0.1.md
    - docs/examples/board-with-login/DOC-DATA-G2-002_Database-Spec_v0.1.md
    - docs/examples/board-with-login/runs/RUN-002_review-data-standard_v0.1.md
  resolved_issues:
    - issue_id: ISSUE-004
      resolution: "공공데이터 공통표준 대조 결과를 프로젝트 단어사전과 DB명세에 반영했다."
    - issue_id: ISSUE-007
      resolution: "단어사전 내 표준 용어 확인 필요 항목을 준용/변형/프로젝트신규로 분류하고 Closed 처리했다."
  remaining_issues:
    - issue_id: ISSUE-008
      severity: Low
      description: "API 필드명과 DB 컬럼명 간 네이밍 규칙은 개발 표준 문서에서 별도 확정할 수 있다."
  verification_results:
    - type: data-standard-review
      status: Passed
      summary: "공통표준용어/단어/도메인 시트를 기준으로 주요 DB 항목을 대조했다."
    - type: tests
      status: Passed
      summary: "20 passed in 8.71s"
    - type: lint
      status: Passed
      summary: "All checks passed!"
  next_run_suggestion:
    run_id: RUN-003
    type: implementation-or-adapter
    goal: "Codex/GPT 어댑터 Run 계약을 vulcan.py init 또는 실행 흐름에 연결할지 검토한다."
```

## 8. 판정

`ISSUE-004`는 해소 가능하며, 이번 Run에서 실제 문서에 반영했다.

현재 샘플은 요구사항-설계-구현-테스트-화면증적-데이터표준 검토까지 연결되었으므로 G4 검증 산출물 샘플로 사용할 수 있다. 다만 `ISSUE-008`은 API 필드명과 DB 컬럼명 사이의 네이밍 정책을 개발 표준 문서에서 더 명확히 할 때 함께 정리하는 것이 좋다.

## 9. 후속 Run 초안

```yaml
run_id: RUN-003
title: Connect Adapter Contract To Vulcan Flow
goal: "현재 작성한 Run 계약과 샘플 산출물을 vulcan.py init 또는 단계별 실행 흐름에 어떻게 연결할지 검토한다."
scope:
  docs:
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/adapters/codex-gpt/
  implementation:
    - vulcan.py
```
