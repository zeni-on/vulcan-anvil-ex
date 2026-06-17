# RUN-001 Build Wave BW-001 - SCN-001~003 TODO product slice implementation

```yaml
run_id: RUN-001
gate: impl
persona: build
adapter: codex-gpt
skill: build-wave
skill_path: .agents/skills/vulcan-impl-wave/SKILL.md
profile: product
bw_id: BW-001
run_type: Implementation
status: Verified
created_at: 2026-06-16
related_ids: [SCN-001, SCN-002, SCN-003, REQ-001, REQ-002, REQ-003, API-001, API-002, API-003, API-004, DATA-001, UI-001, REG-001, REG-002, EV-001, EV-002, EV-003]
trace_context:
  seeds: [SCN-001]
  depth: 2
  direction: "both"
  source: "trace-context"
target_contracts:
  scenario: [SCN-001, SCN-002, SCN-003]
  req: [REQ-001, REQ-002, REQ-003]
  api: [API-001, API-002, API-003, API-004]
  data: [DATA-001]
  ui: [UI-001]
  regression: [REG-001, REG-002]
  test: []
  other: [EV-001, EV-002, EV-003]
  interface_contract:
    language: "Product profile stack/runtime is defined in PRODUCT_ARCHITECTURE and PRODUCT_CONTRACTS."
    signatures:
      - "Implement only the scenarios in target_contracts.scenario using the API/UI/DATA contracts listed in target_contracts."
    schemas:
      - "Use PRODUCT_CONTRACTS API/data tables as the public request, response, and persistence shape."
    error_contracts:
      - "Use PRODUCT_CONTRACTS accepted error/validation behavior; if missing, report an open issue instead of inventing a new public contract."
runner_role: worker-runner
source_documents:
  read_first:
    - "AGENTS.md"
    - "session.json"
    - "docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
    - ".agents/skills/vulcan-impl-wave/SKILL.md"
  working_documents:
    - "docs/product/PRODUCT_BRIEF.md"
    - "docs/product/PRODUCT_ARCHITECTURE.md"
    - "docs/product/PRODUCT_CONTRACTS.md"
    - "docs/product/PRODUCT_TRACEABILITY.md"
    - "docs/product/REGRESSION_AND_RELEASE_REPORT.md"
  reference_on_demand:
    - "docs/core/DELIVERY_PROFILES.md"
    - "docs/core/TECH_STACK_BASELINES.md"
orchestrator_reference:
  - "docs/core/AGENT_RUN_PROTOCOL.md"
  - "docs/core/RUN_INPUT_CONTRACT.md"
  - "docs/core/RUN_OUTPUT_CONTRACT.md"
scope:
  writable:
    - "docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
    - "app/"
    - "src/"
    - "backend/"
    - "frontend/"
    - "static/"
    - "tests/"
    - "requirements.txt"
    - "pyproject.toml"
    - "package.json"
    - "package-lock.json"
    - "README.md"
    - "docs/product/PRODUCT_TRACEABILITY.md"
    - "docs/product/evidence/"
  readonly:
    - "docs/core/"
    - "docs/templates/"
    - "docs/product/PRODUCT_BRIEF.md"
    - "docs/product/PRODUCT_ARCHITECTURE.md"
    - "docs/product/PRODUCT_CONTRACTS.md"
    - "docs/product/REGRESSION_AND_RELEASE_REPORT.md"
  excluded:
    - "docs/ref-docs/"
    - "**/*.db"
    - "**/__pycache__/"
    - "**/.ruff_cache/"
    - "**/node_modules/"
    - "**/.next/"
worker_execution_policy:
  forbidden_actions:
    - "Gate 전환을 수행하지 않는다."
    - "session.json의 current_gate, gate_status, completed를 직접 변경하지 않는다."
    - "사용자 승인, QA Pass, 릴리즈 승인, merge 가능 여부를 최종 확정하지 않는다."
    - "scope.writable 밖 파일을 수정하지 않는다."
  required_outputs:
    - "수행한 변경과 검증 결과를 Run 결과에 남긴다."
    - "wave-complete, Gate 전환, session 변경, 최종 승인 판단이 필요하면 Orchestrator 결정 필요 항목으로 반환한다."
  completion_rules:
    - "이 Run의 target_contracts.scenario만 완결한다."
    - "빌드 또는 담당 테스트가 깨진 상태를 완료로 보고하지 않는다."
dependency_install_policy:
  worker_cache_required: true
  npm_cache_env: "npm_config_cache"
  playwright_cache_env: "PLAYWRIGHT_BROWSERS_PATH"
  if_install_blocked: "dependency install이 권한, 인증, 네트워크, registry, cache 문제로 막히면 코드 실패로 단정하지 않고 environment_blocked 또는 not_run으로 보고한다."
development_standards_applied:
  - standard_id: "PRODUCT-LOG-001"
    source: "docs/product/PRODUCT_CONTRACTS.md"
    rule: "사용자 입력, 내부 오류, 저장소 경로, stack trace를 화면이나 공개 응답에 노출하지 않는다."
  - standard_id: "PRODUCT-TEST-001"
    source: "docs/product/REGRESSION_AND_RELEASE_REPORT.md"
    rule: "테스트는 어떤 시나리오와 기대 결과를 검증하는지 사람이 읽을 수 있게 남긴다."
development_standard_checklist:
  logging:
    required: true
    targets:
      - "API handler"
      - "Service or state handler"
    rule: "표준 logger 또는 최소 오류 처리 흐름을 사용하고 민감정보를 로그/화면에 남기지 않는다."
  comments:
    required: true
    targets:
      - "public API handler"
      - "core state mutation function"
    rule: "핵심 책임과 관련 scenario/API/DATA ID를 짧은 주석 또는 docstring으로 남긴다."
  tests:
    required: true
    targets:
      - "scenario smoke"
      - "unit or integration test"
    rule: "테스트 이름이나 설명에 입력값, 기대값, 관련 SCN/REG ID를 남긴다."
verification:
  commands:
    - "python -m compileall app"
    - "python -m pytest tests -q"
    - "python vulcan.py run-check docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
    - "python vulcan.py run-preflight docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
  evidence:
    required: true
    target_documents:
      - "docs/product/PRODUCT_TRACEABILITY.md"
      - "docs/product/evidence/"
verification_results:
  - command: "python -m compileall app"
    result: "pass"
    evidence: "docs/product/evidence/BW-001_compileall.log"
  - command: "python -m pytest tests -q"
    result: "pass"
    evidence: "docs/product/evidence/BW-001_pytest.log"
  - command: "python vulcan.py run-check docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
    result: "pass"
    evidence: "docs/product/evidence/BW-001_run_check.log"
  - command: "python vulcan.py run-preflight docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
    result: "pass"
    evidence: "docs/product/evidence/BW-001_run_preflight.log"
evidence:
  - "docs/product/evidence/BW-001_compileall.log"
  - "docs/product/evidence/BW-001_pytest.log"
  - "docs/product/evidence/BW-001_run_check.log"
  - "docs/product/evidence/BW-001_run_preflight.log"
delegation_records:
  - mode: "orchestrator-local-smoke"
    delegate: "Codex Orchestrator"
    task: "SCN-001~003 Product TODO slice 구현 및 self-check"
    status: "completed"
    changed_files:
      - "app/main.py"
      - "static/index.html"
      - "static/styles.css"
      - "static/app.js"
      - "tests/test_todos.py"
      - "requirements.txt"
    result_summary: "FastAPI/SQLite/static UI 구현 및 pytest 4 passed"
    orchestrator_verification:
      - "python -m compileall app"
      - "python -m pytest tests -q"
      - "python vulcan.py run-check docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
      - "python vulcan.py run-preflight docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md"
traceability_updates:
  - "PRODUCT_TRACEABILITY.md Implementation 칸을 BW-001 구현 파일로 갱신"
findings: []
change_requests: []
open_issues: []
```

