# Implementation Build Wave Run Input Sample

> 목적: Audit Profile에서 구현 단계가 승인된 설계와 테스트 범위 안에서만 움직이게 하는 기준 예시다.

```yaml
profile: "audit"
run_type: "Implementation"
gate: "impl"
skill: "implementation-plan"
persona: "build-planning"
related_ids: [REQ-001, PGM-001, UT-001, IT-001]
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
  - "화면 구현은 관련 SCR의 UI Implementation Contract와 Gate 3 UI 테스트 기준을 먼저 확인한다."
  - "Build Wave 범위, 소유 파일, 관련 ID, 검증 명령이 명확하다."
  - "구현 변경은 테스트 코드, 테스트 결과, 추적표 갱신과 연결된다."
  - "동시에 active 상태인 Build Wave가 하나만 유지된다."
gate_exit_policy:
  stop_required: true
  next_gate_requires_user_approval: true
  approval_evidence_required: true
ui_implementation_contract_policy:
  impl_checklist:
    - "구현 전 관련 SCR의 UI Implementation Contract를 확인한다."
    - "prototype CSS 또는 동등한 레이아웃/class 구조를 재사용했는지 기록한다."
    - "보안가이드 때문에 바꾼 문구, 필드, 흐름은 DEC/ISSUE/FIND/CR 중 하나로 기록한다."
    - "기본/오류/성공/전환 상태가 Gate 3 UI-ID와 연결되어 있는지 확인한다."
    - "구현 결과 screenshot이 기준 UIREF와 비교 가능한 위치에 저장되는지 확인한다."
```

## Review Notes

- 중간 이상 구현은 `implementation-plan`으로 Wave를 먼저 나눈 뒤 `build-wave`로 실행한다.
- prototype 기반 화면 구현은 UI Implementation Contract를 먼저 확인하고, 다르면 임의 재설계가 아니라 `FIND` 또는 `CR`로 분류한다.
- 구현자가 자기 구현을 최종 승인하지 않도록 Orchestrator 검증과 review Run을 분리한다.
- 구현 완료 후 Gate 4 QA로 넘어가기 전 구현 범위, 테스트 결과, 남은 이슈를 요약하고 승인 질문을 남긴다.
