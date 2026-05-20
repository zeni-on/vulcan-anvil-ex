# Codex/GPT Run Input Contract

> 상태: 초안 v0.1
> 목적: Codex/GPT 계열 에이전트에게 작업을 맡길 때 전달할 표준 작업지시서 형식을 정의한다.

## 1. 개념

Run Input Contract는 에이전트에게 주는 작업지시서다.

사람이 자연어로 요청하더라도 Adapter는 이를 다음 구조로 바꿔 에이전트에게 전달해야 한다.

```text
누가 보아도 같은 범위
같은 기준 문서
같은 관련 ID
같은 완료 조건
같은 금지사항
```

이 계약은 Codex/GPT가 임의로 범위를 넓히거나, 문서를 건너뛰거나, 테스트 없이 완료를 선언하는 일을 줄이기 위한 것이다.

## 2. 필수 필드

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `run_id` | 예 | 실행 단위 ID. 예: `RUN-001` |
| `adapter` | 예 | Adapter 이름. 예: `codex-gpt` |
| `persona` | 예 | 표준 작업 persona. 예: `requirements`, `design`, `build`, `review` |
| `agent_role` | 아니오 | adapter 호환용 보조 역할명. 예: `implementation-agent`, `review-agent` |
| `run_type` | 예 | `Discovery`, `Design`, `Implementation`, `Test`, `Evidence`, `Review` |
| `gate` | 예 | 현재 Gate. 예: `G2`, `G4` |
| `project` | 예 | 대상 프로젝트 또는 샘플 이름 |
| `goal` | 예 | 이번 Run에서 달성할 구체 목표 |
| `related_ids` | 예 | 요구사항, 설계, 보안, 테스트 ID |
| `source_documents` | 예 | 먼저 읽을 문서, 작업 대상 문서, 필요 시 참고 문서 |
| `design_sequence` | Gate 2 권장 | Gate 2 설계 산출 순서와 현재 Run 위치 판단 기준 |
| `scope` | 예 | 수정 가능/읽기 전용/제외 경로 |
| `completion_criteria` | 예 | 완료 판정 조건 |
| `verification` | 예 | 실행해야 할 테스트, 린트, 캡처 |
| `gate_exit_policy` | 예 | Gate 종료 시 멈춤, 승인 질문, 다음 Gate 진행 제한 |
| `ui_evidence_policy` | 화면 작업 시 예 | UI 테스트와 캡처 증적의 상태/시나리오 단위 연결 기준 |
| `ui_implementation_contract_policy` | 화면 작업 시 예 | UIREF/ui-baseline을 구현 계약으로 전환하고 설계-구현 차이를 판정하는 기준 |
| `output_requirements` | 예 | 결과 보고 형식과 갱신할 산출물 |
| `question_policy` | 예 | 질문해야 하는 조건 |
| `security_policy` | 예 | 민감문서, 비밀, 외부전송 제한 |

## 3. 권장 YAML 형식

