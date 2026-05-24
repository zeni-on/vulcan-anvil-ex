# Gate 4 QA Execution Run Input Sample

> 목적: Audit Profile에서 Gate 4 테스트 실행, 증적 수집, 결함 후보 분류를 worker에게 맡기는 기준 예시다.

```yaml
profile: "audit"
adapter: "codex-gpt"
run_type: "Evidence"
gate: "gate4"
skill: "qa-execution"
persona: "evidence"
qa_stage: "QA-000|QA-001|QA-002|QA-003"
qa_workspace:
  path: "TBD: QA-000이 준비하고 QA-001~QA-003이 재사용할 workspace/worktree 경로"
  base_branch: "dev"
  base_commit: "TBD"
related_ids: [UI-001-01, UT-001, IT-001, NREQ-001]
source_documents:
  read_first:
    - AGENTS.md
    - session.json
    - docs/core/TRACEABILITY_RULES.md
    - docs/adapters/codex-gpt/GATE_PROMPTS.md
    - docs/adapters/codex-gpt/skills/qa-execution.md
  working_documents:
    - docs/artifacts/04-review/
  reference_on_demand:
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
    - docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md
    - docs/artifacts/02-design/function/DOC-CORE-G2-001_Function-Spec_v0.1.md
    - docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Design_v0.1.md
    - docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md
    - docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md
    - docs/artifacts/02-design/data/DOC-DATA-G2-002_Database-Spec_v0.1.md
    - docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md
    - docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/templates/QA_FINDING_TEMPLATE.md
    - docs/templates/TEST_RESULT_TEMPLATE.md
    - docs/core/ID_SYSTEM.md
    - docs/core/ORCHESTRATOR_PROTOCOL.md
    - docs/core/AGENT_PERSONAS.md
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/core/DELIVERY_PROFILES.md
    - docs/core/RUN_INPUT_CONTRACT.md
    - docs/core/RUN_OUTPUT_CONTRACT.md
scope:
  writable:
    - docs/runs/RUN-NNN_gate4-qa-stage_v0.1.md
    - docs/artifacts/04-review/
completion_criteria:
  - "Gate 4 전체 QA를 한 번에 수행하지 않고 qa_stage 하나만 수행한다."
  - "QA-000은 후속 QA-001/QA-002/QA-003이 재사용할 qa_workspace.path를 기록한다."
  - "QA-001/QA-002/QA-003은 QA-000이 기록한 같은 qa_workspace.path에서 실행한다."
  - "QA-000 환경 준비/스모크가 통과하지 않으면 QA-001/QA-002를 진행하지 않고 environment_blocked 또는 Not Run으로 반환한다."
  - "개발표준정의서와 테스트케이스에서 필수로 지정한 검증 명령이 테스트 결과서에 모두 기록되어 있다."
  - "각 실행 검증에는 실행 위치(cwd), 명령/방법, OS, 성공 기준, exit code, 결과, 로그/증적 경로가 있다."
  - "실행하지 못한 필수 명령은 Pass가 아니라 Not Run으로 기록하고 사유, 영향 범위, 후속 조치가 있다."
  - "적용 제외한 명령은 Skipped로 기록하고 승인 근거 또는 적용 제외 사유가 있다."
  - "화면/UI 증적 또는 로그 증적이 관련 UI/UT/IT/PT ID와 1:1로 연결되어 있다."
  - "회원가입, 로그인, TODO 같은 UI 흐름은 기본/오류/성공/전환 상태별 캡처가 분리되어 있다."
  - "화면 캡처 증적은 Playwright로 생성되어 있으며, Playwright 미설치 시 설치 명령과 재실행 결과가 기록되어 있다."
  - "CDP, 브라우저 수동 캡처, 런타임 Preview 캡처만으로 UI Pass를 확정하지 않는다."
  - "화면 퍼블리싱 기반 화면은 기준 UIREF와 구현 screenshot의 차이 목록 및 허용 여부가 기록되어 있다."
  - "증적 파일이 기대 화면을 실제로 보여주지 못하면 Pass가 아니라 Fail 또는 Not Run으로 기록되어 있다."
  - "결함은 FIND로 기록하고, 범위 변경은 CR로 승격한다."
  - "실패가 발생하면 코드를 즉시 수정하지 않고 원인 가설, 재현 명령, 로그, 영향 ID를 기록한다."
  - "새 API, 새 메소드, 요구사항/설계 변경이 필요하면 CR 후보로 반환한다."
  - "수정 완료 결함은 qa-fix-loop Run과 재검증 결과가 연결되어 있다."
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
gate_exit_policy:
  stop_required: true
  next_gate_requires_user_approval: true
  approval_evidence_required: true
ui_evidence_policy:
  state_level_required: true
  id_pattern: "UI-001-01"
  capture_tool_required: "Playwright"
  install_if_missing:
    - "npx playwright --version"
    - "npm install -D @playwright/test"
    - "npx playwright install"
  pass_forbidden_when:
    - "CDP 또는 브라우저 수동 캡처만 있고 Playwright 실행 결과가 없다."
  examples:
    - "UI-001-01 회원가입 기본 화면"
    - "UI-001-02 약한 비밀번호 오류"
    - "UI-001-05 회원가입 성공 메시지"
ui_implementation_contract_policy:
  gate4_required_evidence:
    - 기준 UIREF screenshot 또는 ui-baseline 경로
    - 구현 screenshot
    - 차이 목록
    - 허용된 차이 여부
    - 미허용 차이의 FIND 또는 CR
```

