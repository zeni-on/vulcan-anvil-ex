# Gate 4 QA Review Run Input Sample

> 목적: Audit Profile에서 테스트 결과, 증적, 결함 처리를 연결하는 기준 예시다.

```yaml
profile: "audit"
run_type: "Review"
gate: "gate4"
skill: "qa-fix-loop"
persona: "build"
related_ids: [FIND-001, UI-001, UT-001, IT-001]
source_documents:
  read_first:
    - AGENTS.md
    - session.json
    - docs/core/TRACEABILITY_RULES.md
    - docs/adapters/codex-gpt/GATE_PROMPTS.md
    - docs/adapters/codex-gpt/skills/qa-fix-loop.md
  working_documents:
    - docs/artifacts/04-review/
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
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
    - docs/artifacts/04-review/
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/runs/
completion_criteria:
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
  - "수정 완료 결함은 qa-fix-loop Run과 재검증 결과가 연결되어 있다."
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

- `working_documents`에는 이번 Run이 작성/갱신할 QA 결과, 결함, 증적, 추적표만 둔다. 테스트케이스와 설계 산출물은 실행 기준 확인이나 결함 판정이 필요할 때 `reference_on_demand`에서 관련 ID 기준으로 확인한다.
- QA 결함이 승인된 설계 범위 안이면 FIND로 처리한다.
- 요구사항, 보안 기준, 릴리즈 범위를 바꾸면 CR로 승격한다.
- 개발표준의 필수 명령이 테스트결과서에 없거나, exit code/성공 기준/로그 증적 없이 Pass로 기록되어 있으면 FIND로 남긴다.
- 화면 QA는 Playwright 기준으로 수행한다. CDP나 브라우저 수동 캡처는 보조 관찰로만 남기고 Pass 증적으로 쓰지 않는다.
- 화면 퍼블리싱 기반 화면이 UI Implementation Contract와 다르면 기준 UIREF와 구현 screenshot을 비교하고, 허용되지 않은 차이를 FIND로 남긴다.
- 기대 화면과 다른 캡처를 Pass로 기록하지 않는다. 예를 들어 회원가입 성공 테스트에 로그인 화면만 있으면 FIND로 남긴다.

