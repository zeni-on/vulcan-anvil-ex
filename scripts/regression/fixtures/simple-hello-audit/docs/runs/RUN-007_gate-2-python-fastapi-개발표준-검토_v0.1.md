# RUN-007 Gate 2 Python FastAPI 개발표준 검토

```yaml
run_id: RUN-007
gate: gate2
persona: development-review
adapter: codex-gpt
skill: development-standard-review
skill_path: docs/adapters/codex-gpt/skills/development-standard-review.md
profile: audit
run_type: Design
status: Completed
created_at: 2026-05-24
related_ids: [NREQ-001, PGM-001, API-001, SEC-001]
verification_results:
  - command: "document review"
    result: "passed; Python/FastAPI standard defines structure, commands, security, tests, and N/A Java/DB criteria"
evidence:
  - docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md
  - docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md
traceability_updates:
  - "NREQ-001 -> Development Standard -> pytest/API command verification candidates"
findings: []
change_requests: []
open_issues: []
gate_exit_summary:
  status: "Completed"
  summary: "Development standard review passed for Python/FastAPI hello API scope."
approval_request: "Gate 2 전체 설계 승인 시 Gate 3 테스트 설계로 진행한다."
```

## 1. Run 목표

Gate 2 Python FastAPI 개발표준 검토

## 2. 에이전트가 먼저 읽을 문서

- `AGENTS.md`
- `session.json`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/adapters/codex-gpt/GATE_PROMPTS.md`
- `docs/core/GATE2_DESIGN_SEQUENCE.md`
- `docs/adapters/codex-gpt/skills/development-standard-review.md`

나머지 기준 문서는 `source_documents.reference_on_demand`에 있을 때만 필요 시 참고한다.

## 3. Run 입력 계약

```yaml
profile: "audit"
adapter: "codex-gpt"
run_type: "Design"
gate: "gate2"
related_ids: [NREQ-001, PGM-001, API-001, SEC-001]
target_contracts:
  req: []
  nreq: [NREQ-001]
  ac: []
  func: []
  scr: []
  pgm: [PGM-001]
  api: [API-001]
  db: []
  sec: [SEC-001]
  test: []
  ui: []
  other: []
persona: "development-review"
source_documents:
  read_first:
    - "AGENTS.md"
    - "session.json"
    - "docs/core/TRACEABILITY_RULES.md"
    - "docs/adapters/codex-gpt/GATE_PROMPTS.md"
    - "docs/core/GATE2_DESIGN_SEQUENCE.md"
    - "docs/adapters/codex-gpt/skills/development-standard-review.md"
  working_documents:
    - "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md"
    - "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"
  reference_on_demand:
    - "docs/core/ID_SYSTEM.md"
    - "docs/core/ORCHESTRATOR_PROTOCOL.md"
    - "docs/core/AGENT_PERSONAS.md"
    - "docs/core/AGENT_RUN_PROTOCOL.md"
    - "docs/core/DELIVERY_PROFILES.md"
    - "docs/core/RUN_INPUT_CONTRACT.md"
    - "docs/core/RUN_OUTPUT_CONTRACT.md"
    - "docs/core/run-input-samples/gate2-design-review.sample.md"
    - "docs/core/run-input-samples/gate2-development-standard-review.sample.md"
    - "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md"
    - "docs/core/TECH_STACK_BASELINES.md"
    - "docs/core/SECURITY_BASELINE.md"
    - "docs/templates/DEVELOPMENT_STANDARD_TEMPLATE.md"
    - "docs/artifacts/02-design/architecture/DOC-ARCH-G2-001_SW-Architecture_v0.1.md"
    - "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md"
    - "docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md"
    - "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md"
  optional:
    []
design_sequence:
  - "G2-01 Kickoff / 설계 범위 고정: Gate 1 요구사항, AC, 미결 질문, 보류 항목을 확인한다."
  - "G2-02 SW Architecture Draft: 전체 구조, 주요 CNT, ADR 후보, 보안/데이터/배포 경계, Pending을 먼저 잡는다."
  - "G2-03 Screen / User Flow: SCR, UIREF, 화면 상태, 메시지 위치, 사용자 흐름을 확정한다."
  - "G2-04 Function Spec: 화면과 요구사항을 FUNC, 기능 흐름, 예외 흐름으로 전개한다."
  - "G2-05 Program Design / API Spec: FUNC를 PGM, 컴포넌트, 인터페이스, public method contract, API, DTO, 오류코드로 내린다."
  - "G2-06 Data / DB Spec: TERM, WORD, DOMAIN, DB, ERD/DBML, 제약조건을 확정한다."
  - "G2-07 Security Guide: SEC별 정책값, 적용 위치, 오류 메시지, 검증 후보를 확정한다."
  - "G2-08 Development Standard: 패키지 구조, 레이어 규칙, DTO/Entity, 빌드/테스트 명령을 확정한다."
  - "G2-09 SW Architecture Baseline 보강: 상세 설계 결정을 CMP, FLOW, 품질속성, ADR 상태로 되돌려 반영한다."
  - "G2-10 Design Review / Gate 3 승인 대기: 설계 검수 결과, FIND/ISSUE/CR, Gate 3 승인 질문을 남긴다."
