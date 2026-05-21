# Implementation Build Wave Run Input Sample

> 목적: Audit Profile에서 구현 단계가 승인된 설계와 테스트 범위 안에서만 움직이게 하는 기준 예시다.
> 이 샘플은 두 단계로 본다. 먼저 Orchestrator가 Wave를 나누는 `implementation-plan`을 만들고, 실제 작업자에게는 더 얇은 `build-wave` 계약을 전달한다.

```yaml
profile: "audit"
run_type: "Implementation"
gate: "impl"
skill: "implementation-plan"
persona: "build-planning"
related_ids: [REQ-001, PGM-001, UT-001, IT-001]
runner_hint:
  frontend: "claude-cli"
  backend: "codex-cli"
  evidence: "codex-cli"
source_documents:
  read_first:
    - AGENTS.md
    - session.json
    - docs/core/TRACEABILITY_RULES.md
    - docs/adapters/codex-gpt/GATE_PROMPTS.md
    - docs/adapters/codex-gpt/skills/implementation-plan.md
  working_documents:
    - docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md
    - docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/artifacts/02-design/program/DOC-CORE-G2-002_Program-Spec_v0.1.md
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  reference_on_demand:
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/core/ID_SYSTEM.md
    - docs/core/ORCHESTRATOR_PROTOCOL.md
    - docs/core/AGENT_PERSONAS.md
    - docs/core/DELIVERY_PROFILES.md
    - docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md
    - docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
scope:
  writable:
    - docs/runs/
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
completion_criteria:
  - "승인된 Gate 2/3 범위 안에서만 구현 또는 구현 계획을 작성한다."
  - "코딩 전 개발표준정의서의 패키지 구조, 계층 책임, 로깅, 주석, 예외/메시지, 테스트 명령을 확인하고 준수 체크리스트를 남긴다."
  - "Spring Boot 구현은 개발표준의 base package와 feature 우선 패키지 구조를 따른다. domain 래퍼는 DDD 선택 사유가 있을 때만 사용한다."
  - "로깅은 개발표준의 SLF4J/Logback 또는 Log4j2 선택, logger 선언, 로그 레벨, 민감정보 금지 기준을 따른다."
  - "Java/Spring 주요 클래스와 public 업무 메서드는 개발표준의 JavaDoc/추적 ID 기준을 따른다."
  - "화면 구현은 관련 SCR의 UI Implementation Contract와 Gate 3 UI 테스트 기준을 먼저 확인한다."
  - "Build Wave 범위, 소유 파일, 관련 ID, 검증 명령이 명확하다."
  - "Frontend Wave와 Backend Wave가 분리되어 있고, 기본 runner가 각각 claude-cli/codex-cli로 제안되어 있다."
  - "구현 변경은 테스트 코드, 테스트 결과, 추적표 갱신과 연결된다."
  - "동시에 active 상태인 Build Wave가 하나만 유지된다."
development_standard_policy:
  required: true
  block_implementation_when_missing:
    - "base package와 backend 패키지 구조"
    - "계층 책임과 금지 의존성"
    - "로깅 API/구현체, logger 선언, 로그 레벨, 민감정보 로그 금지"
    - "클래스/메서드 주석 또는 JavaDoc 기준과 예시"
    - "필수 검증 명령의 cwd, 성공 기준, 결과 기록 위치"
  spring_boot_default:
    package_style: "feature-first"
    domain_wrapper_allowed_only_with_reason: true
    required_top_level_packages:
      - config
      - common
      - security
      - auth
      - user
      - "{featureName}"
gate_exit_policy:
  stop_required: true
  next_gate_requires_user_approval: true
  approval_evidence_required: true
worker_execution_policy:
  applies_when: "Build Wave가 subagent, codex-cli, claude-cli 등 작업자 runner에게 전달되는 경우"
  role: "worker-runner"
  forbidden_actions:
    - "Gate 전환을 수행하지 않는다."
    - "session.json의 current_gate, gate_status, completed를 직접 변경하지 않는다."
    - "사용자 승인, QA Pass, 릴리즈 승인, merge 가능 여부를 최종 확정하지 않는다."
    - "Orchestrator가 요청하지 않은 신규 Run, PR, 커밋, push를 만들지 않는다."
  required_outputs:
    - "수행한 변경과 검증 결과를 Run 결과에 남긴다."
    - "Gate 전환, session 변경, 최종 승인 판단이 필요하면 Orchestrator 결정 필요 항목으로 반환한다."
ui_implementation_contract_policy:
  impl_checklist:
    - "구현 전 관련 SCR의 UI Implementation Contract를 확인한다."
    - "화면 퍼블리싱 CSS 또는 동등한 레이아웃/class 구조를 재사용했는지 기록한다."
    - "보안가이드 때문에 바꾼 문구, 필드, 흐름은 DEC/ISSUE/FIND/CR 중 하나로 기록한다."
    - "기본/오류/성공/전환 상태가 Gate 3 UI-ID와 연결되어 있는지 확인한다."
    - "구현 결과 screenshot이 기준 UIREF와 비교 가능한 위치에 저장되는지 확인한다."
```

