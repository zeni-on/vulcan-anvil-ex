# RUN-010 Python hello API implementation plan

```yaml
run_id: RUN-010
gate: impl
persona: build-planning
adapter: codex-gpt
skill: implementation-plan
skill_path: docs/adapters/codex-gpt/skills/implementation-plan.md
profile: audit
run_type: Implementation
status: Completed
created_at: 2026-05-24
related_ids: [REQ-001-01, AC-001-01, AC-001-02, AC-002-01, FUNC-001, PGM-001, SEC-001, UT-001, IT-001, IT-002]
verification_results:
  - "python vulcan.py run-check docs/runs/RUN-010_python-hello-api-implementation-plan_v0.1.md: pending final rerun after Run output update"
evidence:
  - "docs/runs/RUN-010_python-hello-api-implementation-plan_v0.1.md"
  - "docs/runs/RUN-011_build-wave-BW-000_python-hello-api-scaffold-and-implementation_v0.1.md"
traceability_updates:
  - "BW-000/BW-001 implementation mapping defined; trace matrix final status update deferred until Orchestrator verifies worker outputs."
findings: []
change_requests: []
open_issues: []
gate_exit_summary: "Implementation Plan completed. Implementation remains in impl; no Gate transition requested."
approval_request: "No user approval needed for next Gate. Continue with active impl Build Wave sequence under prior Gate 3 approval."
```

## 1. Run 목표

Python hello API implementation plan

## 2. 에이전트가 먼저 읽을 문서

- `AGENTS.md`
- `session.json`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/adapters/codex-gpt/GATE_PROMPTS.md`
- `docs/adapters/codex-gpt/skills/implementation-plan.md`

나머지 기준 문서는 `source_documents.reference_on_demand`에 있을 때만 필요 시 참고한다.

## 3. Run 입력 계약

```yaml
profile: "audit"
adapter: "codex-gpt"
run_type: "Implementation"
gate: "impl"
related_ids: [REQ-001-01, AC-001-01, AC-001-02, AC-002-01, FUNC-001, PGM-001, SEC-001, UT-001, IT-001, IT-002]
target_contracts:
  req: [REQ-001-01]
  nreq: []
  ac: [AC-001-01, AC-001-02, AC-002-01]
  func: [FUNC-001]
  scr: []
  pgm: [PGM-001]
  api: [API-001]
  db: []
  sec: [SEC-001]
  test: [UT-001, IT-001, IT-002]
  ui: []
  other: []
persona: "build-planning"
source_documents:
  read_first:
    - "AGENTS.md"
    - "session.json"
    - "docs/core/TRACEABILITY_RULES.md"
    - "docs/adapters/codex-gpt/GATE_PROMPTS.md"
    - "docs/adapters/codex-gpt/skills/implementation-plan.md"
  working_documents:
    - "docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md"
    - "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"
    - "docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md"
    - "docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md"
    - "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md"
  reference_on_demand:
    - "docs/core/ID_SYSTEM.md"
    - "docs/core/ORCHESTRATOR_PROTOCOL.md"
    - "docs/core/AGENT_PERSONAS.md"
    - "docs/core/AGENT_RUN_PROTOCOL.md"
    - "docs/core/DELIVERY_PROFILES.md"
    - "docs/core/RUN_INPUT_CONTRACT.md"
    - "docs/core/RUN_OUTPUT_CONTRACT.md"
    - "docs/core/run-input-samples/impl-build-wave.sample.md"
  optional:
    []
