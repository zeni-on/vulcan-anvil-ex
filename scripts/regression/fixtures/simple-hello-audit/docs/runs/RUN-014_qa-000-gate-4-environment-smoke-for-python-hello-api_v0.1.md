# RUN-014 QA-000 Gate 4 environment smoke for Python hello API

```yaml
run_id: RUN-014
gate: gate4
persona: evidence
adapter: codex-gpt
skill: qa-execution
skill_path: docs/adapters/codex-gpt/skills/qa-execution.md
profile: audit
run_type: Evidence
status: Completed
created_at: 2026-05-24
related_ids: [REQ-001-01, AC-001-01, AC-001-02, AC-002-01, FUNC-001, PGM-001, API-001, SEC-001, UT-001, IT-001, IT-002]
verification_results:
  - id: QA-000-GIT
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-git-status.log
  - id: QA-000-PY
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-python-version.log
  - id: QA-000-PIP
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pip-check.log
  - id: QA-000-DEPS
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pip-install.log
  - id: QA-000-COLLECT
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pytest-collect.log
  - id: QA-000-PORT
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-port-8000.log
  - id: QA-000-STARTUP
    result: passed
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-uvicorn-startup-smoke.log
  - id: QA-000-FE-PW
    result: skipped
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-frontend-playwright-applicability.log
  - id: QA-000-DB
    result: skipped
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-db-applicability.log
evidence:
  - docs/artifacts/04-review/evidence/qa-000/
  - docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md
  - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
traceability_updates:
  - document: docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
    update: QA-000 environment smoke results recorded for REQ-001-01, UT-001, IT-001, IT-002
    owner: orchestrator
gate_exit_summary:
  status: worker_completed
  summary: QA-000 environment smoke completed; Gate 4 completion not decided by worker
approval_request:
  pending: false
  question: null
  approval_recorded: false
  note: QA worker returns result to Orchestrator and does not request user approval directly
findings: []
change_requests: []
open_issues: []
```

## 1. Run 목표

QA-000 Gate 4 environment smoke for Python hello API

## 2. 에이전트가 먼저 읽을 문서

- `AGENTS.md`
- `session.json`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/adapters/codex-gpt/GATE_PROMPTS.md`
- `docs/adapters/codex-gpt/skills/qa-execution.md`

나머지 기준 문서는 `source_documents.reference_on_demand`에 있을 때만 필요 시 참고한다.

## 3. Run 입력 계약

```yaml
profile: "audit"
adapter: "codex-gpt"
run_type: "Evidence"
gate: "gate4"
related_ids: [REQ-001-01, AC-001-01, AC-001-02, AC-002-01, FUNC-001, PGM-001, API-001, SEC-001, UT-001, IT-001, IT-002]
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
persona: "evidence"
source_documents:
  read_first:
    - "AGENTS.md"
    - "session.json"
    - "docs/core/TRACEABILITY_RULES.md"
    - "docs/adapters/codex-gpt/GATE_PROMPTS.md"
    - "docs/adapters/codex-gpt/skills/qa-execution.md"
  working_documents:
    - "docs/runs/RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"
    - "docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md"
    - "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md"
  reference_on_demand:
    - "docs/core/ID_SYSTEM.md"
    - "docs/core/ORCHESTRATOR_PROTOCOL.md"
    - "docs/core/AGENT_PERSONAS.md"
    - "docs/core/AGENT_RUN_PROTOCOL.md"
    - "docs/core/DELIVERY_PROFILES.md"
    - "docs/core/RUN_INPUT_CONTRACT.md"
    - "docs/core/RUN_OUTPUT_CONTRACT.md"
    - "docs/core/run-input-samples/gate4-qa-review.sample.md"
    - "docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md"
    - "docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md"
  optional:
    []