```yaml
run_id: RUN-001
adapter: codex-gpt
persona: build
agent_role: implementation-agent
run_type: Implementation
gate: G4
project:
  name: Project Name
  root: .
goal: "PGM-005 업무 기능을 구현하고 관련 테스트를 통과시킨다."

related_ids:
  req: [REQ-005]
  nreq: [NREQ-001]
  ac: [AC-007, AC-008]
  func: [FUNC-005]
  scr: [SCR-005]
  pgm: [PGM-005]
  db: [DB-002]
  sec: [SEC-002, SEC-004]
  test: [UT-007, UT-008, IT-004]

source_documents:
  read_first:
    - AGENTS.md
    - session.json
    - docs/core/TRACEABILITY_RULES.md
    - docs/adapters/codex-gpt/GATE_PROMPTS.md
    - docs/adapters/codex-gpt/skills/build-wave.md
  working_documents:
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
    - docs/artifacts/02-design/DOC-CORE-G2-002_Program-Spec_v0.1.md
    - docs/artifacts/02-design/DOC-DEV-G2-001_Development-Standard_v0.1.md
    - docs/artifacts/03-test/DOC-QA-G3-001_Test-Cases_v0.1.md
  reference_on_demand:
    - docs/core/ID_SYSTEM.md
    - docs/core/ORCHESTRATOR_PROTOCOL.md
    - docs/core/AGENT_PERSONAS.md
    - docs/core/AGENT_RUN_PROTOCOL.md
    - docs/core/DELIVERY_PROFILES.md
    - docs/adapters/codex-gpt/RUN_INPUT_CONTRACT.md
    - docs/adapters/codex-gpt/RUN_OUTPUT_CONTRACT.md
    - docs/templates/
    - docs/seed-docs/reference-standards/
  optional:
    - docs/artifacts/02-design/DOC-CORE-G2-001_Function-Spec_v0.1.md
    - docs/artifacts/02-design/DOC-CORE-G2-003_Screen-Spec_v0.1.md

design_sequence:
  - "G2-01 Kickoff / 설계 범위 고정"
  - "G2-02 SW Architecture Draft"
  - "G2-03 Screen / User Flow"
  - "G2-04 Function Spec"
  - "G2-05 Program / API Spec"
  - "G2-06 Data / DB Spec"
  - "G2-07 Security Guide"
  - "G2-08 Development Standard"
  - "G2-09 SW Architecture Baseline 보강"
  - "G2-10 Design Review / Gate 3 승인 대기"

scope:
  writable:
    - app/api/work_items.py
    - app/services/work_item_service.py
    - tests/
    - docs/artifacts/04-results/DOC-QA-G4-002_Test-Result_v0.1.md
    - docs/artifacts/02-traceability/DOC-CORE-G4-001_Traceability-Matrix_v0.1.md
  readonly:
    - docs/core/
    - docs/templates/
    - docs/seed-docs/reference-standards/
  excluded:
    - docs/ref-docs/
    - "**/*.db"
    - "**/__pycache__/"
    - "**/.ruff_cache/"

completion_criteria:
  - "관련 구현이 개발표준의 Router-Service-Repository 구조를 따른다."
  - "UT-007, UT-008, IT-004가 통과한다."
  - "실행 결과가 테스트 결과서에 반영된다."
  - "요구사항추적표에 증적이 연결된다."

verification:
  commands:
    - "python -m pytest tests -p no:cacheprovider"
    - "python -m ruff check ."
  evidence:
    required: true
    target_documents:
      - docs/artifacts/04-results/DOC-QA-G4-002_Test-Result_v0.1.md

gate_exit_policy:
  stop_required: true
  next_gate_requires_user_approval: true
  approval_evidence_required: true
  allowed_next_action: "현재 Gate 산출물 요약, 미해결 항목, 다음 Gate 진행 승인 질문을 남기고 대기한다."
  forbidden_actions:
    - "사용자의 명시 승인 없이 다음 Gate 산출물을 작성하지 않는다."
    - "사용자의 명시 승인 없이 구현, 테스트 실행, QA 승인, 릴리즈 승인을 선언하지 않는다."
    - "대화상 승인 없이 Run 또는 릴리즈 승인서에 User Approved로 기록하지 않는다."

ui_evidence_policy:
  state_level_required: true
  id_pattern: "UI-001-01"
  minimum_fields:
    - UI-ID
    - 관련 SCR
    - 상태/시나리오
    - 입력값
    - 기대 화면
    - 실제 확인
    - 증적 파일
    - 결과
  examples:
    - "UI-001-01 회원가입 기본 화면"
    - "UI-001-02 약한 비밀번호 오류"
    - "UI-001-03 비밀번호 확인 불일치"
    - "UI-001-04 중복 이메일 오류"
    - "UI-001-05 회원가입 성공 메시지"
    - "UI-001-06 성공 후 로그인 연계"

ui_implementation_contract_policy:
  required_when: "화면설계서에 UIREF, 이미지 시안, HTML/CSS/JS 화면 퍼블리싱 산출물, Figma, 기존 화면 캡처, ui-baseline 경로가 있는 경우"
  gate2_required_fields:
    - 기준 파일 또는 URL
    - 기준 CSS 또는 디자인 토큰
    - 필수 유지 요소
    - 변경 허용 항목
    - 변경 금지 항목
    - 구현 비교 방식
    - 차이 발생 시 FIND/CR 판정 기준
  impl_checklist:
    - "구현 전 관련 SCR의 UI Implementation Contract를 확인한다."
    - "화면 퍼블리싱 CSS 또는 동등한 레이아웃/class 구조를 재사용했는지 기록한다."
    - "보안가이드 때문에 바꾼 문구, 필드, 흐름은 DEC/ISSUE/FIND/CR 중 하나로 기록한다."
    - "기본/오류/성공/전환 상태가 Gate 3 UI-ID와 연결되어 있는지 확인한다."
    - "구현 결과 screenshot이 기준 UIREF와 비교 가능한 위치에 저장되는지 확인한다."
  gate4_required_evidence:
    - 기준 UIREF screenshot 또는 ui-baseline 경로
    - 구현 screenshot
    - 차이 목록
    - 허용된 차이 여부
    - 미허용 차이의 FIND 또는 CR

output_requirements:
  format: "RUN_OUTPUT_CONTRACT.md"
  include:
    - changed_files
    - related_ids
    - verification_results
    - evidence
    - gate_exit_summary
    - approval_request
    - open_issues
    - next_run_suggestion

question_policy:
  ask_when:
    - "요구사항과 설계문서가 충돌한다."
    - "scope.writable 밖의 파일 수정이 필요하다."
    - "보안 기준을 낮추는 선택이 필요하다."
    - "테스트 실패 원인이 요구사항 변경 없이는 해결되지 않는다."

security_policy:
  forbidden_paths:
    - docs/ref-docs/
  allowed_reference_paths:
    - docs/seed-docs/reference-standards/
  forbidden_actions:
    - "민감문서 내용을 출력에 인용하지 않는다."
    - "토큰, 비밀번호, 개인식별정보를 커밋하지 않는다."
    - "승인 없이 외부 네트워크로 프로젝트 파일을 전송하지 않는다."
```

