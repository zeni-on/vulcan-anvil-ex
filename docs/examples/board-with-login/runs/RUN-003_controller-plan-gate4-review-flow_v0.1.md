# RUN-003 Controller Plan - 로그인 게시판 샘플 Gate 4 검수 흐름 확인

```yaml
run_id: RUN-003
adapter: codex-gpt
gate: gate4
persona: review
skill: controller-plan
skill_path: docs/core/CONTROLLER_PROTOCOL.md
status: Completed
created_at: 2026-05-10
related_ids: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, UI-001]
verification_results:
  - command: "python ../../../vulcan.py controller-plan --goal \"로그인 게시판 샘플 Gate 4 검수 흐름 확인\" --gate gate4 --persona review --related-ids REQ-001,REQ-002,REQ-003,REQ-004,REQ-005,REQ-006,UI-001"
    result: passed
  - command: "python ../../../vulcan.py run-check runs/RUN-003_controller-plan-gate4-review-flow_v0.1.md"
    result: passed
evidence:
  - docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md
  - docs/examples/board-with-login/DOC-QA-G4-003_UI-Test-Result_v0.1.md
  - docs/examples/board-with-login/evidence/ui/SCR-001_signup/desktop.png
  - docs/examples/board-with-login/evidence/ui/SCR-006_edit-post/desktop.png
traceability_updates:
  - "Controller 기반 Gate 4 진입 시 handoff는 강제가 아니라 제안으로 처리한다."
findings: []
change_requests: []
open_issues: []
```

## 1. Controller 목표

로그인 게시판 샘플에서 Controller 기반 Gate 4 검수 흐름이 자연스럽게 동작하는지 확인한다.

## 2. 먼저 읽은 문서

- `AGENTS.md`
- `docs/core/CONTROLLER_PROTOCOL.md`
- `docs/core/AGENT_PERSONAS.md`
- `docs/core/AGENT_RUN_PROTOCOL.md`
- `docs/core/TRACEABILITY_RULES.md`
- `docs/core/CHANGE_CONTROL_PROCESS.md`
- `docs/adapters/codex-gpt/PERSONA_DELEGATION.md`
- `docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md`
- `docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md`
- `docs/examples/board-with-login/DOC-QA-G4-002_Test-Result_v0.1.md`
- `docs/examples/board-with-login/DOC-QA-G4-003_UI-Test-Result_v0.1.md`

## 3. 판단 범위

| 항목 | 내용 |
| --- | --- |
| Gate | `gate4` |
| 우선 persona | `review` |
| 관련 ID | `REQ-001`~`REQ-006`, `UI-001` |
| 목표 산출물 | Controller plan, 검증 결과, handoff 판단 |
| 제외 범위 | 신규 기능 구현, 신규 화면 캡처 생성 |
| 사용자 승인 필요 항목 | 별도 desktop handoff 실행 여부 |

## 4. 권장 Run 순서 검토

| 순서 | persona | 목적 | 산출물 | 검증 |
| --- | --- | --- | --- | --- |
| 1 | `review` | 기존 Gate 4 산출물과 UI 증적 확인 | RUN-003 | `run-check` |
| 2 | `evidence` | 화면 증적이 부족한 경우 보강 | 선택 | desktop handoff 제안 |
| 3 | `review` | FIND/CR/ISSUE 판단 | 본 Run 완료 보고 | 추적성 확인 |

## 5. Handoff 판단

Gate 4로 넘어갈 때 Controller는 desktop handoff를 제안할 수 있다. 이번 샘플은 이미 `DOC-QA-G4-003_UI-Test-Result_v0.1.md`와 `evidence/ui/SCR-001`~`SCR-006` 화면 캡처가 존재한다.

따라서 이번 검증에서는 별도 desktop handoff Run을 만들지 않고, 현재 환경에서 문서와 증적 존재 여부를 확인하는 방식으로 진행한다.

## 6. 완료 보고

### 요약

Controller 기반 Gate 4 흐름은 샘플 프로젝트에서 동작했다. `vulcan.py`는 기존 샘플의 `runs/` 디렉터리를 자동 감지하도록 보강이 필요했고, 이를 반영했다.

### 위임 결과

별도 subagent 또는 desktop handoff는 실행하지 않았다. 기존 UI 증적이 충분하므로 현재 환경에서 `review` 관점 검증으로 처리했다.

### 검증 결과

- `controller-plan` 명령으로 `RUN-003` 생성 확인
- `run-check` 통과
- 기존 Gate 4 테스트 결과 문서와 UI 증적 문서 존재 확인

### 다음 핸드오프

다음 실제 화면 변경이 발생하면 Gate 4 진입 시 사용자에게 desktop handoff를 제안한다. 사용자가 수락하면 `vulcan.py handoff --to desktop ...` 흐름을 사용한다.