scope:
  writable:
    - "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md"
    - "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"
    - "docs/runs/"
  readonly:
    - "docs/core/"
    - "docs/templates/"
    - "docs/seed-docs/reference-standards/"
  excluded:
    - "docs/ref-docs/"
    - "**/*.db"
    - "**/__pycache__/"
    - "**/.ruff_cache/"
completion_criteria:
  - "언어, 런타임, 프레임워크, DB, 빌드, 테스트 도구와 선택 근거가 작성되어 있다."
  - "TECH_STACK_BASELINES.md 중 어떤 기준을 준용하고 어떤 점을 프로젝트에 맞게 조정했는지 기록되어 있다."
  - "패키지 구조, 계층 책임, 금지 의존성, DTO/Entity 분리, 트랜잭션 기준이 구현자가 따를 수 있을 만큼 구체적이다."
  - "메시지, 예외, 로그, 설정값, 외부 의존성, 주석/추적 ID 표기 규칙이 있다."
  - "보안 구현 기준이 SECURITY_BASELINE과 SEC-ID에 연결되어 있다."
  - "필수 검증 명령과 증적 위치가 Gate 3/구현 단계로 전달 가능하다."

verification:
  commands:
    - "python vulcan.py run-check docs/runs/RUN-007_gate-2-python-fastapi-개발표준-검토_v0.1.md"
    - "python vulcan.py check-trace"
  evidence:
    required: true
    target_documents:
      - "docs/runs/RUN-007_gate-2-python-fastapi-개발표준-검토_v0.1.md"
      - "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"

output_requirements:
  format: "RUN_OUTPUT_CONTRACT.md"
  include:
    - "changed_files"
    - "related_ids"
    - "verification_results"
    - "evidence"
    - "traceability_updates"
    - "gate_exit_summary"
    - "approval_request"
    - "open_issues"
    - "next_run_suggestion"
```

## 4. 수행 지시

- `source_documents.read_first`만 먼저 읽고 현재 Gate, skill, 관련 ID를 확인한다.



- `source_documents.working_documents`를 중심으로 실제 산출물을 작성하거나 검토한다.
- `source_documents.reference_on_demand`는 기준 충돌, 작성 규칙 확인, 상세 판단이 필요할 때만 참고한다.
- 전역 memory, 과거 세션 요약, 다른 샘플 프로젝트 기억은 현재 Run의 근거로 사용하지 않는다.
- `scope.writable` 안에서만 산출물을 수정한다.
   - Gate 2 Run이면 `design_sequence`에서 현재 위치를 확인하고, 필요한 이전 단계 누락과 다음 Gate 2 Run 제안을 기록한다.
- `completion_criteria`를 모두 만족하도록 문서, 추적표, Run 기록을 갱신한다.
- Run은 현재 Gate와 related_ids 범위 안에서 완료 가능한 산출물 또는 검토 단위로 끝나야 한다.
- 실제 프로젝트 값으로 작성하고 placeholder를 완료 산출물에 남기지 않는다.
- 실행하거나 확인한 검증 명령과 결과를 Run 기록에 남긴다.


- subagent, CLI, 별도 worktree에서 작업자 runner로 실행 중이면 `worker_execution_policy`를 따른다.
- 기준 충돌, 범위 초과, 도메인 정보 부족은 임의로 통과시키지 말고 `open_issues`에 남기거나 사용자에게 질문한다.
- Gate 산출물 완료 후에는 다음 Gate로 진행하지 말고 사용자 승인 질문을 남긴 뒤 대기한다.

## 5. Gate 종료 및 승인 대기

Run을 완료할 때 다음 항목을 반드시 남긴다.

| 항목 | 작성 기준 |
| --- | --- |
| 현재 Gate 산출물 요약 | 이번 Gate에서 작성/수정한 산출물과 관련 ID |
| 미해결 항목 | `open_issues`, `findings`, `change_requests` |
| 다음 Gate 제안 | 다음 Gate에서 수행할 Run 후보 |
| 사용자 승인 질문 | "다음 Gate로 진행해도 되는지"를 명시적으로 질문 |
| 승인 증적 | 대화에서 사용자가 명시 승인한 문구 또는 승인 보류 사유 |

사용자 승인 전에는 다음 Gate 산출물 작성, 구현 착수, QA Pass, Gate 5 승인 선언을 하지 않는다.

## 6. 완료 보고

### 요약

개발표준은 Python/FastAPI, Router -> Service 구조, pytest/TestClient, 로컬 실행 명령, 보안/로그 기준을 포함한다. DB Pool과 Lombok은 Python/DB 제외 범위로 N/A 처리했다.

### 변경 파일

- docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md

### 검증 결과

- document review: passed

### 후속 조치

Gate 3에서 개발표준의 필수 명령을 UT/IT/QA 명령으로 전개한다.