## 4. 필드 작성 규칙

`goal`은 한 문장으로 쓴다.

좋은 예:

```text
SCR-003 게시글 목록 화면을 구현하고 UI-003 캡처 증적을 생성한다.
```

나쁜 예:

```text
화면 좀 정리
```

`related_ids`는 가능한 한 비워두지 않는다. 관련 ID가 불명확하면 Run을 시작하기 전에 Discovery 또는 Review Run으로 전환한다.

`source_documents.read_first`는 에이전트가 작업 시작 전에 반드시 먼저 읽는 최소 문서다.
보통 `AGENTS.md`, `session.json`, 현재 Gate/Traceability 규칙, 현재 skill 문서만 둔다.

`source_documents.working_documents`는 이번 Run에서 실제로 작성하거나 검토할 산출물이다.
에이전트는 이 문서에 가장 많은 주의를 둔다.

`source_documents.reference_on_demand`는 항상 정독하는 문서가 아니다.
기준 충돌, 작성 규칙 확인, 보안/데이터/개발표준 판단처럼 필요할 때만 펼쳐본다.

`design_sequence`는 Gate 2 Run에서 사용한다.
에이전트는 이번 Run이 설계 순서의 어느 단계인지, 필요한 이전 단계가 누락되었는지, 다음 Gate 2 Run이 무엇인지 Run 결과에 남긴다.

`scope.writable` 밖의 파일 수정은 원칙적으로 금지한다. 단, 테스트 실행 중 생성물 제외를 위한 `.gitignore` 보정처럼 좁고 명백한 보정은 출력에 이유를 남긴다.

`gate_exit_policy.stop_required`가 `true`이면 에이전트는 현재 Gate 산출물 완료 후 반드시 멈춘다.
완료 보고에는 다음 Gate로 넘어가도 되는지 묻는 승인 질문과, 사용자가 승인했는지 여부를 남긴다.
대화상 명시 승인 없이 다음 Gate 산출물 작성, 구현 착수, QA Pass, 릴리즈 승인 선언을 하지 않는다.

UI 검증이 포함된 Run은 화면 단위가 아니라 상태/시나리오 단위로 테스트와 증적을 분리한다.
예를 들어 회원가입은 `UI-001` 한 건으로 처리하지 않고 기본 화면, 약한 비밀번호 오류, 비밀번호 확인 불일치, 중복 이메일, 성공 메시지, 로그인 연계처럼 `UI-001-01`부터 나눈다.
각 UI 테스트는 기대 화면과 실제 캡처 파일이 1:1로 연결되어야 한다.