## 1. Wave 목표

SCN-001~003 TODO product slice implementation

## 2. Product 구현 범위

- 기준 시나리오: [SCN-001, SCN-002, SCN-003]
- 관련 요구/계약: [SCN-001, SCN-002, SCN-003, REQ-001, REQ-002, REQ-003, API-001, API-002, API-003, API-004, DATA-001, UI-001, REG-001, REG-002, EV-001, EV-002, EV-003]
- Product profile은 audit 산출물 대신 `docs/product/` 문서 세트를 기준으로 구현한다.

## 3. 작업자 입력 계약

- 먼저 `source_documents.read_first`를 읽고 `BW-001` 범위와 관련 ID를 확인한다.
- `source_documents.working_documents`의 Product Brief, Architecture, Contracts, Traceability, Regression 문서를 구현 기준으로 삼는다.
- `target_contracts.scenario`, `api`, `data`, `ui`, `regression`에 없는 기능은 추가하지 않는다.
- `target_contracts.interface_contract`는 세부 class 설계가 아니라 Product 계약 경계다. public API/data/UI shape가 충돌하면 임의 변경하지 말고 `open_issues`로 보고한다.
- `scope.writable` 안에서만 코드, 테스트, 자기 Run, Product Trace/evidence를 수정한다.
- 전체 QA Pass, 릴리즈 가능 여부, Gate 전환은 Orchestrator가 판단한다.

## 4. Orchestrator 지시

- 실제 구현은 native worker(subagent/thread/native branch agent)가 수행한다.
- Orchestrator는 worker 결과의 diff/scope를 확인하고, 관련 테스트를 재실행한 뒤 `wave-complete BW-001` 여부를 판단한다.
- `agent-run`/`run-exec`는 외부 CLI 실행 증적이나 worktree/watchdog이 필요할 때만 선택한다.

## 5. 검증 계획

- worker는 가능한 self-check만 실행하고, 실패/미실행 명령은 이유를 남긴다.
- Orchestrator는 worker가 작성한 테스트와 가능한 build/smoke를 재실행한다.
- Gate 4의 공식 UI/E2E 증적과 릴리즈 판정은 이 Run 완료 조건이 아니다.

## 6. 결과 기록

### 변경 파일

- `requirements.txt`
- `app/__init__.py`
- `app/main.py`
- `static/index.html`
- `static/styles.css`
- `static/app.js`
- `tests/test_todos.py`
- `docs/product/PRODUCT_TRACEABILITY.md`
- `docs/product/evidence/BW-001_*.log`

### 검증 결과

- `python -m compileall app` 통과
- `python -m pytest tests -q` 통과: 4 passed
- `python vulcan.py run-check docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md` 통과
- `python vulcan.py run-preflight docs/runs/RUN-001_build-wave-BW-001_scn-001-003-todo-product-slice-implementation_v0.1.md` 통과

### 위임 기록

- v0.4.8 Product profile smoke replay 목적의 Orchestrator local implementation으로 수행했다.
- 실제 운영에서는 native worker/subagent/thread 또는 Agy branch agent 위임 후 `delegation_records`를 기록하는 흐름을 우선한다.

### 후속 조치

- Gate 4에서 REG-002 UI smoke 또는 Playwright 증적을 별도로 수행한다.
- Product `wave-start --trace-seed SCN-001`이 SCN-002/003의 REQ/API/EV를 충분히 확장하지 못해 Run 계약을 수동 보정했다. Ex 프레임워크 보강 후보로 기록한다.