scope:
  writable:
    - "docs/runs/"
    - "session.json"
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
  - "승인된 Gate 2/3 범위 안에서만 구현 또는 구현 계획을 작성한다."
  - "Implementation Plan은 feature 구현 Wave 전에 scaffold 필요 여부를 판단하고, 필요하면 BW-000 implementation-scaffold를 첫 Wave로 둔다."
  - "scaffold가 불필요하면 contract_skeleton.mode: not-required와 확인한 파일/명령 근거를 남긴다."
  - "작은 기능이라도 실제 코드/테스트/UI/API 구현은 Orchestrator 직접 구현이 아니라 worker Run 또는 agent-run --mode work로 수행한다."
  - "사용자가 worker 사용을 명시하지 않았다는 점은 Orchestrator 직접 구현 사유가 아니며, 구현 진행 승인이 있으면 별도 요청이 없어도 worker/subagent/agent-run 위임을 기본 절차로 둔다."
  - "직접 구현 예외는 worker/subagent/agent-run 실행 불가, worker 결과 통합 중 충돌 해결에 필요한 최소 수정, 긴급한 1~2줄 연결 수정, 사용자의 명시적 직접 구현 승인에 한해 허용한다."
  - "Orchestrator 직접 수정 예외가 있으면 orchestrator_direct_edit_reason, 수정 파일, 실행 검증, 후속 검수 필요 여부를 Run에 기록한다."
  - "화면 구현은 관련 SCR의 UI Implementation Contract와 Gate 3 UI 테스트 기준을 먼저 확인한다."
  - "Build Wave와 worker Run은 기능/계약 단위로 나뉘며 target_contracts의 FUNC/PGM/API/DB/SEC/TEST 묶음이 명확하다."
  - "Build Wave 범위, 소유 파일, 관련 ID, 검증 명령이 명확하다."
  - "시간 기준은 10분 내외/최대 15분 권장 보조 기준이며, 미완성 중간 구현을 완료 처리하지 않는다."
  - "구현 변경은 테스트 코드, 테스트 결과, 추적표 갱신 필요 항목과 연결되며, 추적표 Implemented/Verified 상태는 Orchestrator 재검증 후 반영한다."
  - "동시에 active 상태인 Build Wave가 하나만 유지된다."
  - "Build Wave 후보와 각 Wave의 소유 파일, 관련 ID, 검증 명령이 나뉘어 있다."
  - "화면 구현 Wave는 UI Implementation Contract 준수 체크와 screenshot 비교 증적 위치가 정의되어 있다."
  - "구현 착수 전 사용자 승인 또는 명시적인 진행 지시가 필요한 항목이 식별되어 있다."

verification:
  commands:
    - "python vulcan.py run-check docs/runs/RUN-010_python-hello-api-implementation-plan_v0.1.md"
    - "python vulcan.py check-trace"
    - "python vulcan.py sync-session"
  evidence:
    required: true
    target_documents:
      - "docs/runs/RUN-010_python-hello-api-implementation-plan_v0.1.md"
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
- `completion_criteria`를 모두 만족하도록 문서, 추적표, Run 기록을 갱신한다.
- Run은 현재 Gate와 related_ids 범위 안에서 완료 가능한 산출물 또는 검토 단위로 끝나야 한다.
- 실제 프로젝트 값으로 작성하고 placeholder를 완료 산출물에 남기지 않는다.
- 실행하거나 확인한 검증 명령과 결과를 Run 기록에 남긴다.


- UI 검증이 포함되면 `ui_evidence_policy`에 따라 상태/시나리오별 UI-ID와 증적 파일을 1:1로 연결한다.
- UIREF, 화면 퍼블리싱 산출물, 외부 시안이 있으면 `ui_implementation_contract_policy`에 따라 설계-구현-증적 비교 기준을 남긴다.
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

Gate 2/3 산출물 기준으로 신규 Python/FastAPI backend 골격이 없음을 확인했다. 따라서 첫 Wave는 `BW-000 implementation-scaffold`로 두고, 기능 완료는 후속 `BW-001 build-wave`에서 수행한다.

Build Wave 정의:

| BW-ID | 목적 | 관련 ID | 권장 runner | 상태 |
| --- | --- | --- | --- | --- |
| BW-000 | FastAPI app/router/service/test skeleton과 의존성 파일 생성, public signature 고정 | PGM-001, IF-001, MTH-001, MTH-002, API-001, UT-001, IT-001 | codex-cli worker | In Progress |
| BW-001 | `GET /hello`가 `200 text/plain` + `hello`를 반환하도록 구현하고 UT/IT 통과 | REQ-001-01, AC-001-01, AC-001-02, AC-002-01, FUNC-001, PGM-001, API-001, SEC-001, UT-001, IT-001, IT-002 | codex-cli worker | Planned |

Scaffold 판단:

```yaml
contract_skeleton:
  mode: required
  reason: "backend/ 디렉터리와 FastAPI public signature/test skeleton이 아직 없음"
```

중단 조건:

- worker가 `scope.writable` 밖 변경을 요구하는 경우
- API 응답을 JSON, DB, 인증, UI로 확장해야 하는 경우
- 의존성 설치 또는 pytest 실행이 환경 문제로 차단되어 구현 판정이 불가능한 경우

### 변경 파일

- `docs/runs/RUN-010_python-hello-api-implementation-plan_v0.1.md`
- `docs/runs/RUN-011_build-wave-BW-000_python-hello-api-scaffold-and-implementation_v0.1.md`

### 검증 결과

- Pending: `python vulcan.py run-check docs/runs/RUN-010_python-hello-api-implementation-plan_v0.1.md`
- Pending: `python vulcan.py check-trace`

### 후속 조치

- `BW-000` scaffold worker 실행 후 Orchestrator가 import/pytest smoke를 재실행한다.
- `BW-000` 완료 후 `BW-001` feature implementation worker Run을 생성해 실제 `hello` 응답 계약을 닫는다.