`ui_implementation_contract_policy`는 화면 퍼블리싱 산출물 또는 외부 시안이 있는 화면 작업에서 사용한다.
Gate 2에서는 시안을 참고자료로 둘지 구현 계약으로 둘지 분류하고, 구현 계약이면 필수 유지, 변경 허용, 변경 금지, 비교 방식을 작성한다.
Gate 3에서는 이 계약을 UI 테스트 기대결과에 반영한다.
Impl에서는 구현 전 체크리스트로 확인하고, Gate 4에서는 기준 UIREF와 구현 screenshot의 차이를 `Pass`, `FIND`, `CR`로 판정한다.

## 5. Codex/GPT 전달 프롬프트 기본형

Adapter는 YAML 입력 뒤에 다음 실행 지침을 붙인다.

```text
너는 Vulcan-Anvil Ex Codex/GPT Adapter를 통해 실행되는 에이전트다.
아래 Run 입력 계약을 기준으로만 작업한다.

작업 순서:
1. source_documents.read_first를 먼저 읽고 관련 ID와 현재 Gate를 확인한다.
2. source_documents.working_documents를 중심으로 실제 산출물을 작성하거나 검토한다.
3. source_documents.reference_on_demand는 필요할 때만 참고한다.
4. scope.writable 안에서만 수정한다.
5. Gate 2 Run이면 design_sequence에서 현재 위치와 누락된 이전 단계를 확인한다.
6. completion_criteria를 모두 만족하도록 구현/문서/테스트를 갱신한다.
7. verification.commands를 실행한다.
8. UI 검증이 있으면 상태/시나리오별 UI-ID와 캡처 증적을 1:1로 연결한다.
9. UIREF/ui-baseline이 있으면 UI Implementation Contract와 기준 대비 차이 판정을 남긴다.
10. RUN_OUTPUT_CONTRACT 형식으로 결과를 보고한다.
11. 현재 Gate 산출물 완료 후 다음 Gate 진행 승인을 질문하고 대기한다.

금지:
- docs/ref-docs/를 읽거나 커밋하지 않는다.
- 관련 없는 리팩터링을 하지 않는다.
- 테스트를 실행하지 못했으면 통과로 보고하지 않는다.
- 추적표/결과서 갱신이 필요하면 누락하지 않는다.
- 사용자 명시 승인 없이 다음 Gate로 넘어가지 않는다.
- 기대 화면과 다른 캡처를 UI 증적으로 Pass 처리하지 않는다.
- UIREF/ui-baseline이 구현 기준인데 UI Implementation Contract 없이 구현 착수하지 않는다.
```

## 6. 최소 입력과 완전 입력

초기 대화에서는 사람이 최소 입력만 줄 수 있다.

```yaml
goal: "게시글 작성 기능 구현"
related_ids: [REQ-005]
```

이 경우 Adapter는 추적표와 문서를 읽어 완전 입력으로 확장해야 한다.

완전 입력을 만들 수 없으면 `Blocked` 상태로 질문한다.

## 7. 입력 검증 체크리스트

Run 시작 전 Adapter는 다음을 확인한다.

| 체크 | 기준 |
| --- | --- |
| 관련 ID 존재 | 추적표 또는 산출물에 관련 ID가 존재한다 |
| 먼저 읽을 문서 존재 | `source_documents.read_first` 파일이 존재한다 |
| 작업 대상 명확 | `source_documents.working_documents`가 이번 Run 산출물 중심으로 작성되어 있다 |
| 참고문서 분리 | Core/Template/Sample 문서가 `reference_on_demand`로 분리되어 있다 |
| 수정 범위 명확 | `scope.writable`이 비어 있지 않다 |
| 제외 경로 포함 | `docs/ref-docs/`가 제외되어 있다 |
| 완료 조건 명확 | 테스트 또는 증적 기준이 하나 이상 있다 |
| Gate 종료 정책 | 다음 Gate 진행 전 사용자 승인 대기 기준이 있다 |
| UI 증적 기준 | UI 테스트가 상태/시나리오별 증적과 연결된다 |
| 출력 형식 지정 | `RUN_OUTPUT_CONTRACT.md`를 참조한다 |
