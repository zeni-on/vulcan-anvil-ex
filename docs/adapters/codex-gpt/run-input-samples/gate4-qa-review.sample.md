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
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
    - docs/artifacts/04-review/DOC-QA-G4-001_QA-Finding_v0.1.md
    - docs/artifacts/04-review/DOC-QA-G4-002_Test-Result_v0.1.md
    - docs/artifacts/04-review/evidence/
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  reference_on_demand:
    - docs/templates/QA_FINDING_TEMPLATE.md
    - docs/templates/TEST_RESULT_TEMPLATE.md
    - docs/core/ID_SYSTEM.md
    - docs/core/ORCHESTRATOR_PROTOCOL.md
    - docs/core/AGENT_PERSONAS.md
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/core/DELIVERY_PROFILES.md
    - docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md
    - docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
scope:
  writable:
    - docs/artifacts/04-review/
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/runs/
completion_criteria:
  - "실행한 테스트 명령과 결과가 테스트 결과서에 기록되어 있다."
  - "화면/UI 증적 또는 로그 증적이 관련 UI/UT/IT/PT ID와 1:1로 연결되어 있다."
  - "회원가입, 로그인, TODO 같은 UI 흐름은 기본/오류/성공/전환 상태별 캡처가 분리되어 있다."
  - "프로토타입 기반 화면은 기준 UIREF와 구현 screenshot의 차이 목록 및 허용 여부가 기록되어 있다."
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
  examples:
    - "UI-001-01 회원가입 기본 화면"
    - "UI-001-02 약한 비밀번호 오류"
    - "UI-001-05 회원가입 성공 메시지"
ui_implementation_contract_policy:
  gate4_required_evidence:
    - 기준 UIREF screenshot 또는 prototype 경로
    - 구현 screenshot
    - 차이 목록
    - 허용된 차이 여부
    - 미허용 차이의 FIND 또는 CR
```

## Review Notes

- QA 결함이 승인된 설계 범위 안이면 FIND로 처리한다.
- 요구사항, 보안 기준, 릴리즈 범위를 바꾸면 CR로 승격한다.
- prototype 기반 화면이 UI Implementation Contract와 다르면 기준 UIREF와 구현 screenshot을 비교하고, 허용되지 않은 차이를 FIND로 남긴다.
- 기대 화면과 다른 캡처를 Pass로 기록하지 않는다. 예를 들어 회원가입 성공 테스트에 로그인 화면만 있으면 FIND로 남긴다.