scope:
  writable:
    - "docs/runs/RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"
    - "docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md"
    - "docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md"
    - "docs/artifacts/04-review/evidence/"
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
  - "Gate 4 전체 QA를 한 번에 수행하지 않는다. QA-000 환경 준비, QA-001 명령 검증, QA-002 UI/E2E 증적, QA-003 결과 정리 중 현재 Run 범위를 명시한다."
  - "QA-000에서 통합된 소스, 의존성, 실행 포트, DB/환경변수, Playwright 설치 상태를 먼저 확인하고 차단되면 이후 QA 실행을 진행하지 않는다."
  - "Gate 3 테스트케이스와 개발표준정의서의 필수 검증 명령을 실행하거나 Not Run/environment_blocked로 사유를 기록한다."
  - "각 검증 결과에는 cwd, command, exit code, success criteria, result, log/evidence path가 있다."
  - "Playwright 화면 검증은 상태/시나리오별 UI-ID와 screenshot/log/trace 증적을 1:1로 연결한다."
  - "실패나 이상 동작은 즉시 수정하지 않고 원인 가설, 재현 명령, 영향 ID, 후보 FIND/CR/ISSUE를 기록한다."
  - "새 API, 새 메소드, 요구사항/설계 변경이 필요해 보이면 코드를 만들지 않고 CR 후보로 반환한다."
  - "worker는 QA Pass, Gate 완료, 수정 완료를 확정하지 않고 Orchestrator 결정 필요 항목으로 반환한다."

qa_execution_policy:
  worker_can_run_tests: true
  worker_can_write_evidence: true
  worker_can_modify_source: false
  result_statuses: [Pass, Fail, Not Run, Skipped, environment_blocked]
  qa_workspace_policy:
    - "QA-000은 Gate 4 전체에서 재사용할 QA workspace/worktree를 준비하고 경로를 Run 결과에 기록한다."
    - "QA-001, QA-002, QA-003은 QA-000이 기록한 동일 QA workspace/worktree에서 실행한다."
    - "QA-000 workspace가 없거나 차단되면 후속 QA Run은 새 공간을 임의로 만들지 않고 Orchestrator 결정 필요 항목으로 반환한다."
    - "QA 중 결함 수정은 QA workspace에서 직접 수행하지 않고 dev 통합 브랜치의 qa-fix-loop로 분리한다."
  qa000_required_checks:
    - "Gradle wrapper 또는 backend 빌드 도구가 로컬 캐시/권한 기준으로 실행 가능한지 확인한다."
    - "backend 최소 smoke test 또는 test discovery가 실행 가능한지 확인한다."
    - "frontend 의존성이 설치되어 있거나 npm ci/npm install을 실행할 수 있는지 확인한다."
    - "Playwright package와 browser cache가 있거나 npx playwright install을 실행할 수 있는지 확인한다."
    - "backend/frontend 개발 포트(예: 8080, 5173 또는 프로젝트 지정 포트)가 사용 가능한지 확인한다."
    - "SQLite 또는 프로젝트 지정 DB 파일을 생성/접근할 수 있는지 확인한다."
    - "필수 환경변수, test profile, 임시 디렉터리, 로그/증적 출력 디렉터리를 확인한다."
  stages:
    - "QA-000 환경 준비/스모크: 통합된 소스, 의존성, DB/포트/환경변수, backend/frontend 기동 가능성, Playwright 설치/브라우저 캐시를 확인하고 후속 QA Run이 재사용할 QA workspace/worktree 경로를 기록한다."
    - "QA-001 명령 기반 검증: QA-000 workspace에서 backend/frontend test, lint, build, check-contract, check-trace, run-check를 실행하고 로그 증적을 남긴다."
    - "QA-002 UI/E2E 증적: QA-000 workspace에서 서버를 띄우고 UI-ID별 Playwright screenshot/log/trace를 수집한다."
    - "QA-003 결과 정리/판정 후보: QA Finding, Test Result, traceability 반영 후보, FIND/CR/ISSUE, Gate4 완료 판단 필요 항목을 정리한다."
  on_failure:
    - "코드를 직접 수정하지 않는다."
    - "원인 가설, 재현 명령, 로그 경로, 영향 ID를 남긴다."
    - "승인된 설계 범위 안의 결함이면 FIND 후보로 남긴다."
    - "요구사항/API/DB/보안/화면 계약 변경이 필요하면 CR 후보로 남긴다."