## Review Notes

- 중간 이상 구현은 `implementation-plan`으로 Wave를 먼저 나눈 뒤 `build-wave`로 실행한다.
- 실제 `build-wave` 작업자 Run은 이 계획 Run보다 더 좁은 focused source를 사용한다. 전체 설계 산출물을 `working_documents`에 모두 넣지 않고, 현재 Wave Run, 개발표준, 테스트케이스, 추적표를 우선 작업 문서로 둔다.
- API/화면/프로그램/DB/보안 설계는 related ID나 기준 충돌이 있을 때 필요한 문서만 `reference_on_demand`에서 확인한다.
- 화면 퍼블리싱 기반 화면 구현은 UI Implementation Contract를 먼저 확인하고, 다르면 임의 재설계가 아니라 `FIND` 또는 `CR`로 분류한다.
- 구현자는 Gate 전환, session 변경, 최종 승인 판단을 하지 않는다. Orchestrator가 검증과 review Run을 분리한다.
- 구현 완료 후 Gate 4 QA로 넘어가기 전 구현 범위, 테스트 결과, 남은 이슈를 요약하고 승인 질문을 남긴다.

## Worker Build Wave 예시

작업자 runner에게 전달되는 실제 `build-wave` Run은 더 좁아야 한다.
아래 예시는 frontend 담당 worker 기준이며, backend worker라면 `frontend/`를 `backend/`와 해당 테스트 경로로 바꾼다.

```yaml
profile: "audit"
run_type: "Implementation"
gate: "impl"
skill: "build-wave"
persona: "build"
related_ids: [REQ-001, SCR-001, UI-001, UT-001]
source_documents:
  read_first:
    - AGENTS.md
    - session.json
    - docs/adapters/codex-gpt/skills/build-wave.md
  working_documents:
    - docs/runs/RUN-022_bw-001-frontend-구현-claude_v0.1.md
    - docs/artifacts/02-design/development-standard/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
    - docs/artifacts/02-design/screen/ui-baseline/
  reference_on_demand:
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/core/TRACEABILITY_RULES.md
    - docs/artifacts/01-requirements/DOC-CORE-G1-001_Requirements-Spec_v0.1.md
    - docs/artifacts/02-design/screen/DOC-CORE-G2-003_Screen-Spec_v0.1.md
    - docs/artifacts/02-design/api/DOC-API-G2-001_API-Spec_v0.1.md
    - docs/artifacts/02-design/security/DOC-SEC-G2-001_Security-Guide_v0.1.md
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
scope:
  writable:
    - frontend/
    - docs/artifacts/04-review/evidence/ui/
    - docs/runs/RUN-022_bw-001-frontend-구현-claude_v0.1.md
  readonly:
    - docs/core/
    - docs/templates/
    - docs/seed-docs/reference-standards/
  excluded:
    - session.json
    - docs/ref-docs/
    - backend/
    - "**/node_modules/"
    - "**/.next/"
completion_criteria:
  - "담당 Wave 범위만 구현하고 다른 worker 범위는 수정하지 않는다."
  - "UI Implementation Contract와 Gate 3 UI 테스트 기준을 구현 전 확인한다."
  - "담당 테스트, 린트, 빌드를 실행하고 결과를 현재 Run에 남긴다."
  - "추적표 또는 session 갱신 필요 항목은 Orchestrator 결정 필요 항목으로 반환한다."
verification:
  commands:
    - "npm run lint"
    - "npm run build"
    - "python vulcan.py run-check docs/runs/RUN-022_bw-001-frontend-구현-claude_v0.1.md"
  evidence:
    required: true
    target_documents:
      - docs/runs/RUN-022_bw-001-frontend-구현-claude_v0.1.md
      - docs/artifacts/04-review/evidence/ui/
worker_execution_policy:
  forbidden_actions:
    - "Gate 전환, session 변경, wave-complete, check-trace, sync-session을 직접 실행하지 않는다."
    - "사용자 승인, QA Pass, merge 가능 여부를 최종 판단하지 않는다."
    - "scope.writable 밖 파일을 수정하지 않는다."
```