## Review Notes

- `working_documents`에는 이번 Run이 작성/갱신할 QA 결과, 결함, 증적만 둔다. 테스트케이스, 설계 산출물, 추적표는 실행 기준 확인이나 결함 판정이 필요할 때 `reference_on_demand` 또는 Orchestrator 판단 자료로 확인한다.
- Gate 4 QA는 `QA-000` 환경 준비, `QA-001` 명령 검증, `QA-002` UI/E2E 증적, `QA-003` 결과 정리로 쪼갠다.
- `QA-000`은 구현 통합 결과가 실제로 실행 가능한지 다시 확인하고, 후속 QA가 재사용할 `qa_workspace.path`를 확정하는 단계다. 여기서 차단되면 후속 QA를 억지로 진행하지 않는다.
- `QA-001`, `QA-002`, `QA-003`은 새 workspace를 만들지 않고 `QA-000`이 기록한 같은 `qa_workspace.path`에서 실행한다.
- `qa-execution` worker는 테스트 실행과 증적 수집을 맡고, 소스코드 수정은 하지 않는다.
- 실패 원인이 명확해 보여도 worker가 즉시 새 API, 새 메소드, 새 화면 상태를 만들지 않는다.
- Orchestrator는 worker의 실패/차단 보고를 보고 사용자와 `FIND` 수정, `CR` 승격, 재실행, 보류 중 하나를 결정한다.
- QA 결함이 승인된 설계 범위 안이면 FIND로 처리한다.
- 요구사항, 보안 기준, 릴리즈 범위를 바꾸면 CR로 승격한다.
- 개발표준의 필수 명령이 테스트결과서에 없거나, exit code/성공 기준/로그 증적 없이 Pass로 기록되어 있으면 FIND로 남긴다.
- 화면 QA는 Playwright 기준으로 수행한다. CDP나 브라우저 수동 캡처는 보조 관찰로만 남기고 Pass 증적으로 쓰지 않는다.
- 화면 퍼블리싱 기반 화면이 UI Implementation Contract와 다르면 기준 UIREF와 구현 screenshot을 비교하고, 허용되지 않은 차이를 FIND로 남긴다.
- 기대 화면과 다른 캡처를 Pass로 기록하지 않는다. 예를 들어 회원가입 성공 테스트에 로그인 화면만 있으면 FIND로 남긴다.