verification:
  commands:
    - "python vulcan.py run-check docs/runs/RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"
  evidence:
    required: true
    target_documents:
      - "docs/runs/RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md"

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
- `completion_criteria`를 모두 만족하도록 테스트 실행 결과, 로그/화면 증적, 후보 FIND/CR/ISSUE, 자기 Run 기록을 갱신한다.
- QA 실행 worker Run은 테스트 실행/증적 수집/원인 분류 단위로 끝나는 완결 조각이어야 한다.
- 실제 프로젝트 값으로 작성하고 placeholder를 완료 산출물에 남기지 않는다.
- QA 실행 worker Run이면 실행한 명령과 Orchestrator가 재실행할 `verification.commands`를 결과 문서에 남긴다.

- QA 실행 worker이면 테스트 실패 또는 이상 동작을 발견해도 소스코드를 수정하지 않는다.
- QA 실패는 원인 가설, 재현 명령, 로그 경로, 영향 ID, 후보 FIND/CR/ISSUE로 기록하고 Orchestrator 결정 필요 항목으로 반환한다.
- Gate 4 전체 QA를 한 Run에서 모두 수행하지 않는다. QA-000 환경 준비, QA-001 명령 검증, QA-002 UI/E2E 증적, QA-003 결과 정리 중 현재 Run의 범위를 명시한다.
- QA-000은 후속 QA-001/QA-002/QA-003이 재사용할 QA workspace/worktree 경로를 남긴다.
- QA-001/QA-002/QA-003은 QA-000이 기록한 같은 QA workspace/worktree에서 실행한다.
- QA-000 환경 준비가 통과하지 않으면 QA-001/QA-002를 진행하지 않고 environment_blocked 또는 Not Run으로 반환한다.

- UI 검증이 포함되면 `ui_evidence_policy`에 따라 상태/시나리오별 UI-ID와 증적 파일을 1:1로 연결한다.
- UIREF, 화면 퍼블리싱 산출물, 외부 시안이 있으면 `ui_implementation_contract_policy`에 따라 설계-구현-증적 비교 기준을 남긴다.
- subagent, CLI, 별도 worktree에서 작업자 runner로 실행 중이면 `worker_execution_policy`를 따른다.
- 기준 충돌, 범위 초과, 도메인 정보 부족은 임의로 통과시키지 말고 `open_issues`에 남기거나 사용자에게 질문한다.
- 작업자 runner이면 Gate 진행 승인 질문을 사용자에게 직접 하지 말고 Orchestrator 결정 필요 항목으로 반환한다.

## 5. QA Worker 완료 및 Orchestrator 반환

Run을 완료할 때 다음 항목을 반드시 남긴다.

| 항목 | 작성 기준 |
| --- | --- |
| 실행 검증 요약 | 실행한 명령, cwd, exit code, 성공 기준, 결과 |
| 증적 | 로그, screenshot, trace, report 파일 경로와 관련 UT/IT/UI ID |
| 실패/차단 분류 | `Fail`, `Not Run`, `Skipped`, `environment_blocked` 사유 |
| 원인 가설 | 실패 재현 명령, 영향 ID, 관련 로그 위치 |
| 후보 분류 | 승인된 설계 범위 안이면 FIND 후보, 범위 변경이면 CR 후보, 판단 보류면 ISSUE 후보 |
| Orchestrator 결정 필요 | 수정 여부, 재실행 여부, CR 승격 여부, Gate 완료 판단 필요 항목 |

QA 실행 worker는 소스코드를 수정하지 않고, 사용자 승인 질문, Gate 완료 선언, QA Pass, 릴리즈 승인, merge 가능 판단을 직접 하지 않는다.

## 6. 완료 보고

```yaml
run_id: RUN-014
status: Completed

execution:
  runner: codex-cli
  worktree: <QA_WORKSPACE>
  branch: codex/run-run-014-codex-cli
  qa_workspace_path: <QA_WORKSPACE>
  qa_stage: QA-000

summary:
  ko: "Gate 4 QA-000 환경 준비/스모크를 수행했고, 후속 QA Run이 재사용할 QA workspace와 로그 증적을 남겼다."
  changed_behavior:
    - "소스코드는 수정하지 않았다."
    - "Python hello API의 의존성, test discovery, 개발 포트, Uvicorn startup smoke가 실행 가능한 상태임을 확인했다."
    - "Frontend/UI/Playwright와 DB는 개발표준상 제외 범위로 Skipped 처리했다."
    - "QA Pass, Gate 완료, 릴리즈 가능 여부는 확정하지 않았다."

changed_files:
  - path: docs/runs/RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md
    change_type: modified
    related_ids: [RUN-014, REQ-001-01, UT-001, IT-001, IT-002]
  - path: docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md
    change_type: modified
    related_ids: [RUN-014, REQ-001-01, SEC-001]
  - path: docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
    change_type: modified
    related_ids: [RUN-014, REQ-001-01, UT-001, IT-001, IT-002]
  - path: docs/artifacts/04-review/evidence/qa-000/
    change_type: added
    related_ids: [RUN-014, UT-001, IT-001, IT-002]

related_ids:
  req: [REQ-001-01]
  ac: [AC-001-01, AC-001-02, AC-002-01]
  func: [FUNC-001]
  scr: []
  pgm: [PGM-001]
  api: [API-001]
  db: []
  sec: [SEC-001]
  test: [UT-001, IT-001, IT-002]

verification_results:
  - id: QA-000-GIT
    type: environment
    cwd: repository root
    command: "git -c safe.directory=<QA_WORKSPACE> status --short --branch"
    os: windows
    exit_code: 0
    success_criteria: "QA workspace branch 확인 가능"
    result: passed
    summary: "branch codex/run-run-014-codex-cli 확인"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-git-status.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-git-status.log
  - id: QA-000-PY
    type: environment
    cwd: backend
    command: "<PYTHON_HOME>\\bin\\python.exe --version"
    os: windows
    exit_code: 0
    success_criteria: "Python interpreter 실행 가능"
    result: passed
    summary: "Python 3.14.3"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-python-version.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-python-version.log
  - id: QA-000-PIP
    type: environment
    cwd: backend
    command: "<PYTHON_HOME>\\bin\\python.exe -m pip --version"
    os: windows
    exit_code: 0
    success_criteria: "pip 실행 가능"
    result: passed
    summary: "pip 26.0.1"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pip-check.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pip-check.log
  - id: QA-000-DEPS
    type: dependency
    cwd: backend
    command: "<PYTHON_HOME>\\bin\\python.exe -m pip install -r requirements.txt"
    os: windows
    exit_code: 0
    success_criteria: "exit code 0"
    result: passed
    summary: "fastapi, uvicorn, pytest, httpx already satisfied"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pip-install.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pip-install.log
  - id: QA-000-COLLECT
    type: test_discovery
    cwd: backend
    command: "<PYTHON_HOME>\\bin\\python.exe -m pytest --collect-only -q"
    os: windows
    exit_code: 0
    success_criteria: "exit code 0, test discovery 가능"
    result: passed
    summary: "4 tests collected. Python 3.14 dependency deprecation warnings observed; not a QA-000 blocker."
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pytest-collect.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-pytest-collect.log
  - id: QA-000-PORT
    type: environment
    cwd: repository root
    command: "bind TCP 127.0.0.1:8000 availability check"
    os: windows
    exit_code: 0
    success_criteria: "port bind 가능"
    result: passed
    summary: "127.0.0.1:8000 available"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-port-8000.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-port-8000.log
  - id: QA-000-STARTUP
    type: smoke
    cwd: backend
    command: "in-process uvicorn.Server app.main:app on 127.0.0.1:8000 and urllib.request /hello"
    os: windows
    exit_code: 0
    success_criteria: "server startup succeeds, HTTP 200, body hello"
    result: passed
    summary: "server_started true, HTTP 200, body hello"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-uvicorn-startup-smoke.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-uvicorn-startup-smoke.log
  - id: QA-000-FE-PW
    type: applicability
    cwd: repository root
    command: "Test-Path package.json; Test-Path frontend; Test-Path backend/package.json"
    os: windows
    exit_code: 0
    success_criteria: "API-only 범위와 개발표준상 UI 제외 확인"
    result: skipped
    summary: "Frontend/UI/Playwright excluded by DOC-DEV-G2-001"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-frontend-playwright-applicability.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-frontend-playwright-applicability.log
  - id: QA-000-DB
    type: applicability
    cwd: repository root
    command: "DB file and development standard applicability check"
    os: windows
    exit_code: 0
    success_criteria: "DB 제외 범위 확인"
    result: skipped
    summary: "DB excluded by DOC-DEV-G2-001"
    log_path: docs/artifacts/04-review/evidence/qa-000/QA-000-db-applicability.log
    evidence_path: docs/artifacts/04-review/evidence/qa-000/QA-000-db-applicability.log

evidence:
  documents:
    - docs/runs/RUN-014_qa-000-gate-4-environment-smoke-for-python-hello-api_v0.1.md
    - docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md
    - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
  files:
    - docs/artifacts/04-review/evidence/qa-000/QA-000-git-status.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-python-version.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-pip-check.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-pip-install.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-pytest-collect.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-port-8000.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-uvicorn-startup-smoke.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-frontend-playwright-applicability.log
    - docs/artifacts/04-review/evidence/qa-000/QA-000-db-applicability.log
  logs:
    - docs/artifacts/04-review/evidence/qa-000/
  ui: []
  ui_contract_diffs: []
  commit: null

traceability_updates:
  - document: docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
    update: "QA-000 환경 준비/스모크 결과를 REQ-001-01, UT-001, IT-001, IT-002와 연결했다."
    owner: orchestrator
  - document: docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    update: "Gate 4 최종 검증 상태 반영은 QA-001/QA-003 이후 Orchestrator 재검증 필요."
    owner: orchestrator

gate_exit_summary:
  status: worker_completed
  completed_scope:
    - "QA-000 환경 준비/스모크"
  not_completed_scope:
    - "QA-001 명령 기반 검증"
    - "QA-002 UI/E2E 증적"
    - "QA-003 결과 정리/판정 후보"
  gate4_completion_decision: "Orchestrator 재검증 필요"

approval_request:
  pending: false
  question: null
  approval_recorded: false
  note: "QA worker Run은 사용자에게 Gate 승인 질문을 직접 하지 않고 Orchestrator 결정 필요 항목으로 반환한다."

open_issues: []

orchestrator_decision_needed:
  - "QA-000 결과를 기준으로 QA-001 명령 기반 검증 Run을 시작할지 결정해야 한다."
  - "QA Pass, Gate 4 완료, 추적표 최종 상태 반영은 Orchestrator 재검증 후 결정해야 한다."

findings: []
change_requests: []

next_run_suggestion:
  run_type: Evidence
  skill: qa-execution
  goal: "QA-001 명령 기반 검증으로 python -m pytest, check-contract, check-trace, run-check 결과를 로그 증적으로 수집한다."
  related_ids: [REQ-001-01, UT-001, IT-001, IT-002, SEC-001]
```

요약:
QA-000 환경 준비/스모크를 완료했다. 후속 QA workspace는 `<QA_WORKSPACE>`이며, QA-001/QA-002/QA-003은 이 경로를 재사용해야 한다. 소스 수정, QA Pass 선언, Gate 완료 선언은 하지 않았다.
